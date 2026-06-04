import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from langchain_community.document_loaders import DirectoryLoader, UnstructuredFileLoader
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

_MARKDOWN_SEPARATORS = [
    "\n#{1,6} ", "```\n", "\n\\*\\*\\*+\n", "\n---+\n", "\n___+\n", "\n\n", "\n", " ", ""
]

_TEMPLATE = (
    "You are a strict, citation-focused assistant for a private knowledgebase.\n"
    "Rules:\n"
    "1. Use ONLY the provided context to answer the question.\n"
    "2. If the answer is not clearly contained in the context, respond ONLY with the exact phrase: "
    "I don't know based on the provided document.\n"
    "3. Do NOT use outside knowledge, guessing, or web information.\n"
    "4. If applicable, cite sources as (source: page) using the metadata.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}"
)


def build_pipeline(data_path: str = './data'):
    """Nạp tài liệu PDF, tạo vectorstore FAISS và RAG chain.

    Returns:
        embeddings: GoogleGenerativeAIEmbeddings — dùng để tìm kiếm rulebase.
        rag_chain:  LangChain chain — dùng để trả lời câu hỏi từ handbook.
    """
    print("Đang nạp tài liệu và xây dựng Vector Database...")
    loader = DirectoryLoader(
        path=data_path,
        glob='**/*.pdf',
        loader_cls=UnstructuredFileLoader,
        show_progress=True,
        use_multithreading=False,  # tránh lỗi OMP trên macOS
    )
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        add_start_index=True,
        strip_whitespace=True,
        separators=_MARKDOWN_SEPARATORS,
    )
    splits = text_splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

    vectorstore = FAISS.from_documents(
        documents=splits,
        embedding=embeddings,
        distance_strategy=DistanceStrategy.COSINE,
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": 5, "score_threshold": 0.2},
    )

    prompt = ChatPromptTemplate.from_template(_TEMPLATE)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("Khởi tạo RAG Pipeline thành công!")
    return embeddings, rag_chain
