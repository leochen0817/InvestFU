import asyncio
import os
import inspect
import logging
from lightrag import LightRAG, QueryParam
from lightrag.llm import ollama_model_complete, ollama_embedding
from lightrag.utils import EmbeddingFunc
import shutil
import textract

# WORKING_DIR = "../data/wzzj_rag"
WORKING_DIR = "../data/yb_rag"

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)

# 删除工作目录以清除旧数据
# if os.path.exists(WORKING_DIR):
#     shutil.rmtree(WORKING_DIR)
#     print("删除工作目录清除旧数据...")
# os.mkdir(WORKING_DIR)


def split_text_by_max_token(text, max_token):
    """
    按 max_token 切分大文本
    :param text: 输入的文本
    :param max_token: 每个文本块的最大 token 数
    :return: 切分后的文本列表
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_token_count = 0

    for word in words:
        current_chunk.append(word)
        current_token_count += 1

        if current_token_count >= max_token:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_token_count = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


rag = LightRAG(
    working_dir=WORKING_DIR,
    llm_model_func=ollama_model_complete,
    llm_model_name="qwen2.5:7b",
    llm_model_max_token_size=32768,
    llm_model_kwargs={"host": "http://localhost:11434", "options": {"num_ctx": 32768}},

    embedding_func=EmbeddingFunc(
        embedding_dim=1024,
        max_token_size=8192,
        func=lambda texts: ollama_embedding(
            texts, embed_model="bge-m3", host="http://localhost:11434"
        ),
    ),
)


file_path = 'XXX.pdf'
text_content = textract.process(file_path).decode('utf-8')
chunks = split_text_by_max_token(text_content, max_token=32768)
for chunk in chunks:
    rag.insert(chunk)


# question = "平安的发展历史？"
# question = "平安的2023年报总体情况？"
question = "your-question"


# Perform naive search
print(
    rag.query(question, param=QueryParam(mode="naive"))
)

# Perform local search
print(
    rag.query(question, param=QueryParam(mode="local"))
)

# Perform global search
print(
    rag.query(question, param=QueryParam(mode="global"))
)

# Perform hybrid search
print(
    rag.query(question, param=QueryParam(mode="hybrid"))
)

# stream response
resp = rag.query(
    question,
    param=QueryParam(mode="hybrid", stream=True),
)


async def print_stream(stream):
    async for chunk in stream:
        print(chunk, end="", flush=True)


if inspect.isasyncgen(resp):
    asyncio.run(print_stream(resp))
else:
    print(resp)
