import os
import re
import pandas
import shutil

# 注意:
# 腾讯文档直接下载附件可能会导致文件丢失，因为文件名可能会重复，需要单独下载指定段的文件手动整理

# 使用方法:
# 第一列为名称列，用来给文件夹命名
# 后面的每一列都会当做需要取的数据
# 列里的内容需要是文件的名称
# 文件存放的文件夹需要是这一列的第一行的名称
# 最好先编辑好了源文件后再运行脚本
# 列与列之间不能有空格

outDir = "./dist"  # 输出文件夹
doc_dir = "./docs"  # 输入文件夹
doc_name = "图片截图收集（收集结果）.xlsx"  # 文档名
cols = range(2, 5)  # 需要读取的列
# cols = [2, 4]  # 需要读取的列(手动定义)
regex = True  # 是否需要使用正则提取名称
regex_expression = r"学生：(\w+)-\d+-\w+"  # 正则的表达式

if __name__ == "__main__":
    # 清空输出文件夹
    if os.path.isdir(outDir):
        shutil.rmtree(outDir)
        os.mkdir(outDir)
    else:
        os.mkdir(outDir)

    data = {}

    df = pandas.read_excel(
        f"{doc_dir}/{doc_name}", index_col=None, na_values=["NA"], usecols=cols
    )

    # 格式化数据
    for index in range(0, len(cols)):
        col_name = df.columns[index]
        if index == 0:
            # 第一列（名称列）
            for index, name in enumerate(df[col_name]):
                # 正则处理
                if not regex:
                    data[index] = {"name": name}
                    continue
                else:
                    match = re.search(regex_expression, name)

                if match:
                    data[index] = {"name": match.group(1), "data": {}}
                else:
                    data[index] = {"name": name, "data": {}}
        else:
            for index, file_name in enumerate(df[col_name]):
                data[index]["data"][col_name] = f"{doc_dir}/{col_name}/{file_name}"

    # 复制文件
    for key, value in data.items():
        name = value["name"]
        for filename, filepath in value["data"].items():
            print(f"姓名: {name}\t数据名: {filename}\t数据源: {filepath}")
            root, ext = os.path.splitext(filepath)
            if len(cols) > 2:
                if not os.path.isdir(f"{outDir}/{name}"):
                    os.mkdir(f"{outDir}/{name}")  # 创建文件夹
                shutil.copy(filepath, f"{outDir}/{name}/{filename}{ext}")  # 复制文件到文件夹
            else:
                shutil.copy(filepath, f"{outDir}/{name}{ext}")  # 复制文件到文件夹
