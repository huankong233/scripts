import sqlite3
import json

baicizhantopicproblem = "./baicizhantopicproblem.db"
lookup = "./lookup.db"


conn1 = sqlite3.connect(baicizhantopicproblem)
#产生游标
cur = conn1.cursor()
#获得已背单词id
cur.execute("SELECT topic_id FROM ts_learn_offline_dotopic_sync_ids_575 WHERE do_num > 0 ORDER BY create_at")
wordId = cur.fetchall()
#关闭链接
conn1.close()
#从lookup表中寻找已经背的单词表
conn2 = sqlite3.connect(lookup)
cur = conn2.cursor()
sum = 0
data = []

for word in wordId:
    cur.execute(f"SELECT word,accent,mean_cn FROM dict_bcz WHERE topic_id = {word[0]}")
    word = cur.fetchall()
    Q = word[0][0]
    A = word[0][2]
    data.append({
      "Q":Q,
      "A":A
    })
    sum += 1

conn2.close()

file = open('data.json','w',encoding="utf-8")
file.write(json.dumps(data, ensure_ascii=False,indent=2))

print(f"共{sum}个单词")
