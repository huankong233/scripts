# 导入模块
import os
import re
import subprocess
from tqdm import tqdm
import threading
import logging  # 添加logging模块
import argparse  # 添加argparse模块

# 设置日志格式和级别
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO
)

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
src_dir = args.input  # 从命令行参数获取输入文件夹的路径
# 输出
dst_dir = args.output  # 从命令行参数获取输出文件夹的路径

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


def compress(filename, src, dst):

    # 判断输入与输出路径是否相同，如果相同则在原本文件名.后缀之前加一个_temp作为临时文件，否则直接使用输出路径
    if src == dst:
        file_name, file_ext = os.path.splitext(src) # 分割文件名和后缀名
        tmp_path = file_name + "_temp" + file_ext # 在文件名.后缀之前加一个_temp作为临时文件的路径
        output_path = tmp_path # 将输出路径设为临时文件的路径
        override = True # 设置覆盖标志为真，表示需要覆盖源文件
    else:
        output_path = dst # 将输出路径设为目标路径
        override = False # 设置覆盖标志为假，表示不需要覆盖源文件



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

    # 如果需要覆盖源文件，先对比压缩后的缓存文件和压缩前源文件的大小
    if override:
        tmp_size = os.path.getsize(tmp_path) # 获取临时文件的大小
        src_size = os.path.getsize(src) # 获取源文件的大小
        if tmp_size < src_size: # 如果临时文件小于源文件
            os.replace(tmp_path, src) # 替换文件
        else: # 如果临时文件大于或等于源文件
            logging.info(f"{filename}压缩后的大小大于或等于源文件，舍弃") # 使用logging模块输出信息
        os.remove(tmp_path) # 删除临时文件


if __name__ == "__main__":
    # 创建一个信号量对象，用于控制线程数
    semaphore = threading.Semaphore(args.threads)  # 从命令行参数获取最大线程数

    # 遍历源文件夹中的所有文件
    for root, dirs, files in os.walk(src_dir):
        # 遍历当前子文件夹中的所有文件
        for filename in files:
            file_ext = os.path.splitext(filename)[1]
            if (file_ext in video_exts) or (
                file_ext in image_exts
            ):  # 根据命令行参数判断是否处理视频或图片文件
                # 获取源文件和目标文件的完整路径
                src_path = os.path.join(root, filename)
                # 获取源文件相对于源文件夹的相对路径
                rel_path = os.path.relpath(src_path, src_dir)
                # 拼接输出文件夹和相对路径，得到输出文件的完整路径
                dst_path = os.path.join(dst_dir, rel_path)  # 使用os.path.join函数来拼接路径
                # 获取信号量，表示一个线程开始了，如果达到最大线程数，会阻塞等待
                semaphore.acquire()
                # 创建一个线程，执行压缩的函数
                thread = threading.Thread(
                    target=compress, args=(filename, src_path, dst_path)
                )
                thread.start()
            else:
                logging.info(f"{filename}不支持处理")  # 使用logging模块来记录信息
