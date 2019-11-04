## 过滤模块

HTTP过滤模块是对响应内容进行加工，其作用于`CONTENT`和`LOG`阶段之间。

![过滤模块的位置]()

过滤时会先对header进行过滤，然后再对body进行过滤，具体的过滤模块执行顺序由`ngx_modules.c`中指定。过滤模块中有四个模块比较重要：

- `ngx_http_copy_filter_module`：复制包体的内容，`sendfile`指令采用零拷贝技术，将文件内容不经过用户态内容(nginx)，直接发给用户。`gzip`模块必须在`copy_filter`之后，因为`gzip`必须对内存中的内容进行压缩，所以打开`gzip`后，会让`sendfile`失效，`copy_filter`会拷贝一份，给后续模块使用。
- `ngx_http_postpone_filter_module`：处理子请求。
- `ngx_http_header_filter_module`：构造响应头部。
- `ngx_http_write_filter_module`：负责将内存中的内容发送给客户端。

### sub模块

#### 理论

`ngx_http_sub_filter_module`模块能将响应中指定的字符串替换为新的字符串。该模块默认没有编入nginx，可以通过`--with-http_sub_module`启用。

该模块提供了四个指令：

- `sub_filter string replacement`：指定替换内容，忽略大小写。
- `sub_filter_last_modified on | off`：是否返回`Last-Modified`头部字段，默认为`off`。
- `sub_filter_once on | off`：是否只替换一次，默认为`on`。
- `sub_filter_types mime-type`：指定哪些响应类型执行该操作，设置为`*`，则对所有的响应都启动替换，默认为`text/html`。

#### 实验

```nginx
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
		listen 80;
		server_name fangjie.site;
		error_log logs/myerror.log notice;
		root html/;
		location /1{
			sub_filter one 1;
            sub_filter_once on;
        }
        location /2{
            sub_filter two 2;
            sub_filter_once off;
            sub_filter_last_modified on;
        }
	}
}
```

实验结果：

![]()

### addition模块

#### 理论

`ngx_http_addition_filter_module`模块能在响应前后添加子请求的响应内容。该模块默认没有编入nginx，可以通过`--with-http_addition_module`启用。

该模块提供三条指令：

- `add_before_body uri`：在body之前添加内容，新的内容是uri的响应。
- `add_after_body uri`：在body之后添加内容，新的内容是uri的响应。
- `addition_types mime-type`：指定哪些响应类型执行该操作，设置为`*`，则对所有的响应都启动替换，默认为`text/html`。

#### 实验

```nginx
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
		listen 80;
		server_name fangjie.site;
		error_log logs/myerror.log notice;
		root html/;
		location /{
            add_before_body /before;
            add_after_body /after;
        }
        location /before{
           	return 200 'before';
        }
        location /after{
			return 200 'after';
        }
	}
}
```

实验结果：

![]()

## 变量

Nginx的变量分为提供变量的模块和使用变量的模块。Nginx启动时，会调用模块的`preconfiguration`方法，该方法会在模块读取`nginx.conf`之前，定义一个映射`变量名和解析出该变量的方法`，通过该方法，可以与调用者解耦，专注于自己的职责。使用变量的模块在处理请求时，通过变量名找到对应的方法，获取变量值。

Nginx的变量有两大特性：

- 惰性求值：只有使用时，才会计算变量值。
- 动态变化：变量值可以一直变化，其值为使用时刻的值。

为了存储这些变量信息，Nginx提供了一个哈希表：

- `variables_hash_bucket_size size `：每个映射的最大容量，默认为64。
- `variables_hash_max_size size`：映射的最大个数，默认为1024。

### HTTP请求相关的变量

- `arg_参数名`：获取URL中参数的值。
- `args`：获取全部URL参数。
- `query_string`：同`args`。
- `is_args`：URL中是否有参数，有参数返回`?`，没有返回空。
- `content_length`：获取请求中`Content-Length`头部的值。
- `content_type`：获取请求中`Content-Type`头部的值。
- `uri`：获取请求的URI，不包含参数。
- `document_uri`：同`uri`。
- `request_uri`：请求的URL，包含参数。
- `scheme`：协议名。
- `request_method`：请求方法。
- `request_length`：请求的大小。
- `remote_user`：HTTP Basic Authentication协议传入的用户名。
- `request_body_file`：临时存放请求包体的文件，包体很小时，不会存文件。
- `request_body`：请求中的包体，只有使用反向代理，且设置内存暂存包体时，才能获取。
- `request`：获取请求行。
- `host`
  - 先从请求行中获取。
  - 如果头部含有`Host`，则使用`Host`。
  - 都匹配失败，则取匹配上的server_name。
- 头部字段：
  - 通用：`http_头部字段名`
  - 微小处理：
    - `http_host`
    - `http_user_agent`
    - `http_referer`
    - `http_via`
    - `http_x_forwarded_for`
    - `http_cookie`

### HTTP响应相关的变量

- `body_bytes_sent`：响应中包体长度。
- `bytes_sent`：整个响应的长度。
- `status`：响应码
- `send_trailer_name`：获取响应结尾的内容。
- 头部字段
  - 通用：`sent_http_头部字段名`
  - 特殊处理：
    - `sent_http_content_type`
    - `sent_http_content_length` 
    - `sent_http_location`
    - `sent_http_last_modified`
    - `sent_http_connection`
    - `sent_http_keep_alive`
    - `sent_http_transfer_encoding`
    - `sent_http_cache_control`
    - `sent_http_link`

### TCP相关的变量

- `binary_remote_addr`：客户端IP地址的二进制格式，IPv4消耗4字节。
- `connection`：连接序号。
- `connection_requests`：连接上执行过的请求数。
- `remote_addr`：客户端地址，字符串格式。
- `remorte_port`：客户端端口。
- `proxy_protocol_addr`：获取代理协议`proxy_protocol`中的地址，没有使用则返回空。
- `proxy_protocol_port`：获取代理协议`proxy_protocol`中的端口，没有使用则返回空。
- `server_addr`：服务器地址。
- `server_port`：服务器端口号。
- `TCP_INFO`：tcp内核参数。
- `server_protocol`：服务器协议版本，如`HTTP/1.1`。

### Nginx处理请求产生的变量

- `request_time`：请求处理耗时，单位为秒，精度为毫秒。
- `server_name`：匹配上请求的`server_name`。
- `https`：是否是`https`，是为`on`，否为空。
- `request_completion`：请求处理完毕返回OK，否则返回空。
- `request_id`：请求标识id，长度为16进制，随机生成。
- `request_filename`：待访问的文件的完整路径。
- `document_root`：文件所在文件夹的路径。
- `realpath_root`：真实路径。
- `limit_rate`：返回响应时的速度上限，单位为每秒字节数。

### Nginx系统变量

- `time_local`：本地时间标准的当前时间。
- `time_iso8601`：ISO 8601标准的当前时间。
- `nginx_version`：Nginx版本号。
- `pid`：`worker`进程的pid。
- `pipe`：是否使用了管道，使用则返回`p`，否则返回`.`。
- `hostname`：主机名

