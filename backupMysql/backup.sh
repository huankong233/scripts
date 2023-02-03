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

# 获取SQL文件
docker exec $CONTAINER_NAME mysqldump -u$MYSQL_USERNAME -p$MYSQL_PASSWORD --databases $MYSQL_DATABASES > $BACKUP_FILEDIR/sql.sql
# 压缩文件
7z a $BACKUP_FILEDIR/$BACKUP_FILENAME.7z $BACKUP_FILEDIR/sql.sql
# 删除SQL文件
rm -rf $BACKUP_FILEDIR/sql.sql