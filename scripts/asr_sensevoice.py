from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess


def asr_sv(input_audio):
    model_dir = "iic/SenseVoiceSmall"

    model = AutoModel(
        model=model_dir,
        vad_model="fsmn-vad",
        vad_kwargs={"max_single_segment_time": 30000},
        device="cuda:0",
    )

    res = model.generate(
        input=input_audio,
        cache={},
        language="auto",  # "zn", "en", "yue", "ja", "ko", "nospeech"
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,
        merge_length_s=15,
    )
    text = rich_transcription_postprocess(res[0]["text"])
    return text


if __name__ == '__main__':
    input="./data/asr/audio_1.m4a"
    text = asr_sv(input)
    print(text)


