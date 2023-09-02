# 导入模块
import os
import re
import subprocess
from tqdm import tqdm
import threading
import argparse

# 创建一个解析器对象，添加命令行参数
parser = argparse.ArgumentParser(description="使用ffmpeg工具来压缩视频和图片文件")
parser.add_argument(
    "-i",
    "--input",
    type=str,
    required=True,
    help="输入文件夹的路径",
)
parser.add_argument(
    "-o",
    "--output",
    type=str,
    required=True,
    help="输出文件夹的路径",
)
parser.add_argument(
    "-v",
    "--video",
    action="store_true",
    help="是否处理视频文件",
)
parser.add_argument(
    "-p",
    "--image",
    action="store_true",
    help="是否处理图片文件",
)
parser.add_argument(
    "-t",
    "--threads",
    type=int,
    default=3,
    help="设置最大线程数，默认为3",
)
args = parser.parse_args()

# 输入
src_dir = args.input
# 输出
dst_dir = args.output

video = {
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

image = {}

# 视频
video_exts = [".mp4", ".avi", ".mkv", ".flv", ".mov"]

# 图片
image_exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif"]

if src_dir == dst_dir:
    answer = input(f"输入和输出路径相同，是否需要覆盖？(Y/N): ")
    if answer.lower() == "y":
        override = True
    else:
        override = False

def compress(filename, src, dst):

    output_path = dst

    if override:
        file_name, file_ext = os.path.splitext(src)
        tmp_path = file_name + "_temp" + file_ext
        output_path = tmp_path



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
            output_path,
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
            # 输入文件
            "-i",
            f"{src}",
            # 输出文件
            f"{output_path}",
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

    if override:
        tmp_size = os.path.getsize(tmp_path)
        src_size = os.path.getsize(src)
        if tmp_size < src_size:
            os.replace(tmp_path, src) # 替换文件
        else:
            print(f"{filename}压缩后的大小大于或等于源文件，舍弃")
            os.remove(tmp_path)

if __name__ == "__main__":
    # 创建一个信号量对象，用于控制线程数
    semaphore = threading.Semaphore(args.threads)

    # 遍历源文件夹中的所有文件
    for root, dirs, files in os.walk(src_dir):
        # 遍历当前子文件夹中的所有文件
        for filename in files:
            file_ext = os.path.splitext(filename)[1]
            if (file_ext in video_exts) or (
                file_ext in image_exts
            ):
                src_path = os.path.join(root, filename)
                rel_path = os.path.relpath(src_path, src_dir)
                dst_path = os.path.join(dst_dir, rel_path)
                semaphore.acquire()
                thread = threading.Thread(
                    target=compress, args=(filename, src_path, dst_path)
                )
                thread.start()
            else:
                print(f"{filename}不支持处理")
