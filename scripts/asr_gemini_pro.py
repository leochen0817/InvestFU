# pip install -q -U google-genai
from google import genai
import time
import os
from datetime import datetime
from google.genai import types
from tools.audio_handle import to_audio

client = genai.Client(api_key="your_key")
# export GEMINI_API_KEY=your_key_here


def audio_to_text(input, output):
    # 上传音频文件
    audio_file = client.files.upload(file=input)

    # 验证文件上传是否成功
    while audio_file.state.name == "PROCESSING":
        print('.', end='')
        time.sleep(1)
        audio_file = client.files.get(name=audio_file.name)

    if audio_file.state.name == "FAILED":
        raise ValueError(audio_file.state.name)

    print('上传音频文件Done')

    # 生成内容
    response = client.models.generate_content(
        model='gemini-2.0-pro-exp-02-05',
        contents=[
          audio_file,
          'Convert this audio to text',
        ],

        # config = types.GenerateContentConfig(
        #     max_output_tokens=500000000,
        # )
    )
    audio_text = response.text
    print("音频文本 = ", audio_text)


    # 文本写入文件
    with open(output, 'w', encoding='utf-8') as f:
        f.write(audio_text)
        f.close()
    print("语音识别文本已写入！")


# 长视频分段处理
def audio_to_text_segments(segments, output):
    full_text = ""
    for segment in segments:
        # 上传音频文件
        audio_file = client.files.upload(file=segment)

        # 验证文件上传是否成功
        while audio_file.state.name == "PROCESSING":
            print('.', end='')
            time.sleep(1)
            audio_file = client.files.get(name=audio_file.name)

        if audio_file.state.name == "FAILED":
            raise ValueError(audio_file.state.name)

        print(f'上传音频文件（{segment}）Done')


        # 生成内容
        response = client.models.generate_content(
            model='gemini-2.0-pro-exp-02-05',
            contents=[
              audio_file,
              'Convert this audio to text',
            ]
        )
        segment_text = response.text
        print("音频文本 = ", segment_text)
        full_text += segment_text + "\n"


    # 文本写入文件
    with open(output, 'w', encoding='utf-8') as f:
        f.write(full_text)
        f.close()
    print("语音识别文本已写入！")


def text_summary(input, output):
    with open(input, 'r', encoding='utf-8') as f:
        audio_text = f.read()
        f.close()
    print("语音识别文本已读取！")

    # 文本提取要点
    response = client.models.generate_content(
        model='gemini-2.0-pro-exp-02-05',
        contents=f'text: {audio_text}。Extract the main points according to the text content and summarize them, and generate output Chinese meeting minutes',
    )
    audio_extract = response.text
    print("要点提取 = ", audio_extract)

    # 会议纪要写入文件
    with open(output, 'w', encoding='utf-8') as f:
        f.write(audio_extract)
        f.close()
    print("会议纪要已写入！")


if __name__=="__main__":
    # 记录程序开始时间
    start_time = datetime.now()
    print(f"程序开始时间: {start_time}")

    file_path = 'data/audio/12月24日InvestFU项目视频.wav'

    filename_with_extension = os.path.basename(file_path)  # 获取文件名带扩展名
    filename, file_extension = os.path.splitext(filename_with_extension)  # 分离文件名和扩展名
    output1 = 'results/gemini-pro/text/gemini-' + filename + '.txt'
    output2 = 'results/gemini-pro/summary/gemini-' + filename + '.txt'

    # 创建文件夹（如果不存在）
    os.makedirs(os.path.dirname(output1), exist_ok=True)
    os.makedirs(os.path.dirname(output2), exist_ok=True)


    # 音视频处理
    audio_path = to_audio(file_path)

    # 语音识别
    audio_to_text(audio_path, output1)

    # # 语音识别 - 分割，默认每十分钟一段
    # segment_length_ms = 600000
    # segments = split_audio(audio_path, filename)
    # audio_to_text_segments(segments, output1)

    # 会议纪要
    text_summary(output1, output2)


    # 记录程序结束时间
    end_time = datetime.now()
    print(f"程序结束时间: {end_time}")

    # 计算运行耗时
    run_time = end_time - start_time
    print(f"程序运行耗时: {run_time}")
