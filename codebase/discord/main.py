import os
import discord
from dotenv import load_dotenv

from agent.pipeline import build_pipeline
from agent.bot import create_client
from tools.rulebase import build_rulebase_cache

load_dotenv()

# 1. Khởi tạo RAG pipeline (nạp PDF + tạo vectorstore)
embeddings, rag_chain = build_pipeline(data_path='./data')

# 2. Nạp Rule-base cache vào bộ nhớ
build_rulebase_cache(embeddings)

# 3. Khởi động Discord bot
Client = create_client(embeddings, rag_chain)

intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run(os.getenv("DISCORD_BOT_TOKEN"))

