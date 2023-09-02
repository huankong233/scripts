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
    # required=True,
    help="输出文件夹的路径，不输入则使用输入文件夹路径",
)
parser.add_argument(
    "-t",
    "--threads",
    type=int,
    default=5,
    help="设置最大线程数，默认5",
)
parser.add_argument(
    "-a",
    "--acceleration",
    action="store_true",
    help="开启硬件加速(auto)，默认关闭",
)
parser.add_argument(
    "-e",
    "--encoder",
    type=str,
    default="h264_nvenc",
    help="设置视频目标编码，默认为h264_nvenc，支持编码可使用ffmpeg -encoders查看",
)
parser.add_argument(
    "-c",
    "--crf",
    type=int,
    default=23,
    help="设置视频压缩的CRF，范围1-51，18以下无损，18-22高质量，22-27中等质量，51质量最差，默认23",
)
parser.add_argument(
    "-b",
    "--bitrate",
    type=str,
    default="3M",
    help="设置视频目标比特率，默认3M",
)
parser.add_argument(
    "-f",
    "--fps",
    type=int,
    default=None,
    help="设置视频目标帧数",
)
parser.add_argument(
    "-m",
    "--format",
    type=str,
    default="mp4",
    help="设置视频目标格式，默认mp4，支持格式可使用ffmpeg -formats查看",
)
parser.add_argument(
    "-r",
    "--resolution",
    type=str,
    default=None,
    help="设置视频目标分辨率，默认为视频原始分辨率",
)
args = parser.parse_args()

# 输入
src_dir = args.input
# 输出
dst_dir = args.output if args.output else src_dir

video = {
    "hwaccel": "auto" if args.acceleration else "none",
    "encode": args.encoder,
    "crf": str(args.crf),
    "bit_rate": args.bitrate,
    "fps": args.fps,
    "resolution": args.resolution,
    "formats": args.format,
}


image = {}

# 视频
video_exts = [".mp4", ".avi", ".mkv", ".flv", ".mov"]

# 图片
image_exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif"]

if src_dir == dst_dir:
    answer = input(f"输入和输出路径相同，是否需要覆盖？(Y/N): ")
    # override = answer.lower() == "y"
    if answer.lower() == "y":
        override = True
    else:
        override = False
        exit(0)

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
            "stream=nb_read_packets,width,height",
            "-of",
            "csv=p=0",
            src,
        ]

        ffprobe_output = subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE).stdout.decode("utf-8")
        ffprobe_info = ffprobe_output.strip().split(",")
        # print(f"{ffprobe_info}")
        video_width = int(ffprobe_info[0])
        video_height = int(ffprobe_info[1])
        all_frames = float(ffprobe_info[2])

        # Use original resolution if no resolution is specified
        if video["resolution"] is None:
            video["resolution"] = f"{video_width}:{video_height}"

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
