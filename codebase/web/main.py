import os
import json
import numpy as np

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# Constants
RULEBASE_PATH   = os.getenv('RULEBASE_PATH', '../discord/data/rulebase.json')
DISCORD_INVITE  = os.getenv('DISCORD_INVITE_URL', '')
SIMILARITY_THRESHOLD = 0.78
OUT_OF_SCOPE_PHRASE  = "i don't know based on the provided document"
OUT_OF_SCOPE_REPLY   = (
    "Xin lỗi, câu hỏi của bạn hiện chưa có thông tin trong tài liệu hướng dẫn. "
    "Vui lòng tham gia **Discord** để được Mentor hỗ trợ trực tiếp nhé!"
)

# Rule-base
_rulebase_cache: list = []
_rulebase_mtime: float = 0.0


def _cosine_sim(a, b) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))


def _load_rulebase() -> list:
    if os.path.exists(RULEBASE_PATH):
        with open(RULEBASE_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except (json.JSONDecodeError, ValueError):
                return []
    return []


def _build_rulebase_cache(emb_model):
    global _rulebase_cache, _rulebase_mtime
    items = _load_rulebase()
    if not items:
        _rulebase_cache = []
        return
    questions = [i['question'] for i in items]
    vecs = emb_model.embed_documents(questions)
    _rulebase_cache = list(zip(vecs, items))
    try:
        _rulebase_mtime = os.path.getmtime(RULEBASE_PATH)
    except OSError:
        pass


def _maybe_reload_rulebase(emb_model):
    """Tự động reload cache nếu rulebase.json được Discord cập nhật."""
    global _rulebase_mtime
    try:
        mtime = os.path.getmtime(RULEBASE_PATH)
        if mtime != _rulebase_mtime:
            _build_rulebase_cache(emb_model)
    except OSError:
        pass


def _search_rulebase(emb_model, question: str):
    _maybe_reload_rulebase(emb_model)
    if not _rulebase_cache:
        return None
    q_vec = emb_model.embed_query(question)
    best_score, best_item = -1.0, None
    for vec, item in _rulebase_cache:
        score = _cosine_sim(q_vec, vec)
        if score > best_score:
            best_score, best_item = score, item
    if best_score >= SIMILARITY_THRESHOLD and best_item:
        return best_item['answer']
    return None


# RAG Pipeline
_MARKDOWN_SEPARATORS = [
    "\n#{1,6} ", "```\n", "\n\\*\\*\\*+\n", "\n---+\n", "\n___+\n", "\n\n", "\n", " ", ""
]

_SYSTEM_PROMPT = """\
## Persona
- **Role:** Trợ lý hỏi đáp nội bộ cho chương trình đào tạo AI thực chiến tại VinUni.
- **Expertise:** Chuyên gia tra cứu tài liệu handbook, quy định chương trình, lịch học, và quy trình nộp bài.
- **Communication style:** Ngắn gọn, chính xác, thân thiện. Ưu tiên tiếng Việt. Không dùng ngôn ngữ mơ hồ.

## Rules
- LUÔN trả lời dựa trên nội dung được cung cấp trong `{context}`.
- LUÔN trích dẫn nguồn theo định dạng `*(Nguồn: <tên file/trang>)*` nếu metadata có sẵn.
- LUÔN trả lời theo **Output Format** quy định bên dưới.
- NÊN ưu tiên bullet list cho các câu trả lời có nhiều ý.
- NÊN dùng **in đậm** để nhấn mạnh thông tin quan trọng (ngày, số liệu, tên mục).

## Capabilities
- Tra cứu thông tin từ Handbook PDF đã được index vào vectorstore (RAG).
- Tra cứu câu trả lời đã được Mentor xác nhận trong Rule-base.
- Trả lời các câu hỏi liên quan đến: lịch học, quy định, quy trình nộp bài, đổi nhóm/chủ đề, điều kiện hoàn thành chương trình.

## Constraints
- KHÔNG tự suy đoán hoặc bịa đặt thông tin ngoài tài liệu được cung cấp.
- KHÔNG sử dụng kiến thức bên ngoài (web, GPT training data).
- Khi thông tin KHÔNG có trong context, phản hồi ĐÚNG cụm từ sau (không thêm gì):
  `I don't know based on the provided document.`
- KHÔNG trả lời các câu hỏi ngoài phạm vi chương trình (chính trị, y tế, pháp lý, v.v.).

## Output Format
Trả lời theo cấu trúc markdown sau:

**[Câu trả lời ngắn gọn — 1-2 câu tóm tắt]**

- Chi tiết điểm 1
- Chi tiết điểm 2
- ...

*(Nguồn: <tên file hoặc trang nếu có>)*
"""

_TEMPLATE = _SYSTEM_PROMPT + "\n---\nContext:\n{context}\n\nQuestion: {question}"

print("Đang nạp tài liệu và xây dựng Vector Database...")
_loader = DirectoryLoader(
    path='./data',
    glob='**/*.pdf',
    loader_cls=UnstructuredFileLoader,
    show_progress=True,
    use_multithreading=False,
)
_docs = _loader.load()

_splits = RecursiveCharacterTextSplitter(
    chunk_size=1200, chunk_overlap=200,
    add_start_index=True, strip_whitespace=True,
    separators=_MARKDOWN_SEPARATORS,
).split_documents(_docs)

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

_vectorstore = FAISS.from_documents(
    documents=_splits,
    embedding=embeddings,
    distance_strategy=DistanceStrategy.COSINE,
)

_retriever = _vectorstore.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 5, "score_threshold": 0.2},
)

_rag_chain = (
    {"context": _retriever, "question": RunnablePassthrough()}
    | ChatPromptTemplate.from_template(_TEMPLATE)
    | ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    | StrOutputParser()
)

_build_rulebase_cache(embeddings)
print("Pipeline sẵn sàng!")

# Flask App
app = Flask(__name__, static_folder='.', static_url_path='')


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/config')
def config():
    return jsonify({'discord_invite': DISCORD_INVITE})


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'answer': 'Vui lòng nhập câu hỏi.', 'source': 'error'})

    # Bước 1: Rule-base
    rulebase_answer = _search_rulebase(embeddings, question)
    if rulebase_answer:
        return jsonify({'answer': rulebase_answer, 'source': 'rulebase'})

    # Bước 2: RAG Handbook
    try:
        answer = _rag_chain.invoke(question)
        if OUT_OF_SCOPE_PHRASE in answer.lower():
            return jsonify({'answer': OUT_OF_SCOPE_REPLY, 'source': 'out_of_scope'})
        return jsonify({'answer': answer, 'source': 'rag'})
    except Exception as e:
        err_str = str(e)
        if 'RESOURCE_EXHAUSTED' in err_str or '429' in err_str:
            msg = 'Hệ thống đang quá tải, vui lòng thử lại sau ít phút hoặc đặt câu hỏi trên Discord để được Mentor hỗ trợ.'
        else:
            msg = 'Đã xảy ra lỗi khi tra cứu, vui lòng thử lại sau.'
        return jsonify({'answer': msg, 'source': 'error'})


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
