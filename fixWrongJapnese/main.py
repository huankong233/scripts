import os

srcDir = r"C:\Users\huan_kong\Downloads\Custom_Udon"

for root, dirs, files in os.walk(srcDir):
    # 遍历当前子文件夹中的所有文件
    for filename in files:
        fullPath = os.path.join(root, filename)
        try:
            newName = filename.encode("gbk").decode("shift-jis")
            newPath = os.path.join(root, newName)
            os.rename(fullPath, newPath)
            print(newPath)
        except Exception as error:
            print(f"{fullPath} 处理失败 已跳过")
            print(error)
