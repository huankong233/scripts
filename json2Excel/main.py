import json
import os
import pandas


__file__ = os.path.dirname(os.path.abspath(__file__)) + "/"

baicizhantopicproblem = input("请输入data.json路径:") or "./data.json"

# 读取json文件

with open(baicizhantopicproblem, "r", encoding="utf-8") as file:
    data = json.load(file)

# 创建 excel 文件
df = pandas.DataFrame(data)
df.to_excel(__file__ + "/data.xlsx", index=False)
