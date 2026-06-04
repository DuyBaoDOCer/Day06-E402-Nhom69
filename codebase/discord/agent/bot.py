import asyncio
import discord
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from tools.rulebase import (
    search_rulebase,
    save_to_rulebase,
    log_new_issue,
    build_rulebase_cache,
)

_PARAPHRASE_PROMPT = ChatPromptTemplate.from_template(
    "Generate 5 Vietnamese paraphrases of the following question. "
    "Return ONLY the paraphrases, one per line, no numbering, no explanation.\n\n"
    "Question: {question}"
)


async def _generate_paraphrases(question: str) -> list[str]:
    """Dùng LLM sinh 5 cách hỏi khác nhau để mở rộng Rule-base (lazy init)."""
    try:
        chain = (
            _PARAPHRASE_PROMPT
            | ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
            | StrOutputParser()
        )
        raw = await chain.ainvoke({"question": question})
        paraphrases = [line.strip() for line in raw.strip().splitlines() if line.strip()]
        return paraphrases[:5]
    except Exception:
        return []

OUT_OF_SCOPE_PHRASE = "i don't know based on the provided document"
OUT_OF_SCOPE_REPLY = (
    "Xin lỗi, câu hỏi của bạn hiện chưa có thông tin trong tài liệu hướng dẫn. "
    "Vui lòng liên hệ Mentor để được hỗ trợ.\n\n"
    "*(Mentor: hãy **Reply** vào tin nhắn này hoặc tin nhắn của học viên để lưu câu trả lời vào hệ thống)*"
)

# Map: message_id → original_question
# Lưu cả id tin nhắn của bot lẫn id tin nhắn học viên để Mentor reply vào đâu cũng được
pending_questions: dict[int, str] = {}


def _is_mentor(member: discord.Member) -> bool:
    return any(role.name.lower() == 'mentor' for role in member.roles)


def _cleanup_pending(question: str):
    """Xóa tất cả các key trỏ đến cùng một câu hỏi khỏi pending_questions."""
    to_remove = [mid for mid, q in pending_questions.items() if q == question]
    for mid in to_remove:
        del pending_questions[mid]


def create_client(embeddings, rag_chain) -> type:
    """Tạo Discord Client class với embeddings và rag_chain được inject vào."""

    class Client(discord.Client):
        async def on_ready(self):
            print(f'Đã đăng nhập Discord với tên: {self.user}')

        async def _handle_question(self, message: discord.Message, question: str):
            # Bước 1: Kiểm tra Rule-base
            rulebase_answer = await asyncio.to_thread(search_rulebase, embeddings, question)
            if rulebase_answer:
                await message.channel.send(f"**[Rule-base]**\n{rulebase_answer}")
                return

            # Bước 2: RAG (Handbook)
            loading_msg = await message.channel.send("Đang tra cứu tài liệu, bạn đợi chút nhé...")
            try:
                answer = await rag_chain.ainvoke(question)
                if OUT_OF_SCOPE_PHRASE in answer.lower():
                    # Bước 3: Ngoài phạm vi — ghi log và chờ Mentor reply
                    await asyncio.to_thread(log_new_issue, question)
                    await loading_msg.edit(content=OUT_OF_SCOPE_REPLY)
                    pending_questions[loading_msg.id] = question
                    pending_questions[message.id] = question
                else:
                    await loading_msg.edit(content=answer)
            except Exception as e:
                await loading_msg.edit(content=f"Quá trình tra cứu gặp lỗi: {e}")

        async def on_message(self, message: discord.Message):
            if message.author == self.user:
                return

            print(f'Message from {message.author}: {message.content}')

            # Mentor reply vào tin nhắn "ngoài phạm vi" → tự động lưu rulebase
            if message.reference and message.reference.message_id in pending_questions:
                if _is_mentor(message.author):
                    question = pending_questions[message.reference.message_id]
                    answer = message.content.strip()
                    if answer:
                        _cleanup_pending(question)
                        # Sinh paraphrase để mở rộng coverage của rule-base
                        paraphrases = await _generate_paraphrases(question)
                        all_questions = [question] + paraphrases
                        await asyncio.to_thread(save_to_rulebase, all_questions, answer)
                        await asyncio.to_thread(build_rulebase_cache, embeddings)
                        para_preview = "\n".join(f"  - {p}" for p in paraphrases)
                        await message.reply(
                            f"Đã lưu vào Rule-base! ({len(all_questions)} biến thể câu hỏi)\n"
                            f"**Q gốc:** {question}\n"
                            f"**Paraphrases:**\n{para_preview}\n"
                            f"**A:** {answer}",
                            mention_author=False,
                        )
                    return

            # Xử lý khi bot bị mention
            bot_mention = f'<@{self.user.id}>'
            if message.content.startswith(bot_mention):
                question = message.content.replace(bot_mention, '').strip()
                if not question:
                    await message.channel.send(
                        "Bạn chưa nhập câu hỏi! Hãy tag bot kèm câu hỏi hoặc dùng `/ask <câu hỏi>`"
                    )
                    return
                await self._handle_question(message, question)
                return

            # Lệnh /ask
            if message.content.startswith('/ask'):
                question = message.content[len('/ask'):].strip()
                if not question:
                    await message.channel.send(
                        "Bạn chưa nhập câu hỏi! Hãy dùng cú pháp: `/ask <câu hỏi của bạn>`"
                    )
                    return
                await self._handle_question(message, question)
                return

            # Lệnh /hello
            if message.content.startswith('/hello'):
                await message.channel.send('Hello!')

    return Client
