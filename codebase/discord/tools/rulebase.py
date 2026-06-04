import os
import json
import numpy as np

RULEBASE_PATH = './data/rulebase.json'
NEW_ISSUE_PATH = './data/new_issue.json'
SIMILARITY_THRESHOLD = 0.85

# Cache: list of (embedding_vector, rulebase_item)
rulebase_cache: list = []


def load_rulebase() -> list:
    """Đọc toàn bộ Rule-base từ file JSON."""
    if os.path.exists(RULEBASE_PATH):
        with open(RULEBASE_PATH, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except (json.JSONDecodeError, ValueError):
                return []
    return []


def save_to_rulebase(question: str, answer: str):
    """Lưu cặp câu hỏi - câu trả lời vào Rule-base."""
    rulebase = load_rulebase()
    rulebase.append({"question": question, "answer": answer, "source": "mentor_input"})
    with open(RULEBASE_PATH, 'w', encoding='utf-8') as f:
        json.dump(rulebase, f, ensure_ascii=False, indent=2)


def log_new_issue(question: str):
    """Ghi lại câu hỏi chưa có câu trả lời vào new_issue.json để Mentor xem xét."""
    issues = []
    if os.path.exists(NEW_ISSUE_PATH):
        with open(NEW_ISSUE_PATH, 'r', encoding='utf-8') as f:
            try:
                issues = json.load(f)
            except (json.JSONDecodeError, ValueError):
                issues = []
    if not any(i.get('question') == question for i in issues):
        issues.append({"question": question, "status": "pending"})
        with open(NEW_ISSUE_PATH, 'w', encoding='utf-8') as f:
            json.dump(issues, f, ensure_ascii=False, indent=2)


def _cosine_sim(a, b) -> float:
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))


def build_rulebase_cache(emb_model):
    """Xây dựng lại cache embedding cho toàn bộ Rule-base. Gọi lại sau mỗi lần lưu mới."""
    global rulebase_cache
    items = load_rulebase()
    if not items:
        rulebase_cache = []
        return
    questions = [i['question'] for i in items]
    vecs = emb_model.embed_documents(questions)
    rulebase_cache = list(zip(vecs, items))


def search_rulebase(emb_model, question: str):
    """Tìm câu trả lời trong Rule-base theo độ tương đồng ngữ nghĩa (cosine similarity).
    
    Input: embedding model và chuỗi câu hỏi.
    Output: câu trả lời nếu tìm thấy (similarity >= 0.85), ngược lại trả về None.
    """
    if not rulebase_cache:
        return None
    q_vec = emb_model.embed_query(question)
    best_score, best_item = -1.0, None
    for vec, item in rulebase_cache:
        score = _cosine_sim(q_vec, vec)
        if score > best_score:
            best_score, best_item = score, item
    if best_score >= SIMILARITY_THRESHOLD and best_item:
        return best_item['answer']
    return None


# Đăng ký tools cho Agent
TOOLS = [
    {
        "name": "search_rulebase",
        "description": (
            "Tìm câu trả lời trong Rule-base theo độ tương đồng ngữ nghĩa. "
            "Input: embedding model và chuỗi câu hỏi. "
            "Output: câu trả lời nếu similarity >= 0.85, ngược lại None."
        ),
        "function": search_rulebase,
    },
    {
        "name": "save_to_rulebase",
        "description": (
            "Lưu cặp câu hỏi - câu trả lời vào Rule-base (rulebase.json). "
            "Input: question (str), answer (str). Output: None."
        ),
        "function": save_to_rulebase,
    },
    {
        "name": "log_new_issue",
        "description": (
            "Ghi câu hỏi chưa có câu trả lời vào new_issue.json để Mentor xem xét. "
            "Input: question (str). Output: None."
        ),
        "function": log_new_issue,
    },
    {
        "name": "build_rulebase_cache",
        "description": (
            "Xây dựng lại cache embedding cho Rule-base sau mỗi lần thêm dữ liệu mới. "
            "Input: embedding model. Output: None."
        ),
        "function": build_rulebase_cache,
    },
]
