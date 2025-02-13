# pip3 install -U funasr
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
import os
from datetime import datetime
from tools.audio_handle import to_audio
from asr_gemini_pro import text_summary

"""
    功能一: 利用paraformer-zh 语音文字识别
    功能二: 利用fsmn_vad_zh 来语音结束点识别
    功能三: 利用ct-punc 对语音识别文本进行标点符合预测
    功能四: 利用cam++ 对语音中说话人身份识别
"""

# paraformer-zh is a multi-functional asr model
# use vad, punc, spk or not as you need
# hub：表示模型仓库，ms为选择modelscope下载，hf为选择huggingface下载。
def audio_to_text(input_file, output_file):
    model = AutoModel(
        model="paraformer-zh",        # paraformer-zh 、paraformer-en
        vad_model="fsmn-vad",   # 将长音频切割成短音频
        vad_kwargs={"max_single_segment_time": 30000},  # max_single_segment_time: 表示vad_model最大切割音频时长, 单位是毫秒ms
        punc_model="ct-punc",   # 标点恢复
        # spk_model="cam++"     # 说话人确认/分割，依赖时间戳，需要paraformer模型才有时间戳
        device="cuda:0",
    )

    res = model.generate(
        # input=f"{model.model_path}/example/asr_example.wav",
        input=input_file,
        use_itn=True,  # 是否包含标点与逆文本正则化
        # language="en",  # "auto", "zn", "en", "yue", "ja", "ko", "nospeech"
        batch_size_s=300,   # 动态batch，batch中总音频时长，单位为秒s
        hotword='魔搭'
    )

    audio_text = rich_transcription_postprocess(res[0]["text"])
    print("音频文本 = ", audio_text)

    # 文本写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(audio_text)
        f.close()
    print("语音识别文本已写入！")


if __name__=="__main__":
    # 记录程序开始时间
    start_time = datetime.now()
    print(f"程序开始时间: {start_time}")


    file_path = 'data/audio/12月24日InvestFU项目视频.wav'

    filename_with_extension = os.path.basename(file_path)  # 获取文件名带扩展名
    filename, file_extension = os.path.splitext(filename_with_extension)  # 分离文件名和扩展名
    output1 = 'results/funasr-pf/text/' + filename + '.txt'
    output2 = 'results/funasr-pf/summary/' + filename + '.txt'

    # 创建文件夹（如果不存在）
    os.makedirs(os.path.dirname(output1), exist_ok=True)
    os.makedirs(os.path.dirname(output2), exist_ok=True)


    # 音视频处理
    audio_path = to_audio(file_path)

    # 语音识别
    audio_to_text(audio_path, output1)

    # 会议纪要
    text_summary(output1, output2)


    # 记录程序结束时间
    end_time = datetime.now()
    print(f"程序结束时间: {end_time}")

    # 计算运行耗时
    run_time = end_time - start_time
    print(f"程序运行耗时: {run_time}")
