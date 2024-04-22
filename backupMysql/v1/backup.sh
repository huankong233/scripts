#!/bin/bash
#备份目录
MYSQL_FILEDIR=/storage/mysql/date
BACKUP_FILEDIR=/storage/mysql/backups
#当前日期
DATE=$(date +%Y-%m-%d-%T)

7z a $BACKUP_FILEDIR/$DATE.7z $MYSQL_FILEDIR
