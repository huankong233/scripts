# 介绍

这是一个简单的备份mysql数据库的脚本
需要安装`p7zip`

## 使用方法

### (1)配置备份脚本

1.将`backup.sh`放到适合的位置
2.修改变量
3.测试运行一次

### (2)配置定时器

1.将`backupMysql.service`和`backupMysql.timer`放到`/etc/systemd/system/`下
2.修改`backupMysql.service`中的第7行的`ExecStart`的值,后面更上的改成完整的绝对路径!
2.使用`systemctl enable backupMysql.timer`和`systemctl enable backupMysql.service`激活
3.使用`systemctl start backupMysql.service`测试脚本运行状态
4.使用`systemctl start backupMysql.timer`激活计时器

### (3)过一段时间自行检查效果
