import requests
import os
from pathlib import Path
import datetime
from tqdm import tqdm
import urllib3
urllib3.disable_warnings()  # 禁用证书认证和警告

# 下载m3u8视频，支持多个
# 视频存储地址的最后需要要加上/

save_path = 'D:/'
m3u8_list = ["https://978212-1316292924.cos.ap-beijing.myqcloud.com/2S3L133610.m3u8"]

def download():
    path = Path(save_path)
    # 如果文件夹不存在，则创建
    if not path.is_dir():
        os.mkdir(save_path)
    for i in range(len(m3u8_list)):
        print(f'开始下载{m3u8_list[i]}')
        start = datetime.datetime.now().replace(microsecond=0)
        ts_urls = []
        m3u8 = requests.get(url=m3u8_list[i])
        content = m3u8.text.split('\n')
        for s in content:
            # 如果是注释就跳过
            if s and s.find('#') == -1:
                ts_urls.append(s)
        download_ts(ts_urls, down_path=f"{save_path}video{str(i+1)}.ts")
        end = datetime.datetime.now().replace(microsecond=0)
        print(f'耗时：{end - start}')


# 下载文件并拼接
def download_ts(ts_urls, down_path):
    file = open(down_path, 'wb')
    for i in tqdm(range(len(ts_urls))):
        ts_url = ts_urls[i]
        # 可以开启，但是速度会变慢很多
        # time.sleep(1)
        try:
            response = requests.get(url=ts_url, stream=True, verify=False)
            file.write(response.content)
        except Exception as e:
            print('异常请求：%s' % e.args)
    file.close()


if __name__ == '__main__':
    download()
