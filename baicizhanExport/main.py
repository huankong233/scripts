import sqlite3
import json
import re
import os

__file__ = os.path.dirname(os.path.abspath(__file__)) + "/"

baicizhantopicproblem = (
    input("请输入baicizhantopicproblem.db路径:") or __file__ + "./baicizhantopicproblem.db"
)
baicizhantopicproblemConn = sqlite3.connect(baicizhantopicproblem)
baicizhantopicproblemCursor = baicizhantopicproblemConn.cursor()

baicizhandoexampleinfo = (
    input("请输入baicizhandoexampleinfo.db路径:") or __file__ + "./baicizhandoexampleinfo.db"
)
baicizhandoexampleinfoConn = sqlite3.connect(baicizhandoexampleinfo)
baicizhandoexampleinfoCursor = baicizhandoexampleinfoConn.cursor()

lookup = input("请输入lookup.db路径:") or __file__ + "./lookup.db"
lookupConn = sqlite3.connect(lookup)
lookupCursor = lookupConn.cursor()

slice = input("是否需要裁切(y/n):")
if slice == "y" or slice == "Y":
    slice = True
else:
    slice = False

if slice:
    sliceWord = input("需要裁剪的词:") or "cheek"


# 获得已背词库
baicizhantopicproblemCursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' order by name"
)
databases = baicizhantopicproblemCursor.fetchall()
databases = filter(
    lambda value: value[0].startswith("ts_learn_offline_dotopic_sync_ids_"),
    databases,
)


def getBaicizhandoexampleinfo(id):
    # 获得已背词库
    baicizhandoexampleinfoCursor.execute(
        f"SELECT * FROM ZBOOKFINISHINFO WHERE book_id = {id}"
    )
    data = baicizhandoexampleinfoCursor.fetchall()
    return "已被删除的书" if len(data) == 0 else data[0][2]


def get_databases(database):
    database = {"table_name": database[0]}
    database["id"] = int(
        re.match(
            r"ts_learn_offline_dotopic_sync_ids_(.*)", database["table_name"]
        ).group(1)
    )
    database["name"] = getBaicizhandoexampleinfo(database["id"])
    return database


databases = map(get_databases, databases)
databases = list(databases)

print("\n现有以下数据库:")
print("数据库ID\t书名")

for database in databases:
    print(f"{database['id']}\t\t{database['name']}")

print("\n")

databaseID = input("请输入需要导出的数据库ID:")
if databaseID == "" or databaseID is None:
    raise Exception("未输入数据库ID")

database = next(
    (database for database in databases if database["id"] == int(databaseID)), None
)

if database is None:
    raise Exception("输入的数据库ID有误")

baicizhantopicproblemCursor.execute(
    f"SELECT topic_id FROM {database['table_name']} WHERE do_num > 0 ORDER BY create_at"
)
words = baicizhantopicproblemCursor.fetchall()


def get_word(topic_id):
    lookupCursor.execute(
        f"SELECT word,accent,mean_cn FROM dict_bcz WHERE topic_id = {topic_id}"
    )
    return lookupCursor.fetchall()[0]


data = []

for word in words:
    word = get_word(word[0])
    if slice and word[0] == sliceWord:
        data = []
    data.append({"Q": word[0], "A": word[2]})

file = open(__file__ + "data.json", "w", encoding="utf-8")
file.write(json.dumps(data, ensure_ascii=False, indent=2))

print(f"共{len(data)}个单词")
