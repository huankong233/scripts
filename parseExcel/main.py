import os
import re
import pandas
import shutil

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
cols = range(0, 3)  # 需要读取的列
# cols = [0, 1, 2]  # 需要读取的列(手动定义)
regex = True  # 是否需要使用正则提取名称
regex_expression = r"学生：(\w+)-\d+-\w+"  # 正则的表达式

if os.path.isdir(outDir):
    shutil.rmtree(outDir)
    os.mkdir(outDir)
else:
    os.mkdir(outDir)


if __name__ == '__main__':
    data = {}

    df = pandas.read_excel(f"{doc_dir}/{doc_name}", index_col=None,
                           na_values=['NA'], usecols=cols)

    # 格式化数据
    for index, col_index in enumerate(cols):
        if (index == 0):
            # 第一列（名称列）
            col_name = df.columns[col_index]
            for index, name in enumerate(df[col_name]):
                # 正则处理
                if (not regex):
                    data[index] = {'name': name}
                    continue
                else:
                    match = re.search(regex_expression, name)

                if (match):
                    data[index] = {'name': match.group(1)}
                else:
                    data[index] = {'name': name}
        else:
            col_name = df.columns[col_index]
            for index, file_name in enumerate(df[col_name]):
                file_path = f"{doc_dir}/{col_name}/{file_name}"
                data[index][col_name] = file_path

    # 复制文件
    for key, value in data.items():
        name = value["name"]
        os.mkdir(f"{outDir}/{name}")  # 创建文件夹
        for file, path in value.items():
            if file != "name":
                print(f"姓名:{name},数据名:{file},数据源:{path}")
                root, ext = os.path.splitext(path)
                shutil.copy(path, f"{outDir}/{name}/{file}{ext}")  # 复制文件到文件夹
