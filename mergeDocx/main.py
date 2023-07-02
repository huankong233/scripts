import os
from win32com import client as wc
from docx import Document
from docxcompose.composer import Composer

original_docx_path = 'C:/Users/huan_kong/Desktop/123/周兴瑞/日总结'
new_docx_path = 'C:/Users/huan_kong/Desktop/123/周兴瑞.docx'

# 获取文件列表
doc_files = os.listdir(original_docx_path)

# 将doc文件转化为docx
word = wc.Dispatch("Word.Application")  # 打开word应用程序
word.Visible = True
for file in doc_files:
    file = f"{original_docx_path}/{file}"
    print(file)
    doc = word.Documents.Open(file)  # 打开word文件
    doc.SaveAs("{}x".format(file), 12)  # 另存为后缀为".docx"的文件
    doc.Close()  # 关闭原来word文件
    if '.docx' in file:
        os.remove(file)
        os.rename(file + 'x', file)
word.Quit()

# 合并docx

result = []


def search(path=".", name=""):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            search(item_path, name)
        elif os.path.isfile(item_path):
            if name in item:
                global result
                result.append(item_path)
                print(item_path)


search(path=original_docx_path, name=".docx")

files = result


def combine_all_docx(filename_master, files_list):
    number_of_sections = len(files_list)
    master = Document(filename_master)
    master.add_page_break()  # 强制新一页
    composer = Composer(master)
    for i in range(1, number_of_sections):
        doc_temp = Document(files_list[i])
        doc_temp.add_page_break()  # 强制新一页
        composer.append(doc_temp)
    composer.save(new_docx_path)


combine_all_docx(result[0], result)
print("...合并完成...")
