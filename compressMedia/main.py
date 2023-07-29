import os
import re
import subprocess
from tqdm import tqdm
import threading

# 输入
src_dir = r"input"
# 输出
dst_dir = r"output"

video = {
    # 自动覆盖源文件
    "override": True,
    # 使用硬件加速
    "hwaccel": "auto",
    # 编码器
    "encode": "h264_nvenc",
    # crf
    "crf": "23",
    # 视频比特率
    "bit_rate": "5M",
    # 帧数
    "fps": False,
    # 分辨率
    "resolution": "1920:1080",
    # 输出格式
    "formats": "mp4",
}

image = {
    # 自动覆盖源文件
    "override": True
}

# 视频
video_exts = [".mp4", ".avi", ".mkv", ".flv", ".mov"]

# 图片
image_exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif"]

# 设置最大线程数
max_threads = 3


def compress(filename, src, dst):
    if os.path.splitext(filename)[1] in video_exts:
        # 获取总帧数
        ffprobe_cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-count_packets",
            "-show_entries",
            "stream=nb_read_packets",
            "-of",
            "csv=p=0",
            src,
        ]

        all_frames = float(subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE).stdout)
        pbar = tqdm(total=all_frames, unit="frame", desc=f'压缩视频: "{filename}"')

        ffmpeg_cmd = [
            "ffmpeg",
            # 隐藏不必要的信息
            "-hide_banner",
            # 使用硬件加速
            "-hwaccel",
            video["hwaccel"],
            # 自动覆盖源文件
            "-y" if video["override"] else None,
            # 输入文件
            "-i",
            src,
            # 编码器
            "-c:v",
            video["encode"],
            # 视频比特率
            "-b:v",
            video["bit_rate"],
            # 分辨率
            "-vf",
            f'scale={video["resolution"]}',
            # crf
            "-crf",
            video["crf"],
            # 帧数
            "-r" if video["fps"] else None,
            video["fps"] or None,
            # 输出格式
            "-f",
            video["formats"],
            # 输出
            "-c:a",
            "copy",
            dst,
            # 输出进度(不可去除)
            "-progress",
            "pipe:1",
        ]

        ffmpeg_cmd = [x for x in ffmpeg_cmd if x is not None]

        process = subprocess.Popen(
            ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        while True:
            if process.poll() is not None:
                pbar.close()
                # 释放信号量，表示一个线程结束了
                semaphore.release()
                break
            else:
                for line in process.stdout:
                    line = line.decode("utf-8")
                    if line.startswith("frame="):
                        match = re.search(r"frame=(\d+)", line)
                        if match:
                            now_frame = float(match.group(1))
                            pbar.update(now_frame - pbar.n)
    else:
        pbar = tqdm(total=1, unit="frame", desc=f'压缩图片: "{filename}"')
        ffmpeg_cmd = [
            "ffmpeg",
            # 隐藏不必要的信息
            "-hide_banner",
            # 自动覆盖源文件
            f'{"-y" if image["override"] else None}',
            # 输入文件
            "-i",
            f"{src}",
            # 输出文件
            f"{dst}",
            # 输出进度(不可去除)
            "-progress",
            "pipe:1",
        ]

        ffmpeg_cmd = [x for x in ffmpeg_cmd if x is not None]

        process = subprocess.Popen(
            ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        while True:
            if process.poll() is not None:
                pbar.update(1)
                pbar.close()
                # 释放信号量，表示一个线程结束了
                semaphore.release()
                break


if __name__ == "__main__":
    # 创建一个信号量对象，用于控制线程数
    semaphore = threading.Semaphore(max_threads)

    # 遍历源文件夹中的所有文件
    for root, dirs, files in os.walk(src_dir):
        # 遍历当前子文件夹中的所有文件
        for filename in files:
            file_ext = os.path.splitext(filename)[1]
            if file_ext in video_exts or file_ext in image_exts:
                # 获取源文件和目标文件的完整路径
                src_path = os.path.join(root, filename)
                # 获取源文件相对于源文件夹的相对路径
                rel_path = os.path.relpath(src_path, src_dir)
                # 拼接输出文件夹和相对路径，得到输出文件的完整路径
                dst_path = os.path.join(dst_dir, rel_path)
                # 是否存在输出文件夹
                if not os.path.exists(os.path.dirname(dst_path)):
                    os.makedirs(os.path.dirname(dst_path))
                # 获取信号量，表示一个线程开始了，如果达到最大线程数，会阻塞等待
                semaphore.acquire()
                # 创建一个线程，执行压缩的函数
                thread = threading.Thread(
                    target=compress, args=(filename, src_path, dst_path)
                )
                thread.start()
            else:
                print(f"{filename}不支持处理")
