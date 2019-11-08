# Nginx学习笔记—缓存

为了尽可能快的获取资源，通常都会采取缓存策略。缓存一般分为两大类：

- 客户端缓存：资源缓存在客户端本地。
  - 本地缓存有效时，使用缓存，没有网络开销。
  - 本地缓存失效，通过`GET`请求获取资源时，服务器会判断客户端缓存是否失效，如果没有失效，则会返回`304 Not Modified`，将网络开销最小化。
  - 客户端缓存只能提升一个用户的体验。
- 服务器缓存：通常采用Nginx进行缓存。
  - Nginx收到请求后，会先判断客户端缓存是否有效，若有效，返回`304`响应。
  - 检查自身缓存缓存是否有效，若有效，返回缓存的资源；无效则访问上游服务。
  - 通过服务器缓存，能有效降低上游服务的负载，而且能提升所有用户的体验。

采用服务器缓存，用户仍然需要网络消耗，通常采用客户端和服务器缓存并用。

## 客户端缓存策略

![客户端缓存流程]()

HTTP协议提供了两个响应头部字段，用于控制客户端缓存过期时间：

- `Expires`：缓存过期的绝对时间，如`Thu, 31 Dec 2037 23:55:55 GMT`。
- `Cache-Control`：缓存过期的相对时间，用于避免服务器和客户端时间不同，如`Cache-Control:max-age=60`，单位为秒。

如果本地缓存已经到期，需要回服务器判断本地缓存需要更新，HTTP也提供了两个，用于传递资源的状态：

- `ETag`：记录资源的版本号，如果资源已经更新，则资源的`ETag`和缓存的`Etag`不相同。`ETag`分为两种：
  - 弱`ETag`：以`W/`开头，只有当语义发生改变，才会变化。如`html`文件中删除无效空行不会引起`ETag`变化。
  - 强`ETag`：要求字节级别相同。
- `Last-Modifiled`：记录资源的修改时间，精度为秒。
  - 如果出现一秒内出现多次资源修改，无法区分。
  - 资源定期更新时，只修改资源时间，也会引发重新获取资源。

## ETag

`HTTP`协议中提供了两个头部字段用于和`ETag`相关的条件请求：

- `If-None-Match：ETag-filed `
- `If-Match: ETag-filed`

`If-None-Match `搭配`GET`和`HEAD`请求方法使用时，只有当服务器上资源`ETag`值与`ETag-Filed`不相等时，才返回请求的资源，响应码为`200`；如果存在`ETag`值相等的资源，返回`304 Not Modified`。针对`PUT`、`POST`、`DELETE`等会改变服务器资源状态的方法，只有确认没有资源的`ETag`与之相等时，才处理请求(避免覆盖之前的更新)，否则返回`412 Precondition Failed`响应。`304 Not Modified`响应中会包含`Cache-Control`、`Content-Location`、`Date`、`ETag`、`Expires`、`Vary`头部字段，更新客户端的缓存信息。`If-None-Match`常用场景有：

- 搭配GET请求，更新指定资源。
- `If-None-Match:*`搭配`PUT`、`POST`操作时，用于生成不知道是否存在的文件，如果URL指定的资源存在，返回`412 Precondition Failed`。

`If-Match`搭配`GET`和`HEAD`请求方法使用时，只有当服务器上资源的`ETag`值与之相等时，才返回请求的资源，响应码为`200`。针对`PUT`、`POST`、`DELETE`这类方法，只有满足条件时，才修改资源，避免覆盖之前的更新。当条件不满足时，返回`412 Precondition Failed`。`If-Match`常用场景有：

- 搭配`GET`请求，通过`Range`字段，保证前后两次范围请求是针对统一资源的。条件不满足时，返回`416 Range Not Satisfiable`响应。
- 搭配`PUT`、`POST`请求，避免更新丢失。

## Last-Modified

针对`Last-Modified`，`HTTP`也提供了两个头部字段，处理条件请求：

- `If-Modified-Since:Last-Modifiled-filed `
- `If-Unmodified-Since：Last-Modifiled-filed`

`If-Modified-Since`同`If-None-Match`，但是`If-Modified-Since`字段只能用于`GET`或`HEAD`请求，只有在资源在给定的日期之后发生更新，才返回请求的资源，响应码为`200`；如果没有更新，则返回`304 Not Modified`。该字段优先级低于`If-None-Match`。

`If-Unmodified-Since`类似`If-Match`，搭配`GET`请求时，只有当资源在指定时间后没有发生改变，服务器才返回请求的资源。搭配`POST`等方式时，如果资源在指定的时间后发生了改变，返回`412 Precondition Failed`响应。`If-Unmodified-Since`常用场景有：

- 搭配`GET`请求和`If-Range`字段，确保新的请求片段来自同一文档。
- 搭配`POST`、`PUT`请求，避免更新丢失。

## Nginx缓存策略

### 理论

`Nginx`收到客户端的请求后，采用如下缓存策略：

`if_match`流程有问题，不等于返回412，等于返回200响应。

![nginx处理客户端条件请求流程]()

- `etag on|off`：是否启用`ETag`字段。`ETag`的生成规则为`"%x-%x"`，第一个参数为`last_modified_time`，第二个参数为`Content_length_n`。
- `expires off|max|epoch|time`：有`ngx_http_headers_module`模块提供，控制客户端缓存如何过期，默认值为`off`。
  - `off`：不添加`Expires`或`Cache-Control`字段。
  - `max`：永久有效，最大值为10年。
    - `Expires:Thu, 31 Dec 2037 23:55:55 GMT`。
    - `Cache-Control:max-age=315360000`。
  - `epoch`：不使用缓存。
    - `Expires: Thu, 01 Jan 1970 00:00:01 GMT`
    - `Cache-Control: no-cache`
  - 具体时间，默认单位为秒。
    - 正数：设置`Cache-Control`，计算`Expire`相对于(`nginx`的时间)。
    - 负数：`Cache-Control: no-cache`，计算`Expires`。
    - 具体时间，如`@18h30m`，表示下午18点30分过期，如果当前时间未超过指定时间，`Expire`为当天的下午18点30分；否则为第二天的下午18点30分。根据`Expire`计算`Cache-Control`。
- `if_modified_since off|exact|before`：设置如何处理`If-Modified-Since`头部字段。
  - `off`：忽略`If-Modified-Since`头部字段。
  - `exact`：完全匹配。
  - `before`：如果`If-Modified-Since`大于资源的`last-modified`时，返回`304`。

### 实验

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
		listen 8000;
		server_name localhost;
		error_log  logs/error.log  debug;
		default_type text/plain;
		etag on;
		expires 3600;
		location / {
		
		}
		location /off {
			if_modified_since off;
		}
		location /exact { 
			if_modified_since exact;
		}
		location /before {
			if_modified_since before;
		}
	}
}
```

实验结果：

```bash
# 获取原始信息
[root@upgrade-71132 nginx]# curl 127.0.0.1:80/ -I
HTTP/1.1 200 OK
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 06:50:22 GMT
Content-Type: text/html
Content-Length: 612
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 07:50:22 GMT
Cache-Control: max-age=3600
Accept-Ranges: bytes

# last-modified小于If-Unmodified-Since，预期返回200
[root@upgrade-71132 nginx]# curl -H "If-Unmodified-Since:Tue, 13 Aug 2019 07:57:44 GMT" 127.0.0.1/ -I
HTTP/1.1 200 OK
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 06:59:35 GMT
Content-Type: text/html
Content-Length: 612
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 07:59:35 GMT
Cache-Control: max-age=3600
Accept-Ranges: bytes

# last-modified大于If-Unmodified-Since，预期返回412
# 大于表示服务器上的资源版本比客户端缓存的资源新，如果正常处理，则会出现更新被覆盖
[root@upgrade-71132 nginx]# curl -H "If-Unmodified-Since:Tue, 13 Aug 2019 07:41:44 GMT" 127.0.0.1/ -I
HTTP/1.1 412 Precondition Failed
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 07:01:33 GMT
Content-Type: text/html
Content-Length: 173
Connection: keep-alive

# If-Unmodified-Since等于last-modified，预期返回200
[root@upgrade-71132 nginx]# curl -H "If-Unmodified-Since:Tue, 13 Aug 2019 07:51:44 GMT" 127.0.0.1/ -I
HTTP/1.1 200 OK
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 07:02:22 GMT
Content-Type: text/html
Content-Length: 612
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 08:02:22 GMT
Cache-Control: max-age=3600
Accept-Ranges: bytes

# If-Match 大于ETag，预期返回412
[root@upgrade-71132 nginx]# curl -H "If-Match:5d526c10-364" 127.0.0.1/ -I
HTTP/1.1 412 Precondition Failed
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 07:08:23 GMT
Content-Type: text/html
Content-Length: 173
Connection: keep-alive

# If-Match 小于ETag，预期返回412
[root@upgrade-71132 nginx]# curl -H "If-Match:5d526c10-164" 127.0.0.1/ -I
HTTP/1.1 412 Precondition Failed
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 07:09:02 GMT
Content-Type: text/html
Content-Length: 173
Connection: keep-alive

# If-Match 等于ETag ，预期返回200
[root@upgrade-71132 nginx]# curl -H 'If-Match:"5d526c10-264"' 127.0.0.1/ -I
HTTP/1.1 200 OK
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 07:15:27 GMT
Content-Type: text/html
Content-Length: 612
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 08:15:27 GMT
Cache-Control: max-age=3600
Accept-Ranges: bytes


# off ,预期返回200
[root@upgrade-71132 nginx]# curl -H "If-Modified-Since:Tue, 13 Aug 2019 07:51:44 GMT" 127.0.0.1/off/ -I
HTTP/1.1 200 OK
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 07:17:27 GMT
Content-Type: text/html
Content-Length: 612
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 08:17:27 GMT
Cache-Control: max-age=3600
Accept-Ranges: bytes

# off ,预期返回200
[root@upgrade-71132 nginx]# curl -H "If-Modified-Since:Tue, 13 Aug 2019 07:51:44 GMT" 127.0.0.1/off/ -I
HTTP/1.1 200 OK
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 07:19:42 GMT
Content-Type: text/html
Content-Length: 612
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 08:19:42 GMT
Cache-Control: max-age=3600
Accept-Ranges: bytes

# exact，预期返回200
[root@upgrade-71132 nginx]# curl -H "If-Modified-Since:Tue, 13 Aug 2019 07:11:44 GMT" 127.0.0.1/exact/ -I
HTTP/1.1 200 OK
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 07:20:14 GMT
Content-Type: text/html
Content-Length: 612
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 08:20:14 GMT
Cache-Control: max-age=3600
Accept-Ranges: bytes

# exact，预期返回304
[root@upgrade-71132 nginx]# curl -H "If-Modified-Since:Tue, 13 Aug 2019 07:51:44 GMT" 127.0.0.1/exact/ -I
HTTP/1.1 304 Not Modified
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 07:24:58 GMT
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 08:24:58 GMT
Cache-Control: max-age=3600

# before，预期返回200
[root@upgrade-71132 nginx]# curl -H "If-Modified-Since:Tue, 13 Aug 2019 07:41:44 GMT" 127.0.0.1/before/ -I
HTTP/1.1 200 OK
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 07:25:38 GMT
Content-Type: text/html
Content-Length: 612
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 08:25:38 GMT
Cache-Control: max-age=3600
Accept-Ranges: bytes

# before，预期返回304
[root@upgrade-71132 nginx]# curl -H "If-Modified-Since:Tue, 13 Aug 2019 07:58:44 GMT" 127.0.0.1:8000/before/ -I
HTTP/1.1 304 Not Modified
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 07:26:11 GMT
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 08:26:11 GMT
Cache-Control: max-age=3600

# 测试带if_modified_sicnce指令，预期返回304
[root@upgrade-71132 nginx]# curl -H "If-Modified-Since:Tue, 13 Aug 2019 07:58:44 GMT" -H 'If-None-Match:"5d526c10-264"' 127.0.0.1/before/ -I
HTTP/1.1 304 Not Modified
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 12:13:07 GMT
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 13:13:07 GMT
Cache-Control: max-age=3600

# 测试带if_modified_sicnce指令，预期返回200
[root@upgrade-71132 nginx]# curl -H "If-Modified-Since:Tue, 13 Aug 2019 07:58:44 GMT" -H 'If-None-Match:"5d526c10-364"' 127.0.0.1/before/ -I
HTTP/1.1 200 OK
Server: nginx/1.17.5
Date: Thu, 07 Nov 2019 12:13:15 GMT
Content-Type: text/html
Content-Length: 612
Last-Modified: Tue, 13 Aug 2019 07:51:44 GMT
Connection: keep-alive
ETag: "5d526c10-264"
Expires: Thu, 07 Nov 2019 13:13:15 GMT
Cache-Control: max-age=3600
Accept-Ranges: bytes
```

## 请求回源

Nginx还提供缓存上游服务的能力，主要有`ngx_http_proxy_module`模块提供。

![缓存流程，是否回源]()

### 缓存使用

- `proxy_cache_path`：配置缓存使用的共享内存信息。	

  - `path`：指定缓存文件存放位置。
  - `levels`：缓存目录层级，最多三级，每层目录名字长度为1或2。

  - `use_temp_path`：
    - `on`：缓存临时文件存放在`proxy_temp_path`指定的目录，固化时拷贝到`path`中。
    - `off`：直接使用`path`存放临时文件。
  - `keys_zone`：指定共享的`name`和`size`，1MB大概存放8000个key。
  - `inactive`：超过`inactive`，未被访问的资源将被淘汰，默认10分钟。
  - `max_size`： 设置最大的缓存文件大小，超出后由`cache manager`进程按`LRU`淘汰。
  - `manager_files`： 控制一次淘汰流程，最多能淘汰多少个文件，默认100个。
  - `manager_sleep`：控制两次淘汰的间隔时间，默认200毫秒。
  - `manager_threshold`：执行一次淘汰最大耗时，默认50毫秒。避免淘汰操作耗时过长。
  - `loader_files`：控制`cache loader`进程加载缓存文件到共享内存时，一个流程，加载文件的最大个数。
  - `loader_sleep`：两次加载流程的间隔时间，默认200毫秒。
  - `loader_threshold`：执行一次加载流程的最大耗时，默认50毫秒。

  ```nginx
  # 缓存文件存放位置：/data/nginx/cache
  # 缓存文件/data/nginx/cache/c/29/b7f54b2df7773722d382f4809d65029c
  proxy_cache_path /data/nginx/cache levels=1:2 keys_zone=one:10m;
  ```

- `proxy_cache zone | off`：指定缓存使用的共享内存，默认值为`off`。

- `proxy_cache_key string`：设置缓存的key，默认值`$scheme$proxy_host$request_uri`。

### 其他

- `proxy_cache_bypass string`：当条件满足时，不使用缓存。
- `proxy_cache_convert_head on | off`：是否将`HEAD`方法转换为`GET`，默认为`on`。
- `proxy_cache_methods method`：指定使用缓存的请求方法，默认值为`GET HEAD`。

### 变量

变量`$upstream_cache_status`，获取缓存状态。

- `MISS`：未命中缓存
- `HIT`：命中缓存。
- `EXPIRED`：缓存已经过期(例：`proxy_cache_valid`指定时间为`10m`，上游返回的响应`Cache-Control:max-age=300`)。
- `STALE`：陈旧的缓存命中。
- `UPDATING`：更新陈旧缓存中。
- `REVALIDATED`：Nginx验证陈旧缓存有效。
- `BYPASS`：从原始服务器获得的响应。

### 实验

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
	
	proxy_cache_path /data/nginx/tmpcache levels=2:2 keys_zone=two:10m loader_threshold=300 
        loader_files=200 max_size=200m inactive=1m;

	server {
		listen 80;
		server_name localhost;
		root html/;
		error_log logs/cacherr.log debug;
		# 验证hit、miss
		location / {
			proxy_cache two;
			# 缓存200 响应
			proxy_cache_valid 200 30s;
			add_header X-Cache-Status $upstream_cache_status;
			proxy_pass http://localhost:8000;
		}
		# 验证上游通过X-Accel-Expires控制缓存
		location /expires {
			proxy_cache two;
			proxy_cache_valid 200 1m;
			add_header X-Cache-Status $upstream_cache_status;
			proxy_pass http://localhost:8000/expires;
		}
		location /cookie {
			proxy_cache two;
			proxy_cache_valid 200 1m;
			add_header X-Cache-Status $upstream_cache_status;
			proxy_pass http://localhost:8000/cookie;
		}
		location /vary {
			proxy_cache two;
			proxy_cache_valid 200 1m;
			add_header X-Cache-Status $upstream_cache_status;
			proxy_pass http://localhost:8000/vary;
		}
		
	}
}

worker_processes  1;
events {
    worker_connections  1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
	
	proxy_cache_path /data/nginx/tmpcache levels=2:2 keys_zone=two:10m loader_threshold=300 
        loader_files=200 max_size=200m inactive=1m;

	server {
		listen 80;
		server_name localhost;
		root html/;
		error_log logs/cacherr.log debug;
		# 验证hit、miss
		location / {
		
		}
		location /expires {
			add_header X-Accel-Expires 3;
		}
		location /cookie {
			add_header Set-Cookie user_header_token=$http_user_header_token;;
		}
		location /vary {
			add_header Vary *;
		}
	}
}
```

## 缓存响应

![响应缓存]()

- `proxy_no_cache string`：当条件满足时，不缓存该响应。
- ` proxy_cache_valid [code ...] time`：指定缓存的响应类型及缓存时间。
  - 不同的响应设置不同的缓存时间：`code 404 5m`。
  - 只填时间：只缓存`200`、`301`、`302`。
  - 上游响应头部控制缓存时间：
    - `X-Accel-Expires`：单位为秒，如果为`0`则禁止缓存，可通过`@`设置为具体时间点。
    - 不缓存包含`Set-Cookie`、`Vary:*`的响应，`Vary`表明响应生成时，所依据的头部信息。

## 缓存失效

当缓存中的资源失效后，为了避免缓存过期时，大量请求同时回源，上游服务因为压力过大出现崩溃(缓存击穿)。面对缓存击穿，常见的两种方式是：

- 合并回源请求：通过第一个请求回源，其他请求等待响应或超时。
- 减少回源请求：通过第一个请求回源，其他请求使用旧缓存。

### 合并回源请求

- `proxy_cache_lock on | off`：是否启用合并回源请求，默认为`off`。
- `proxy_cache_lock_timeout time`：上一个请求超时后，剩余请求全部回源，不缓存响应，默认为`5s`。
- `proxy_cache_lock_age time`：上一个请求超时后，只放行一个请求，默认为`5s`。

### 减少回源请求

- `proxy_cache_use_stale`：，默认为`off`。
  - `updating`：缓存过期时，第一个请求请求回源，其他请求使用旧缓存。
    - `Cache-Control: max-age=600, stale-while-revalidate=30`：缓存过期后，`30s`内`updating`设置有效，否则回源。
    - `Cache-Control: max-age=600, stale-if-error=1200 `：缓存过期后，如果在`1200s`内，上游服务出现错误，则使用缓存，否则回源。
  - `error`：和上游建立连接、发送请求、读取响应等操作出现错误时，使用缓存。
  - `timeout`：和上游建立连接、发送请求、读取响应等操作出现超时，使用缓存。
  - `http_(500|502|503|504|403|404|429)` ：缓存错误码的响应。

- `proxy_cache_background_update on|off`：采用子请求更新缓存，第一个请求也使用旧缓存，默认为`off`。
- `proxy_cache_revalidate on|off`：使用`If-Modified-Since`和`If-None-Match`来更新缓存，默认为`off`。

### 及时清理缓存

第三方模块[`ngx_cache_purge`](https://github.com/FRiCKLE/ngx_cache_purge)提供主动清理nginx缓存的方法，使用`--add-module`指令添加模块。`purge`模块收到`purge`请求后，会立刻删除缓存。

- `proxy_cache_purge on|off|<method> [from all|<ip> [.. <ip>]]`：打开`purge`，默认使用`purge`请求方法，可以设置请求方法和限制请求发送的`ip`。
- `proxy_cache_purge zone_name key`：指定从`zone_name`中删除`key`的缓存。

```nginx
location ~ /purge(/.*) {
    proxy_cache_purge two $scheme$1;
}
```

## slice模块

当客户端发起一个范围请求时，Nginx为了优化后续请求，会从上游获取整个资源，再响应客户端的范围请求。如果资源很大时，多个请求访问该资源，会导致严重的性能问题。这时有两种优化手段：

- 采用缓存，缓存该资源，但是第一个请求的耗时较长。
- 使用`slice`模块，分片缓存。

![slice模块运行流程]()

当缓存上游响应时，如果上游响应文件特别大，这是nginx处理性能较差(同时出现同一文件的多个请求时)，可以使用`http_slice_module`模块，通过range协议将大文件分解为多个小文件，更好的使用缓存为客户端的range协议服务，提升服务性能。slice模块默认没有编译进nginx中。`--with-http_slice_module`添加。

- `slice`：每片的大小，默认值为`0`。

![slice模块运行流程]()

```
slice 1m;# 不能太大，容易影响性能
proxy_cache_key $uri$is_args$args$slice_range;
proxy_set_header Range $slice_range;
prxy_cache_valid 200 206 1m;
```

## open_file_cache指令

- `open_file_cache offmax=N [inactive=time]`：最多在内存中缓存的文件个数，超过采用LRU，如果一个文件在inactive中未被访问，则移除。只针对单个worker进程。默认`off`。
- `open_file_cache_errors on|off`：是否缓存文件访问错误信息。默认`off`。
- `open_file_cache_min_uses`：留在缓存中的最少访问次数。默认为`1`。
- `open_file_cache_valid`：缓存信息刷新时间。默认60s。

缓存的内容有：

- 文件句柄
- 文件修改时间
- 文件大小
- 文件查询时的错误信息
- 目录是否存在

通过`strace -p pid`可以跟踪系统调用，`sendfile`通过零拷贝技术，文件不需要从磁盘读到用户态，再从用户态到内核态，再通过网卡发送。而是直接从磁盘读到内核态，发送到网卡上，使用了open和close，就不需要`sendfile`(`sendfile`不需要open和close)，nginx作为用户态，没有必要打开，这是优化关键点。通过`open_file_cache`，可以不使用open、close，减少了两次系统调用。
