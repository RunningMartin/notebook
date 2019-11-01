# HTTP

## 处理流程

针对HTTP请求，Nginx定义了一个处理流程，该处理流程有11个阶段。除HTTP过滤模块和只提供变量的模块之外，其他HTTP模块必须在这11个阶段之中。

![Nginx 11个阶段,图片来源于极客时间](../raw/HTTP/Nginx 11个阶段.png)

每个阶段中都对应着相关的模块，同一个阶段中可以有多个模块，模块之间也会有执行顺序。

![HTTP 官方模块执行顺序,图片来源于极客时间](../raw/HTTP/HTTP 官方模块执行顺序.png)

具体的执行顺序将在`configure`的产物`ngx_modules.c`中定义，`ngx_module_names`定义了相关模块的执行顺序(执行顺序是定义的倒序)。

```c
char *ngx_module_names[] = {
… …
"ngx_http_static_module",
"ngx_http_autoindex_module",
"ngx_http_index_module",
"ngx_http_random_index_module",
"ngx_http_mirror_module",
"ngx_http_try_files_module",
"ngx_http_auth_request_module",
"ngx_http_auth_basic_module",
"ngx_http_access_module",
"ngx_http_limit_conn_module",
"ngx_http_limit_req_module",
"ngx_http_realip_module",
"ngx_http_referer_module",
"ngx_http_rewrite_module",
"ngx_http_concat_module",
… …
}
```

当请求到来后，Nginx会依次调用阶段对应的模块，处理请求。

## POST_READ

### 理论

`POST_READ`阶段只有一个模块`ngx_http_realip_module`，该模块负责修改变量`remote_addr`中存储的客户端地址，默认是从TCP四元组中取源IP。如果传输过程中出现代理，通过`remote_addr`将不能获取到用户真实的IP，后续的限流操作也就无从谈起。

HTTP中有三种方法用于获取客户端的真实IP：

- `X-Real-IP`：记录客户端真实IP。
- `X-Forwarded-For`：会以链表形式表示为谁转发的信息。如`X-Forwarded-For:127.0.0.1,192.168.0.1`，当前HTTP请求转发自`192.168.0.1`。
- `proxy_protocol`：代理协议，会在TCP报文前添加源IP、源端口、目标IP、目标端口。

`realip`模块默认避讳编译进Nginx，需要在`configure`时通过`--with-http_realip_module`启用该功能。该模块提供两个变量：

- `realip_remote_addr`：TCP连接源IP。
- `realip_remote_port`：TCP连接源端口。

还提供三个命令

- `set_real_ip_from`：设置可信地址，只有可信地址的连接才替换`remote_addr`。
- `real_ip_header`：指定`remote_addr`来源，如果采用X-Forwarded-For时，取末尾IP。
- `real_ip_recursive`：为`on`时，根据`X-Forwarded-For`，从右到左找第一个不是`set_real_ip_from`指定的IP。

### 实践

```nginx
# 编辑nginx.conf
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
        listen 8080;
        server_name localhost;
        error_log logs/myerror.log debug;
        set_real_ip_from  127.0.0.1;
        #real_ip_header X-Real-IP;
        #real_ip_recursive off;
        real_ip_recursive on;
        real_ip_header    X-Forwarded-For;

        location /{
            return 200 "Client real ip: $remote_addr\n";
        }

    }
}

# 测试结果
➜  conf curl -H 'X-Forwarded-For:192.168.1.1,127.0.0.1' -H 'X-Real-IP:192.168.0.1' -v 127.0.0.1:8080
* Rebuilt URL to: 127.0.0.1:8080/
*   Trying 127.0.0.1...
* TCP_NODELAY set
* Connected to 127.0.0.1 (127.0.0.1) port 8080 (#0)
> GET / HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/7.52.1
> Accept: */*
> X-Forwarded-For:192.168.1.1,127.0.0.1
> X-Real-IP:192.168.0.1
> 
< HTTP/1.1 200 OK
< Server: nginx/1.17.3
< Date: Wed, 23 Oct 2019 12:34:31 GMT
< Content-Type: application/octet-stream
< Content-Length: 28
< Connection: keep-alive
< 
Client real ip: 192.168.1.1
* Curl_http_done: called premature == 0
* Connection #0 to host 127.0.0.1 left intact
```

### 注意

- `set_real_ip_from`、`real_ip_header`不要放在`location`中，否则`remote_addr`将不会生效。
## SERVER_REWRITE

`SERVER_REWRITE`和`REWRITE`阶段将由`ngx_http_rewrite_module`模块负责处理。`rewrite`
