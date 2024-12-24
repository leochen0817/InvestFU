import os

# 下载 源词向量模型 - BAAI/bge-m3
def download_embedding_model(model_name, model_path):
    if not os.path.exists(model_path):
        # 设置环境变量
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

        # os.system(
        #     'huggingface-cli download --resume-download sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --local-dir ' + model_path)
        # print('sentence-transformer模型下载完成')
        os.system(
            f'huggingface-cli download --resume-download {model_name} --local-dir {model_path}')
        print('BAAI/bge-m3模型下载完成')
    else:
        print('BAAI/bge-m3模型已存在，无需下载')

if __name__ == '__main__':
    # 下载所需模型
    download_embedding_model(model_name='BAAI/bge-m3', model_path='D:/AI/local_models/BAAI/bge-m3')
