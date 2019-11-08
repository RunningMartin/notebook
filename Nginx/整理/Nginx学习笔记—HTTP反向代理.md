# Nginx学习笔记—HTTP反向代理

`Nginx`支持的反向代理可以分为两类：

- 四层反向代理：作用于传输层，下游连接可以为TCP、UDP，上游连接类型和下游连接相同。
- 七层反向代理：作用应用层，下游连接为HTTP请求，上游连接可以为其他类型。

![支持多种协议的反向代理]()

`ngx_http_proxy_module`模块用于反向代理`HTTP/HTTPS`协议。该模块默认编入Nginx，可以使用`--without-http_proxy_module`移除。`proxy`模块中，整个HTTP反向代理流程如下：

![HTTP反向代理流程]()

`proxy`模块工作于`CONTENT`阶段(`CONTENT`阶段之前只处理了请求的header部分)。为了避免处理请求的头部和body时占用上游服务资源，`proxy`模块会在处理好请求后，才与上游服务建立连接。

## 配置反向代理

`proxy`模块提供了很多命令用于处理请求和响应，其中最关键的指令是：

- `proxy_pass URL`：指定上游服务的`URL`。
  - `URL`必须以`http://`或`https://`开头，后面可以跟域名、`IP`、`unix socket`或`upstream`名称。
  - `URL`中可以包含`URI`，携带`URI`时，转发时会将location匹配部分替换为该`URI`；不携带，则直接转发给上游服务(采用正则或@名字时)。
  - `URL`中可以携带参数。

```nginx
location /a {
	proxy_pass http://proxy.com;# 访问时/a/b/c转发的url为http://proxy.com/a/b/c
    proxy_pass http://proxy.com/www;# 访问时/a/b/c转发的url为http://proxy.com/www/b/c
}
```

## 请求处理

#### 修改请求行

- `proxy_method method`：修改请求方法。
- `proxy_http_version 1.0 | 1.1`：修改HTTP协议版本，默认`1.0`。

#### 修改请求头部

- `proxy_set_header field value`：修改`header`中对应字段值，变量值为空时，不会发送该字段，默认修改`Host $proxy_host`和`Connection close`。
- `proxy_pass_request_headers on | off`：是否转发用户请求的header，默认为`on`。

#### 包体发送

- `proxy_pass_request_body on | off`：是否转发用户请求的`body`，默认为`on`。
- `proxy_set_body value`：构造发往上游的`body`。

#### 包体接收

- `proxy_request_buffering on | off`：决定对`body`采用先收再转发还是边收边转发，默认为`on`。

  - `on`适用于网速慢、上游并发处理能力低、高吞吐量场景。
  - `off`适用于低延时的场景，该设置能降低nginx读写磁盘的损耗(body可能会存入文件)。一旦开始发送内存，`proxy_next_upstream`指令失效。

- `client_body_buffer_size size`：设置接收`body`的缓存区大小。默认值为`8K|16K`。

  - 如果接收`header`时已经接收完`body`，则不分配。
  - 如果`body`长度小于`size`，则按需分配。
  - 如果`body`长度大于`size`，只分配`size`大小的缓存区，用于`body`处理时的缓存区。
    - 边收边转发：缓存区满后，立即将缓存区数据发往上游服务。
    - 先收先转发：缓存区满后，存入临时文件。

- `client_body_in_single_buffer on|off`：将body存放在缓存中，默认为`off`。只适用于`body`比较小的场景，设置为`on`后，可以通过变量`$request_body`获取`body`。

- `client_max_body_size size`：设置`body`的最大长度，只有`Content-Length`超过该值时，返回`413`响应。默认值为`1m`。

- `client_body_temp_path path [level1 [level2 [level3]]]`：设置缓存`body`的临时文件存储位置，临时默认值为`client_body_temp`。`level`为数字`1|2`，表示该级目标名的长度，最多可以指定三级子目录。设置子目录的原因是避免目录下文件很多时，导致检索速度慢。

  ```nginx
  # 临时文件存放在client_body_temp下，有三级子目录，每级子目录名长为2位
  # 例如client_body_temp/88/46/65/1254654688
  client_body_temp_path client_body_temp 2 2 2;
  ```

- `client_body_in_file_only on | clean | off`：设置`body`是否必须存放在文件中，默认值为`off`。

  - `on`：一直存放在文件中，通常用于定位问题。
  - `clear`：`body`必须存放在文件中，处理完请求后，清理文件。
  - `off`：如果`body`小于`client_body_buffer_size`指定的`size`，不会存入文件。

- `client_body_timeout time`：两次包体接受的最大间隔时间，超时返回408响应，默认值为60S。

## 上游建立连接

- `proxy_connect_timeout time`：设置TCP握手超时时间，超时则返回502响应，默认值60S。
- `proxy_next_upstream http_502`：遇到指定错误码时，切换上游服务器，默认值为`error timeout`。
- `proxy_socket_keepalive on|off`：是否打开TCP层`keepalive`，打开后，会通过探测包探测对端是否存活，默认值为`off`。该功能会关闭无效连接，释放资源。
- `keepalive connections`：设置并发连接数。
- `keepalive_requests number`：设置单个连接能执行的最大请求数，默认值100。
- ` proxy_bind address [transparent]|off`：修改TCP四元组中的源IP，如果指定的IP地址不是本地IP地址，需要使用`transparent`参数，通常用于IP透传(保证worker进程有root权限)。
- `proxy_ignore_client_abort on|off`：客户端关闭连接时，Nginx是否关闭与上游的连接，默认值`off`，关闭Nginx和上游的连接。
- `proxy_send_timeout time`：设置请求发送超时，默认60S。

## 上游响应接收

- `body`接收
  - ` proxy_buffer_size size`：限制上游响应的`header`的尺寸，如果`header`过大，会在`error.log`中记录`error.logupstream sent too big header `。默认值为`4K|8K`。
  - `proxy_buffering on|off`：对`body`采取先接收完再处理还是采用边收边发，默认值为`on`，先接收完再处理。如果上游响应中存在`X-Accel-Buffering`头部时，`yes`表示必须先接收完再处理，只有Nginx能识别该头部。
  - `proxy_buffers number size`：指定`body`的缓存区大小，如果使用缓存能存储`body`，则不需暂存到磁盘，默认值`8 4k|8k`。
  - `proxy_max_temp_file_size size`：临时文件的最大值，默认1024M。
  - `proxy_temp_file_write_size size;`：每次往磁盘写入的字节数，默认值`8K|16K`。
  - `proxy_temp_path path [level1 [level2 [level3]]]`：临时文件的存储位置，默认值`proxy_temp`。
- 及时响应
  - `proxy_busy_buffers_size size`：缓存时，先向客户端转发一定数据，默认值`8K|16K`。
- 接收上游响应速度
  - `proxy_read_timeout time;`：两次TCP读取的超时间隔，默认值`60S`。
  - `proxy_limit_rate rate`：限制读取上游响应的速度，默认为`0`，没有限制；

- `body`持久化
  - `proxy_store_access users:permissions`：设置临时文件转存后的权限，默认为`user:rw`，可以设置为`user:rw group:rw all:rw`。
  - `proxy_store on | off | string`：设置临时文件转存目录，默认为`root`指定。

## 响应头部处理

上游响应返回后，会被过滤模块依次进行处理，因此上游返回的响应会影响到Nginx返回给客户端的响应。Nginx提供了几条指令用于处理上游的响应。

- `proxy_ignore_headers field`：禁用改变Nginx行为的头部。
  - `X-Accel-Redirect`：上游指定在Nginx内部重定向，控制请求执行。
  - `X-Accel-Limit-Rate`：上游限制发往客户端的速度。
  - `X-Accel-Buffering`：上游控制是否缓存上游的常用。
  - `X-Accel-Charset`：上游控制`Content-Type`中的`charset`。
  - 缓存相关
    - `X-Accel-Expires`：设置响应在Nginx中的缓存时间，单位为秒。
    - `Expires`：控制Nginx缓存时间。
    - `Cache-Control`：控制Nginx缓存时间。
    - `Set-Cookie`：响应中出现`Set-Cookie`则不缓存。
    - `Vary`：响应中出现`Vary:*`，则不缓存
- `proxy_hide_header field`：设置不向客户端转发的字段。
  - `Date`：由`ngx_http_header_filter_module`填写，发送响应头部时的时间。
  - `Server`：由`ngx_http_header_filter_module`填写，nginx版本号。
  - `X-Pad`：`Apache`避免浏览器Bug生成的头部，默认忽略。
  - `X-Accel-`：用于控制nginx行为的响应，默认不转发。
- `proxy_pass_header field`：允许被`proxy_hide_header`的头部字段，转发给客户端。
- `proxy_cookie_domain off|domain replacement`：修改`Set-Cookie`中的`domain`，默认值为`off`。
- `proxy_cookie_path off|path replacement`：修改`Set-Cookie`中的`path`，默认值为`off`。
- `proxy_redirect default|off|redirect replacement`：替换上游服务响应中的`Location`，默认值为`default`。

## 上游错误响应处理

- `proxy_next_upstream error_type`：选择下一个上游服务，前提是没有向客户端发送任何内容，只有在转发响应之前才能生效。默认值`error timeout`。

  - `error`：与上游发生网络错误(建立连接、读取响应)

  - `timeout`：超时

  - `invalid_header`：`header`不合法

  - `non_idempotent`：非幂等操作(`POST`、`LOCK`、`PATCH`)

  - `http_响应码`：处理响应码，选取新的upstream

  - `off`：关闭

- `proxy_next_upstream_timeout time`：超时时间，默认值为0.

- `proxy_next_upstream_tries number`：重试次数，默认值为0。

- `proxy_intercept_errors on|off`：当上游响应的响应码大于等于300时，将响应返回客户端还是交给error_page指令处理。

## TLS认证

`ngx_http_ssl_module`模块负责对下游执行TLS认证，`ssl`模块依赖`OpenSSL`库。该模块默认不编入Nginx，使用`--with-http_ssl_module`加入。

#### 指令

- `proxy_ssl_server_name on|off`：是否启用`SNI`。
- `proxy_ssl_name name`：配置`SNI`服务器名称，默认为`$proxy_host`。

- 提供给下游的证书
  - `ssl_certificate file`：
  - `ssl_certificate_key file`：
- 验证下游的证书
  - `ssl_verify_client on | off | optional | optional_no_ca`：是否验证下游的证书，默认为`off`。
    - `optional`：可选。
    - `optional_no_ca`：下游提供的证书不强制要求时可信CA前面。
  - `ssl_client_certificate file`：下游证书签发CA的证书。
- 提供给上游的证书
  - `proxy_ssl_certificate file`：
  - `proxy_ssl_certificate_key file`：
- 是否验证上游的证书
  - `proxy_ssl_verify on | off`：是否验证上游的证书，默认为`off`。
  - `proxy_ssl_trusted_certificate file`：上游证书签发CA的证书。

## 实验

![双向认证]()

```nginx

```

实验结果：

```bash
# 根证书
# 创建CA私钥
openssl genrsa -out ca.key 2048
# 创建CA公钥
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt

# 证书签发
# 创建上游私钥
openssl genrsa -out upstream.pem 1024
openssl rsa -in upstream.pem -out upstream.key
# 生成签发请求
openssl req -new -key upstream.pem -out upstream.csr
# 使用CA证书进行签发证书
openssl x509 -req -sha256 -in upstream.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 3650 -out upstream.crt
# 验证签发证书是否正确
openssl verify -CAfile ca.crt upstream.crt

# 创建下游证书
# 创建上游私钥
openssl genrsa -out downstream.pem 1024
openssl rsa -in downstream.pem -out downstream.key
# 生成签发请求
openssl req -new -key downstream.pem -out downstream.csr
# 使用CA证书进行签发证书
openssl x509 -req -sha256 -in downstream.csr -CA ca.crt -CAkey ca.key -CAcreateserial -days 3650 -out downstream.crt
# 验证签发证书是否正确
openssl verify -CAfile ca.crt downstream.crt
```

