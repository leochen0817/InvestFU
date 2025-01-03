# pip install chromadb==0.5.23
# pip install transformers==4.46.0
# pip install tokenizers==0.20.3
import chromadb
from transformers import AutoTokenizer, AutoModel
import torch
from tools.download_model import download_embedding_model
import os
import warnings
warnings.filterwarnings("ignore")
from openai import OpenAI


def embedding(model_path, text):
    if text is None:
        raise ValueError("输入文本不能为空")

    # 加载 bge-m3 模型 和 分词器
    model = AutoModel.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    # tokens = tokenizer.tokenize(text)
    # print(tokens)

    # 分词并转换为模型输入
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    # 生成嵌入
    with torch.no_grad():
        outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()  # 取平均池化
    print(embeddings)
    return embeddings


def embedding_search(model_path, text1, text2):
    embedding1 = embedding(model_path, text1)
    embedding2 = embedding(model_path, text2)
    # 计算余弦相似度
    from sklearn.metrics.pairwise import cosine_similarity
    similarity = cosine_similarity(embedding1.reshape(1, -1), embedding2.reshape(1, -1))
    return similarity[0][0]


def is_chroma_data_exist(directory):
    # 检查目录下是否有 Chroma 数据文件，假设 Chroma 会创建这些文件
    return os.path.exists(os.path.join(directory, "chroma.sqlite3"))


def get_chroma_db(vector_store_path, embeddings, data=None):
    """
        获取 Chroma 数据库（如果存在则加载，否则构建）
        :param data: 文本数据列表
        :param vector_store_path: 数据库持久化路径
        :param embeddings: 嵌入向量列表
        :return: Chroma 客户端和集合
    """
    try:
        # 持久化路径
        if not os.path.exists(vector_store_path):
            os.makedirs(vector_store_path)

        # 初始化 Chroma 客户端（使用新的配置方式）
        vectordb = chromadb.PersistentClient(path=vector_store_path)  # 指定数据库的存储路径

        if is_chroma_data_exist(vector_store_path):
            # 目录中已有库，直接加载获取已有的集合（Collection）
            collection = vectordb.get_collection(name="my_text_embeddings")
            print("向量数据库加载完成")
        else:
            # 目录中没有库，创建一个集合（Collection）
            collection = vectordb.create_collection(name="my_text_embeddings")
            print("向量数据库已构建并持久化完成")

        # 获取当前集合中的最大 id
        existing_ids = collection.get(include=[])["ids"]  # 获取所有现有的 ids
        if existing_ids:
            max_id = max(int(id.split("_")[1]) for id in existing_ids)  # 找到最大的 id
        else:
            max_id = -1  # 如果没有现有数据，从 0 开始
        print("max_id = ", max_id)

        if data and embeddings:
            # 添加嵌入和元数据到集合中
            for i, (text, embedding) in enumerate(zip(data, embeddings)):
                # 确保 embedding 是一个列表
                if not isinstance(embedding, list):
                    embedding = embedding.tolist()

                # 生成自增的 id
                new_id = f"id_{max_id + i + 1}"

                # 添加嵌入和元数据
                collection.add(
                    embeddings=[embedding],  # 嵌入必须是列表格式
                    metadatas=[{"text": text}],  # 元数据（如文本内容）
                    ids=[new_id]  # 唯一 ID
                )
            print("嵌入已成功存储到 Chroma 数据库！")
        return vectordb, collection
    except Exception as e:
        print(f"构建/加载向量数据库时出错: {e}")
        return None


def db_search(collection, model_path, input_text, top_k):
    query_embedding = embedding(model_path, input_text)
    # 在 Chroma 中查询相似的嵌入
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],  # 查询嵌入
        n_results=top_k  # 返回最相似的 top_k 个结果
    )
    print("查询结果：", results)
    return results


def llm_gen(prompt, client, model):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    return response.choices[0].message.content

if __name__=="__main__":
    model_path = 'D:/AI/local_models/BAAI/bge-m3'
    model_name = 'BAAI/bge-m3'

    # 下载模型
    download_embedding_model(model_name=model_name, model_path=model_path)

    # from data_reader import read_data
    # from get_datasets import *
    #
    # pdf_text, _ = read_data('../data/annual_report')
    # print('data = \n', pdf_text)
    # text_list = pdf_split("年报", pdf_text)
    # print('text_list = \n', text_list)

    # text_list = ['测试文本111', '这是测试文本222']

    # 定义 Embeddings
    embeddings = []
    # for text in text_list:
    #     embeddings.append(embedding(model_name, text))

    # 向量数据库持久化路径
    vector_store_path = '../data/chroma'
    # db, collection = get_chroma_db(vector_store_path, embeddings, text_list)
    db, collection = get_chroma_db(vector_store_path, embeddings)
    print(db, collection)

    # input_text = "中国平安主营业务"
    input_text = input("请输入知识库检索问题：")
    top_k = 2
    top_results = db_search(collection, model_path, input_text, top_k)


    # 调用llm总结返回文本，优化输出
    content = top_results['metadatas']
    prompt = f"请根据{input_text}问题总结{content}内容并输出"
    api_key = ""    # your-key
    client = OpenAI(base_url="https://internlm-chat.intern-ai.org.cn/puyu/api/v1/", api_key=api_key)
    model = "internlm2.5-latest"
    output = llm_gen(prompt, client, model)
    print("output = ", output)

