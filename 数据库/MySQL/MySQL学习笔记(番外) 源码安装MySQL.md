# MySQL学习笔记(番外) 源码安装MySQL

## 0X00 配置源

```bash
# 下载apt源 https://dev.mysql.com/downloads/repo/apt/
# 安装
➜  Desktop sudo dpkg -i mysql-apt-config_0.8.13-1_all.deb
```

然后会弹出界面，选择你的系统后选择OK(默认配置)即可。

![](raws/安装MySQL/安装源.png)

## 0X01 安装

```bash
# 更新包信息
➜  Desktop sudo apt update
➜  Desktop sudo apt-get install mysql-server
# 查看状态
# 修改密码，默认为空直接回车，也可以通过/etc/mysql/debian.cnf查看默认密码
➜  sudo mysql -u root -p
# 修改密码
MariaDB [mysql]> use mysql;
# 设置密码
MariaDB [mysql]> update user set authentication_string=PASSWORD("root") where User='root'; 
# 设置密码验证插件
MariaDB [mysql]> update user set plugin="mysql_native_password" where User='root'; 
MariaDB [mysql]> flush privileges;
MariaDB [mysql]> quit;
# 重启服务
➜  Desktop sudo service mysql start
# 验证，使用密码登录
➜  Desktop mysql -u root -p
```

## 0X02 参考

- https://stackoverflow.com/questions/37879448/mysql-fails-on-mysql-error-1524-hy000-plugin-auth-socket-is-not-loaded
- https://dev.mysql.com/doc/mysql-getting-started/en/