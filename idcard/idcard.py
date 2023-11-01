import time

# 定义一个函数，用于计算身份证号的校验码
def check_code2(id_number):
    # 定义一个字典，存储校验码对应的权重
    weight_dict = {1: 7, 2: 9, 3: 10, 4: 5, 5: 8, 6: 4, 7: 2, 8: 1, 9: 6, 10: 3, 11: 7, 12: 9, 13: 10, 14: 5, 15: 8, 16: 4, 17: 2}
    # 定义一个字典，存储余数对应的校验码
    check_dict = {0: '1', 1: '0', 2: 'X', 3: '9', 4: '8', 5: '7', 6: '6', 7: '5', 8: '4', 9: '3', 10: '2'}
    # 初始化一个变量，用于存储加权和
    sum = 0
    # 遍历身份证号的前17位，计算加权和
    for i in range(1,18):
        sum += int(id_number[i-1]) * weight_dict[i]
    # 计算余数
    remainder = sum % 11
    # 返回余数对应的校验码
    return check_dict[remainder]

# 定义一个函数，用于穷举身份证号
def enumerate_id(id_prefix):
    # 定义一个列表，用于存储生成的身份证号
    id_list = []
    # 遍历顺序码的可能值，从00到99
    for i in range(100):
        # 将顺序码转换为两位字符串，补零在前面
        order_code = str(i).zfill(2)
        # 拼接顺序码和性别码，得到倒数第三位到倒数第一位
        for i in range(1,9,2):
            last_three = order_code + str(i)
            # 拼接身份证号的前17位
            id_number = id_prefix + last_three
            # 调用check_code函数，计算校验码
            check_code = check_code2(id_number)
            # 拼接校验码，得到完整的身份证号
            id_number += check_code
            # 将身份证号添加到列表中
            id_list.append(id_number)
    # 返回列表
    return id_list

# 定义一个变量，存储给出的身份证号前14位
id_prefix = "33079120040725"
# 调用enumerate_id函数，穷举身份证号
id_list = enumerate_id(id_prefix)
# 打印列表中的身份证号，每行一个

def checkId(id,name,appcode):
    import requests
    headers = {
        'Authorization': f'APPCODE {appcode}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'idNo': f'{id}',
        'name': f'{name}',
    }
    response = requests.post('https://idenauthen.market.alicloudapi.com/idenAuthentication', headers=headers, data=data)
    json = response.json()
    print(json)
    return json['respMessage'] == '身份证信息匹配'

import check

for id_number in id_list:
    if(check.IdNumber.verify_id(id_number)):
      print(id_number)
      status = checkId(id_number,"邓晓飞",123456)
      if(status): exit()
      time.sleep(5)

