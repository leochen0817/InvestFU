# ASR
FunASR + paraformer-zh模型

## 音频提取
1. 如果本地直接有音频文件，可跳过此步。
2. 如果本地是视频文件，使用`ffmpeg`提取音频，代码见 tools/audio_handle.py
```py
ffmpeg.input(input_video).output(output_audio, format='wav').run()
```
3. 如果是在线视频提取音频文件，使用 `yt-dlp` 工具，代码见 tools/download_audio.py
```bash
yt-dlp -f "bestaudio" "视频URL" --output "输出文件路径"
```


## 音频切割
FunASR可自动处理音频分段，无需切割。
若使用其他模型做语音识别长音频无法识别完整（如Gemini），可先切割音频，代码见 tools/audio_handle.py - split_audio方法。
使用 `pydub` 库做音频切割。
```py
def split_audio(filepath, filename, segment_length_ms=600000):  # 默认每10分钟一段
    audio = AudioSegment.from_file(filepath)
    segments = []
    for i, start_time in enumerate(range(0, len(audio), segment_length_ms)):
        end_time = start_time + segment_length_ms
        segment = audio[start_time:end_time]
        segment_path = f"audio/segments/segment_{filename}_{i}.wav"
        segment.export(segment_path, format="wav")
        segments.append(segment_path)
    print(f"视频分割完成！segments = {segments}")
    return segments
```

## 音频识别
首先，我们尝试了四组模型进行语音识别和文本纪要整理，并对多组音视频、多种时长、中英文语言进行了对比。
* Gemini-2.0-flash
* Gemini-2.0-pro-exp-02-05
* FunASR paraformer-zh
* FunASR SenseVoiceSmall

项目视频：10分钟（97401KB）https://www.bilibili.com/video/BV1f4kRYwE1o （InvestFU项目视频）  
其中，项目视频的对比数据如下：  
| | Gemini-2.0-flash | Gemini-2.0-pro-exp-02-05 | FunASR-paraformer-zh | FunASR-SenseVoiceSmall |
| --- | --- | --- | --- | --- |
| 运行耗时 | 2分钟+ |  2分钟+ |  43秒 |  20秒 | 
| 识别完整度 | 完整 |  完整 |  完整 |  完整 | 
| 识别效果 | 优秀 |  优秀 |  优秀 |  较优秀，存在部分错别字，在文本总结会议纪要时部分被修正 | 
| 多角色区分 | 无 |  无 |  无 |  无 | 

另外，Gemini在超长音频上表现出识别不完整，切割后再分段识别运行时间更久的问题；FunASR SenseVoiceSmall表现出文本错误较多的问题等。  
最终，根据多组音频识别效果表现、成本、运行时长等综合能力，最终选定 FunASR paraformer-zh 模型作为语言识别模型、Gemini-2.0-pro模型/deepseek-V3模型作为后续识别文本的整理纪要生成模型。

输入音频文件，通过FunASR调用paraformer-zh模型进行识别输出音频文本。
```py
# pip3 install -U funasr
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
import os
from datetime import datetime
from tools.audio_handle import to_audio
from asr_gemini_pro import text_summary

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
```

Gemini-2.0-pro模型生成识别文本的纪要。
```py
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
```

识别示例：  
[项目视频语言识别文本](./results/funasr-pf/text/12月24日InvestFU项目视频.txt)  
[项目视频文本纪要](./results/funasr-pf/summary/12月24日InvestFU项目视频.txt)
