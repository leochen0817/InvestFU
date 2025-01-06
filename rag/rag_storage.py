# 需先把ILICONFLOW_API_KEY设置到环境变量,先echo后source
# echo "export SILICONFLOW_API_KEY='你的硅基云API-KEY'" >> ~/.bashrc
# source ~/.bashrc
#
import os
import asyncio
import time
import numpy as np
from lightrag import LightRAG, QueryParam
from lightrag.llm import openai_complete_if_cache, siliconcloud_embedding
from lightrag.utils import EmbeddingFunc
import shutil
import textract # 多文件类型支持 -- The textract supports reading file types such as TXT, DOCX, PPTX, CSV, and PDF.


RPM_LIMIT = 2000
TPM_LIMIT = 500_000
REQUEST_INTERVAL = 600 / RPM_LIMIT
MAX_TOKENS_PER_REQUEST = min(TPM_LIMIT // RPM_LIMIT, 2048)


class RateLimiter:
    def __init__(self):
        self.last_request_time = 0
        self.token_count = 0
        self.last_reset_time = time.time()
        self.request_count = 0
        self.lock = asyncio.Lock()

    async def wait_if_needed(self, tokens):
        async with self.lock:
            now = time.time()

            if now - self.last_reset_time >= 60:
                self.token_count = 0
                self.request_count = 0
                self.last_reset_time = now

            if self.request_count >= RPM_LIMIT:
                wait_time = 60 - (now - self.last_reset_time)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                self.request_count = 0
                self.token_count = 0
                self.last_reset_time = time.time()

            if self.token_count + tokens > TPM_LIMIT:
                wait_time = 60 - (now - self.last_reset_time)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                self.token_count = 0
                self.request_count = 0
                self.last_reset_time = time.time()

            elapsed = now - self.last_request_time
            if elapsed < REQUEST_INTERVAL:
                await asyncio.sleep(REQUEST_INTERVAL - elapsed)

            self.last_request_time = time.time()
            self.token_count += tokens
            self.request_count += 1


rate_limiter = RateLimiter()


async def llm_model_func(
        prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    await asyncio.sleep(30)  # 增加延迟

    # 固定参数
    MIN_TOKENS = 100  # 最小响应token数
    MAX_TOKENS = 2048  # 最大响应token数

    try:
        # 计算输入token数量（使用更保守的估算）
        input_tokens = int(len(prompt.split()) * 1.3)

        # 等待速率限制
        await rate_limiter.wait_if_needed(input_tokens)

        # 计算可用的响应token数
        available_tokens = MAX_TOKENS_PER_REQUEST - input_tokens

        # 确保 max_tokens 在合理范围内
        response_tokens = max(MIN_TOKENS, min(available_tokens, MAX_TOKENS))

        # 如果 available_tokens 太小，减少输入长度
        if available_tokens < MIN_TOKENS:
            max_words = int((MAX_TOKENS_PER_REQUEST - MIN_TOKENS) / 1.3)
            prompt = " ".join(prompt.split()[:max_words])
            response_tokens = MIN_TOKENS

        # 设置 max_tokens
        kwargs['max_tokens'] = response_tokens

        # 打印调试信息
        print(f"Debug - input_tokens: {input_tokens}, response_tokens: {response_tokens}")

        return await openai_complete_if_cache(
            "Qwen/Qwen2.5-7B-Instruct",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=os.getenv("SILICONFLOW_API_KEY"),
            base_url="https://api.siliconflow.cn/v1/",
            **kwargs,
        )
    except Exception as e:
        print(f"Error in llm_model_func: {str(e)}")
        # 在出错时使用安全的默认值
        kwargs['max_tokens'] = MIN_TOKENS
        return await openai_complete_if_cache(
            "Qwen/Qwen2.5-7B-Instruct",
            prompt[:1000],  # 限制输入长度
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=os.getenv("SILICONFLOW_API_KEY"),
            base_url="https://api.siliconflow.cn/v1/",
            **kwargs,
        )


async def embedding_func(texts: list[str]) -> np.ndarray:
    # 固定参数
    BATCH_SIZE = 20

    # 计算总token数
    total_tokens = sum(len(text.split()) for text in texts)

    # 等待速率限制
    await rate_limiter.wait_if_needed(total_tokens)

    # 批处理并确保维度一致
    results = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        processed_batch = [t.strip()[:512] for t in batch if t.strip()]

        if processed_batch:
            try:
                embeddings = await siliconcloud_embedding(
                    processed_batch,
                    model="BAAI/bge-m3",
                    api_key=os.getenv("SILICONFLOW_API_KEY"),
                    base_url="https://api.siliconflow.cn/v1/embeddings",
                )

                # 确保每个嵌入向量都是二维的
                for emb in embeddings:
                    if len(emb.shape) == 1:
                        # 如果是一维向量，转换为二维
                        emb = np.expand_dims(emb, axis=0)
                    results.append(emb)

            except Exception as e:
                print(f"Error in batch {i}: {str(e)}")
                continue

    if not results:
        raise ValueError("No valid embeddings were generated")

    # 确保所有向量都是二维的，然后连接
    results = [np.atleast_2d(r) for r in results]
    return np.concatenate(results, axis=0)


# function test
async def test_funcs():
    result = await llm_model_func("How are you?")
    print("llm_model_func: ", result)

    result = await embedding_func(["How are you?"])
    print("embedding_func: ", result)


asyncio.run(test_funcs())


def rag_store(WORKING_DIR, file_path=None):
    # 删除工作目录以清除旧数据
    if os.path.exists(WORKING_DIR):
        shutil.rmtree(WORKING_DIR)
        print("删除工作目录清除旧数据...")
    os.mkdir(WORKING_DIR)

    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=1024, max_token_size=512, func=embedding_func
        ),
    )

    if file_path:
        if file_path.split('.')[-1] == 'txt':
            with open(file_path) as f:
                text = f.read()
        elif file_path.split('.')[-1] == 'pdf':
            text = textract.process(file_path).decode('utf-8')
        else:
            text = None

    rag.insert(text)
    return rag


def rag_query(question, mode='hybrid', rag=None, WORKING_DIR=None):
    try:
        if not rag:
            rag = LightRAG(
                working_dir=WORKING_DIR,
                llm_model_func=llm_model_func,
                embedding_func=EmbeddingFunc(
                    embedding_dim=1024, max_token_size=512, func=embedding_func
                ),
            )
        # mode: naive\local\global\hybrid
        result = rag.query(question, param=QueryParam(mode=mode))
        return result
    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':
    os.environ.setdefault("SILICONFLOW_API_KEY", "your-key")

    rag_dir = "../data/rag_kg"
    file_path = ''

    # rag = rag_store(rag_dir, file_path)
    # print('rag存储完成')

    question = "your-question"
    print("question: ", question)
    print(rag_query(question=question, mode='local', WORKING_DIR=rag_dir))
    print('rag查询完成')
