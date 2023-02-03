#!/bin/bash
#备份目录
MYSQL_FILEDIR=/var/lib/docker/volumes/ce1991a4e6f1c50776f6ee75450c896c117747eefb7ed6e9cdfe48f782e2e9f1/_data
BACKUP_FILEDIR=/storage/mysql/backups
#当前日期
DATE=$(date +%Y-%m-%d-%T)

7z a $BACKUP_FILEDIR/$DATE.7z $MYSQL_FILEDIR
