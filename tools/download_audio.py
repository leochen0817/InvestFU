import os


# 下载音视频
def download_audio(video_url, output_file):
    os.system(f'yt-dlp -f "bestaudio" {video_url} --output {output_file}')
    print('音视频下载完成')


if __name__ == '__main__':
    output = "../data/asr/audio_2.m4a"
    download_audio(video_url="https://www.bilibili.com/video/BV1Kx4y1W7TP", output_file=output)
