#!/bin/bash

# 这个脚本是用于批量解压文件的
# 使用方法：bash decompress.sh [后缀] [目录] [密码]
# 例如：bash decompress.sh zip /home/user 123456

# 检查是否提供了后缀和目录
if [ $# -lt 2 ]; then
  echo "缺少参数"
  echo "使用方法：bash decompress.sh [后缀] [目录] [密码]"
  exit 1
fi

# 将参数赋值给变量
extension=$1
dir=$2
password=$3

for file in $dir/*.$extension; do
  # 检查文件是否存在
  if [ -f "$file" ]; then
    if [ -z "$password" ]; then
      7z x "$file" -o$dir
    else
      7z x "$file" -o$dir -p$password
    fi
    echo "解压了 $file"
  fi
done

echo "完成！"