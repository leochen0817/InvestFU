# 金融知识库
## 文件解析 - PDF
1. PDF通过pymupdf4llm读取转为markdown
```
def read_pdf_pymupdf4llm_to_md(file_path):
    import pymupdf4llm      # pip install pymupdf4llm==0.0.17
    return pymupdf4llm.to_markdown(file_path)
```

2. PDF的markdown数据切分：研报按标题切分、年报按固定格式（大主题）切分
```
def pdf_split(pdf_type, pdf_md):
    """
        :param pdf_type: 年报、研报
        :param pdf_md: md
        :return: list
    """
    text_list = []
    if pdf_type == '研报':
        # 正则表达式匹配 Markdown 标题找到所有的标题
        header_pattern = re.compile(r'^(#{1,6})\s+(.*)', re.MULTILINE)
    elif pdf_type == '年报':
        # 正则表达式匹配 Markdown 标题找到所有的二级标题
        header_pattern = re.compile(r'^(#{1,2})\s+(.*)', re.MULTILINE)
    else:
        return None

    headers = header_pattern.findall(pdf_md)

    # 如果没有标题，直接返回整个文本
    if not headers:
        return [pdf_md.strip()]

    # 将文本按标题切分
    last_end = 0
    for i, (header_level, header_text) in enumerate(headers):
        # 找到标题的位置
        header_start = pdf_md.find(f"{header_level} {header_text}", last_end)
        if header_start == -1:
            continue

        # 获取标题后的内容
        header_end = header_start + len(f"{header_level} {header_text}")
        next_header_level, next_header_text = headers[i+1] if i + 1 < len(headers) else headers[-1]
        next_header = pdf_md.find(f"{next_header_level} {next_header_text}", header_end) if i + 1 < len(headers) else -1
        if next_header == -1:
            content = pdf_md[header_end:].strip()
        else:
            content = pdf_md[header_end:next_header].strip()

        # 如果是年报，拼接一级标题
        if pdf_type == '年报':
            # 找到一级标题（#）
            first_level_header_pattern = re.compile(r'^# (.*)', re.MULTILINE)
            first_level_header = first_level_header_pattern.search(pdf_md[:header_start])
            if first_level_header:
                first_level_text = first_level_header.group(1)
                text_list.append(f"{first_level_text}\n{header_text}\n{content}")
            else:
                text_list.append(f"{header_text}\n{content}")
        else:
            # 如果是研报，直接添加标题和内容
            text_list.append(f"{header_text}\n{content}")

        # 更新 last_end
        last_end = header_end

    return text_list
```

## 向量数据库 Chroma
1. 构建向量库：data/chroma
2. 已有向量库：加载
```
# 初始化 Chroma 客户端（使用新的配置方式）
vectordb = chromadb.PersistentClient(path=vector_store_path)  # 指定数据库的存储路径

if is_chroma_data_exist(vector_store_path):
    # 目录中已有库，直接加载获取已有的集合（Collection）
    collection = vectordb.get_collection(name="embeddings_name")
else:
    # 目录中没有库，创建一个集合（Collection）
    collection = vectordb.create_collection(name="embeddings_name")
```
3. 词嵌入：
   1) 下载模型BAAI/bge-m3
   2) 读取文件解析后的文本列表
   3) 生成词嵌入embeddings
   4) 嵌入向量数据库

生成词嵌入embeddings：
```
from transformers import AutoTokenizer, AutoModel

# 加载 bge-m3 模型 和 分词器
model = AutoModel.from_pretrained('./model/BAAI/bge-m3')
tokenizer = AutoTokenizer.from_pretrained('./model/BAAI/bge-m3')

# 分词并转换为模型输入
inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
# 生成嵌入
with torch.no_grad():
    outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()  # 取平均池化
```
嵌入向量数据库：
```
# 添加嵌入和元数据到集合中
for i, (text, embedding) in enumerate(zip(data, embeddings)):
    # 确保 embedding 是一个列表
    if not isinstance(embedding, list):
        embedding = embedding.tolist()

    # 添加嵌入和元数据
    collection.add(
        embeddings=[embedding],  # 嵌入必须是列表格式
        metadatas=[{"text": text}],  # 元数据（如文本内容）
        ids=[id]  # 唯一 ID
    )
```

4. 向量库检索：input做词嵌入，通过collection.query对库进行top_k相似度文本检索并返回
5. 优化输出：通过结合输入问题和检索结果组成prompt喂入llm（internlm2.5-latest）优化文本后获得最终输出
``` 
query_embedding = embedding(model_path, input_text)
# 在 Chroma 中查询相似的嵌入
results = collection.query(
    query_embeddings=[query_embedding.tolist()],  # 查询嵌入
    n_results=top_k  # 返回最相似的 top_k 个结果
)

prompt = f"请根据{input_text}问题总结{content}内容并输出"

response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": prompt},
    ],
    stream=False
)
return response.choices[0].message.content
```
