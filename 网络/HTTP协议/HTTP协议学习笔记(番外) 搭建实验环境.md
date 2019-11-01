# HTTP协议学习笔记(番外) 搭建实验环境

这一章将介绍如何搭建《透视HTTP协议》这一门课中的实验环境。这一门课中需要安装两个软件：

- openresty下载地址：https://openresty.org/cn/download.html
- wireshark：抓包工具，下载地址https://www.wireshark.org/#download
- 课件：https://github.com/chronolaw/http_study

我主要介绍如何在Linux上安装环境。如果想要系统学习HTTP协议，可以扫码了解下，这门课我已经学了大半了，真心不错。

![](raws/搭建实验环境/推广.jpg)

## 0X00 openretry源码安装

- 安装流程

```bash
# 下载源码：`https://openresty.org/cn/download.html#最新版`
# 解压
➜  Desktop tar -zxvf openresty-1.15.8.1.tar.gz
# 安装依赖
➜  Desktop sudo apt-get install libpcre3-dev libssl-dev perl make build-essential curl
# 生成配置文件，/etc/apps是安装目录
➜  Desktop cd openresty-1.15.8.1;./configure --prefix=/etc/apps`，
# 安装
➜  Desktop make && sudo make install
# 设置软连接：
➜  Desktop sudo ln -sf /etc/apps/bin/openresty /usr/bin/openresty
# 修改host文件，添加如下三行
127.0.0.1       www.chrono.com
127.0.0.1       www.metroid.net
127.0.0.1       origin.io
➜  Desktop sudo vi /etc/host
# 启动
➜  Desktop cd http_study;sudo openresty -p www -c conf/nginx.conf
```

- 测试：访问`http://localhost/

![](raws/openresty初始界面.png)

## 0X01 telnet安装

- 安装`openbsd-inetd`：`sudo apt install openbsd-inetd`
- 安装服务：`sudo apt install telnetd`
- 重启`openbsd-inetd`：`sudo /etc/init.d/openbsd-inetd restart`

## 0X02 wireshark安装

- 安装：`sudo apt-get install wireshark -y`
- 授权：`sudo chmod +x /usr/bin/dumpcap`
- 启动：`wireshark`

## 0X03 wireshark 基本使用

- 加载已有包文件

  <video src="raws/搭建实验环境/加载已有包文件.mp4"></video>

- 抓包

<video src="raws/搭建实验环境/wireshark抓包.mp4"></video>

---

## 0X04 总结

这篇文章介绍了如何搭建一个测试环境和wireshark抓包简单使用，希望大家在学习HTTP协议时，利用wireshark抓抓包，看看现实中HTTP协议是如何工作的。

![微信号](../../公共图片/微信号.png)