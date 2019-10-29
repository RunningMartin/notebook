# HTTP实验

## 0X00 梗概

我的测试环境是`Deepin`，如果你的测试环境是`Ubuntu`或`Centos`，请使用相关命令安装依赖`pcre`、`zlib`和`openssl`。

## 0X01 准备

```bash
# 下载nginx源码：https://nginx.org/en/download.html
➜  ~ mkdir /home/fangjie/Desktop/network_lib
➜  ~ cd /home/fangjie/Desktop/network_lib
➜  network_lib wget https://nginx.org/download/nginx-1.17.3.tar.gz
➜  network_lib tar -zxvf nginx-1.17.3.tar.gz

# 安装依赖
➜  network_lib sudo apt install libpcre3 libpcre3-dev
➜  network_lib sudo apt install zlib1g zlib1g-dev
➜  network_lib sudo apt install openssl

# 下载openssl 1.1.1 tls 1.3需要
➜  network_lib wget -c  https://github.com/openssl/openssl/archive/OpenSSL_1_1_1.tar.gz
➜  network_lib tar -zxvf OpenSSL_1_1_1.tar.gz
➜  network_lib mv openssl-OpenSSL_1_1_1 openssl

# 安装http2测试工具nghttp2
➜  network_lib sudo apt install nghttp2

# 存储你的域名证书信息，我的域名证书是从阿里云购买的
➜  network_lib mkdir cert

# 修改hosts，将127.0.0.1映射到域名上，便于本地测试
# 修改内容如下
➜  network_lib cat /etc/hosts
127.0.0.1	localhost
127.0.1.1   fangjie-PC
127.0.0.1   fangjie.site
127.0.0.1   www.fangjie.site

# 准备好后，实验环境目录结构
➜  network_lib mkdir nginx_lib
➜  network_lib tree -L 1
.
├── cert
├── nginx-1.17.3
├── nginx-1.17.3.tar.gz
├── nginx_lib
├── openssl
└── openssl-OpenSSL_1_1_1.tar.gz
```

## 0X0 HTTP/2实验

```bash
➜  network_lib cd nginx-1.17.3
# 编译
# prefix 指定安装目录 --with指定需要启动的模块
➜  nginx-1.17.3 ./configure --prefix=/home/fangjie/Desktop/network_lib/nginx_lib/httpv2 --with-http_ssl_module --with-http_v2_module

# 安装
➜  nginx-1.17.3 make && make install
➜  nginx-1.17.3 cd ../nginx_lib/httpv2

# 拷贝证书
➜  httpv2 sudo cp -r /home/fangjie/Desktop/network_lib/cert ./cert
➜  httpv2 tree -L 1
.
├── cert
├── conf
├── html
├── logs
└── sbin

# 编写配置文件conf/nginx.conf
worker_processes  1;
  
events {
worker_connections  1024;
}
  
http {
    include       mime.types;
    default_type  application/octet-stream;

    sendfile        on;
    keepalive_timeout  65;

    server {
        server_name fangjie.site www.fangjie.site;
        
        # 打开h2c，只支持直接发送h2c请求，不支持从http1.1升级到http2
        listen 80 http2;
        
        # 使用h2
        # listen 443 ssl http2;
        # ssl_certificate ../cert/www.fangjie.site.pem;
        # ssl_certificate_key ../cert/www.fangjie.site.key;

        location / {
            return 200 "ssl_cipher:$ssl_cipher
ssl_protocol:$ssl_protocol
http version:$server_protocol
http2 protocol:$http2
";
        }
    }
}

# 重新加载配置
➜  httpv2 sudo sbin/nginx -s reload
```

h2

![http2 h2c](../Documents/notebook/网络/HTTP协议/raws/HTTP实验/http2 h2c.png)