import os
import random
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

max_workers = 16

path = r"C:\Users\huan_kong\Desktop\code\集训\vue3_admin_template"

# 定义一个字典，存储时间范围
time_range = {
    "start_year": 2023,
    "end_year": 2023,
    "start_month": 7,
    "end_month": 7,
    "start_day": 1,
    "end_day": 26,
    "start_hour": 8,
    "end_hour": 17
}

# 定义一个函数，用于生成随机的时间字符串，格式为 YYYYMMDDhhmmss
def random_time(time_range):
    year = random.randint(time_range["start_year"], time_range["end_year"])
    month = random.randint(time_range["start_month"], time_range["end_month"])
    day = random.randint(time_range["start_day"], time_range["end_day"])
    hour = random.randint(time_range["start_hour"], time_range["end_hour"])
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return f"{year:04}-{month:02}-{day:02} {hour:02}:{minute:02}:{second:02}"


# 定义一个函数，用于调用 PowerShell 命令修改文件的创建时间和修改时间
def change_file_time(file_path, creation_time, modification_time):
    print(f"正在处理：{file_path}\n创建时间：{creation_time}\n修改时间：{modification_time}") # 打印修改时间
    command = f"powershell.exe (Get-Item '{file_path}').creationtime = '{creation_time}'; (Get-Item '{file_path}').lastwritetime = '{modification_time}'"
    subprocess.run(command)

# 创建一个线程池对象，指定最大线程数为10
executor = ThreadPoolExecutor(max_workers=max_workers)

# 获取当前目录下的所有文件和子文件夹
futures = [] # 创建一个空列表，用于存储 Future 对象
for root, dirs, files in os.walk(path):
    # 遍历每个文件夹，随机生成创建时间和修改时间，并提交任务给线程池
    for dir in dirs:
        dir_path = os.path.join(root, dir) # 获取完整的文件夹路径
        creation_time = random_time(time_range) # 假设创建时间是根据字典中的时间范围随机生成的
        modification_time = random_time(time_range) # 假设修改时间也是同样的范围
        future = executor.submit(change_file_time, dir_path, creation_time, modification_time) # 提交任务给线程池，返回 Future 对象
        futures.append(future) # 把 Future 对象添加到列表中
  
    # 遍历每个文件，随机生成创建时间和修改时间，并提交任务给线程池
    for file in files:
        file_path = os.path.join(root, file) # 获取完整的文件路径
        creation_time = random_time(time_range) # 假设创建时间是根据字典中的时间范围随机生成的
        modification_time = random_time(time_range) # 假设修改时间也是同样的范围
        future = executor.submit(change_file_time, file_path, creation_time, modification_time) # 提交任务给线程池，返回 Future 对象
        futures.append(future) # 把 Future 对象添加到列表中

# 遍历 Future 对象，获取结果或异常
for future in as_completed(futures):
    try:
        result = future.result() # 获取任务的返回值，如果有异常，会抛出
    except Exception as e:
        print(e) # 打印异常信息
