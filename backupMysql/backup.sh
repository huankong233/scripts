#!/bin/bash

# MYSQL容器名
CONTAINER_NAME=mysql
# MYSQL用户名
MYSQL_USERNAME=root
# MYSQL密码
MYSQL_PASSWORD=password
# MYSQL数据库名(用空格隔开)
MYSQL_DATABASES="db1 db2"
# 保存路径
BACKUP_FILEDIR=/storage/mysql/backups
# 备份文件名(默认时间)
BACKUP_FILENAME=$(date +%Y-%m-%d-%T)
# 保留多少份
BACKUP_LIMIT=100

# 获取SQL文件
docker exec $CONTAINER_NAME mysqldump -u$MYSQL_USERNAME -p$MYSQL_PASSWORD --databases $MYSQL_DATABASES > $BACKUP_FILEDIR/sql.sql
# 压缩文件
7z a $BACKUP_FILEDIR/$BACKUP_FILENAME.7z $BACKUP_FILEDIR/sql.sql
# 删除SQL文件
rm -rf $BACKUP_FILEDIR/sql.sql

# 统计文件夹内的文件数
COUNT=$(find $BACKUP_FILEDIR -type f | wc -l)
# 如果文件数超过阈值，就删除最老的文件，直到达到阈值
while [ "$COUNT" -gt "$BACKUP_LIMIT" ]
do
  # 找到最老的文件，根据文件名排序
  OLDFILE=$(find $BACKUP_FILEDIR -type f -printf '%f\n' | sort | head -n 1)
  # 删除最老的文件
  rm $BACKUP_FILEDIR/$OLDFILE
  # 更新文件数
  COUNT=$(find $BACKUP_FILEDIR -type f | wc -l)
done