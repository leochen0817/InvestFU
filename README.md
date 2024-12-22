# InvestFU

<!-- TOC -->

## 🗂️ 目录
- [前言](#%E5%89%8D%E8%A8%80)
- [技术架构](#%E6%8A%80%E6%9C%AF%E6%9E%B6%E6%9E%84)
- [使用指南](#%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)
    - [文件结构](#%E6%96%87%E4%BB%B6%E7%BB%93%E6%9E%84)
    - [环境准备](#%E7%8E%AF%E5%A2%83%E5%87%86%E5%A4%87)
    - [数据集制作](#%E6%95%B0%E6%8D%AE%E9%9B%86%E5%88%B6%E4%BD%9C)
    - [模型训练](#%E6%A8%A1%E5%9E%8B%E8%AE%AD%E7%BB%83)
    - [RAG检索增强生成](#rag%E6%A3%80%E7%B4%A2%E5%A2%9E%E5%BC%BA%E7%94%9F%E6%88%90)
- [开发计划](#%E5%BC%80%E5%8F%91%E8%AE%A1%E5%88%92)
    - [初版功能](#%E5%88%9D%E7%89%88%E5%8A%9F%E8%83%BD)
    - [后续多模态版本](#%E5%90%8E%E7%BB%AD%E5%A4%9A%E6%A8%A1%E6%80%81%E7%89%88%E6%9C%AC)
- [致谢](#%E8%87%B4%E8%B0%A2)
- [免责声明](#%E5%85%8D%E8%B4%A3%E5%A3%B0%E6%98%8E)

<!-- /TOC -->




## 前言

在当今瞬息万变的金融市场中，投资决策的复杂性与日俱增。随着信息量的激增和市场环境的不断变化，传统的投资研究方式已难以满足高效、准确的决策需求。因此，构建一个智能投资研究系统已成为金融机构提升竞争力的重要举措。

### 投资研究智能系统的帮助

投资研究智能系统通过整合大数据和人工智能技术，可以为投研经理提供以下支持：

1. **信息整合与分析**：系统能够快速汇聚来自不同渠道的信息，包括财务报表、宏观经济数据、行业动态和舆情分析，帮助研究人员全面了解市场状况。

2. **实时风险监控**：借助先进的算法，智能系统可以实时监测市场变化和持仓资产的风险，及时发出预警，助力投资经理做出迅速反应。

3. **智能决策支持**：通过数据挖掘和模式识别，系统可以提供基于历史数据的投资建议，帮助投研团队识别潜在的投资机会与风险。

4. **提高工作效率**：自动化的数据处理和报告生成减少了人工工作量，使研究人员能将更多时间投入到深度分析和战略思考中。


## 技术架构

![img.png](assets/img.png)

构建**金融领域模型**,使用Internlm2-chat-7b 💥通过xtuner进行SFT微调，部署集成了LMDeploy加速推理 🚀，支持 RAG 检索增强生成 💾，为金融领域大模型提供丰富的知识库组。

### 构建金融领域模型数据集和微调(Fine-tune)

使用的数据集在datasets文件夹下，感谢HuggingFace提供的金融术语数据集。
使用Xtuner微调工具+qlora的方法构建新的**金融领域模型**，也支持直接通过LMDeploy接入现有的llm进行对话。

### RAG技术

目前支持Doc、Docx、Excel、csv、PDF、MD文件。

针对PDF文件，本项目通过使用PymuPDF4llm将pdf文件转换成markdown结构化格式。

针对Doc\Docx文件，本项目通过使用Py2Doc将文档转成转换成json格式。

最终输出的结构化数据，通过bce-embedding-base_v1和bce-reranker-base_v1模型Embedding到向量数据库。

## 使用指南

### 文件结构

```bash
InvestFU/
│
├── assets                   # 素材
├── configs                  # 配置
├── data                     # 内外部数据
├── datasets                 # 预训练数据集
├── deploy                   # 发布
├── docs                     # doc文档
├── evaluation               # 验证集
├── rag                      # RAG
├── scripts                  # 处理数据脚本
├── src                      # 项目代码
├── tools                    # 工具类
├── xtuner_config            # xtuner配置
├── README.md                # README.md
└── requirements.txt         # 使用pip安装的依赖
```

### 环境准备

```shell
# 创建虚拟环境
conda create -n invest python=3.10 -y

# 激活虚拟环境（注意：后续的所有操作都需要在这个虚拟环境中进行）
conda activate invest

# 安装一些必要的库
conda install pytorch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 pytorch-cuda=12.1 -c pytorch -c nvidia -y
# 安装其他依赖
pip install -r requirements.txt
```


### 数据集制作

- 从上交所获取股票年报：python handle_ssc.py
- 从HuggingFace数据集中获取中国平安相关信息：python handle_jsonl.py
- 从东方财富获取舆情新闻：python handle_eastmoney.py
- 从巨潮资讯获取事件信息：python handle_cninfo.py
- 从沧海数据通过api获取行情数据等：python handle_canghai_api.py

### 模型训练

命令行直接如下操作：

**QLoRA+deepspeed训练**

```
#增量预训练
xtuner train ./xtuner_config/pretrain/internlm2_5-1_8b-chat_pretrain.py  --work-dir ./pretrain --deepspeed deepspeed_zero1

#指令微调
xtuner train ./xtuner_config/finetune/internlm2_5_chat_1_8b_qlora_wulewule_all_test.py  --work-dir ./finetune --deepspeed deepspeed_zero1
```

### RAG(检索增强生成)

默认`data`目录为txt数据源目录，开启RAG后，会使用bce-embedding-base_v1自动将`data`目录下的txt数据转为换chroma向量库数据，存放在`rag/chroma `目录下（如果该目录下已有数据库文件，则跳过数据库创建），然后使用bce-reranker-base_v1对检索到的信息重排序后，将问题和上下文一起给模型得到最终输出。`rag/simple_rag.py`里是一个简单的demo，参数配置见`configs/rag_cfg.yaml`。

RAG代码讲解见[rag配置](rag/readme.md)。

 
## 开发计划

### 初版功能

- [x] 游戏角色、背景故事、原著联系等知识问答助手

- [x] 使用RAG支持游戏攻略、菜单、网络梗等新鲜知识的更新

- [x] 基于OpenXLab使用LMDepoly实现初版demo部署

- [ ] 增加history记忆，增加标准测试集，opencompass评估模型性能

### 后续多模态版本

- [ ] 加入语音多模态，如ASR（用户语音输入）、TTS（猴哥语音回答问题）

- [ ] 加入图像生成，接入别人的[SD+LoRA模型]( https://www.qpipi.com/73996/ )，判断用户意图生成对应prompt的天命人

- [ ] 加入音乐多模态，接类似[SUNO-AI](https://suno-ai.org/)，生成古典风格游戏配乐


## 致谢

非常感谢以下这些开源项目给予我们的帮助：

- [InternLM](https://github.com/InternLM/InternLM)
- [Xtuner](https://github.com/InternLM/xtuner)
- [Imdeploy](https://github.com/InternLM/lmdeploy)
- [InternlM-Tutorial](https://github.com/InternLM/Tutorial)
- [HuixiangDou](https://github.com/InternLM/HuixiangDou)
- [Streamer-Sales](https://github.com/PeterH0323/Streamer-Sales)

最后感谢上海人工智能实验室推出的书生·浦语大模型实战营，为我们的项目提供宝贵的技术指导和强大的算力支持！

## 免责声明

**本项目相关资源仅供学术研究之用，严禁用于商业用途。** 使用涉及第三方代码的部分时，请严格遵循相应的开源协议。模型生成的内容受模型计算、随机性和量化精度损失等因素影响，本项目不对其准确性作出保证。对于模型输出的任何内容，本项目不承担任何法律责任，亦不对因使用相关资源和输出结果而可能产生的任何损失承担责任。本项目由个人及协作者业余时间发起并维护，因此无法保证能及时回复解决相应问题。
