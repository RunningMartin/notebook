# Linux 安装OpenResty

## 二进制文件安装

二进制文件安装请参考[官方二进制文件安装教程](<https://openresty.org/cn/linux-packages.html>)

## 源码安装

- 下载源码：`https://openresty.org/cn/download.html#最新版`
- 解压：`tar -zxvf openresty-1.15.8.1.tar.gz`
- 安装依赖：`sudo apt-get install libpcre3-dev 
  libssl-dev perl make build-essential curl`
- 生成配置文件：`cd openresty-1.15.8.1;./configure --prefix=/usr/local/apps`
- 安装：`make && sudo make install`
- 设置软连接：`sudo ln -sf /usr/local/apps/bin/openresty /usr/bin/openresty`
- 启动：`sudo openresty -p www -c conf/nginx.conf`
- 测试：访问`http://localhost/`

![](raws/openresty初始界面.png)

## telnet安装

- 安装`openbsd-inetd`：`sudo apt install openbsd-inetd`
- 安装服务：`sudo apt install telnetd`
- 重启`openbsd-inetd`：`sudo /etc/init.d/openbsd-inetd restart`