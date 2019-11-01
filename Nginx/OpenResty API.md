# OpenResty API

## 原理和基本概念

![OpenResty 架构图]()

OpenResty中每个进程都有一个LuaJIT VM，同一个进程中的协程将共享该VM。Nginx通过epoll的事件驱动来处理请求，减少等待和空转。

在OpenResty中，Lua协程需要等待操作完成时，会先通过yield操作将自己挂起，然后在Nginx中注册回调，将CPU交给其他请求；操作完成后，Nginx通过`resume`唤醒协程，协程继续操作，整个操作是同步非阻塞的。

![协程切换流程]()

`ngx.sleep`这个Lua API的源码清晰的解释了该流程，源码位置https://github.com/openresty/lua-nginx-module/blob/master/src/ngx_http_lua_sleep.c。

```c
// 注册ngx.sleep
void ngx_http_lua_inject_sleep_api(lua_State *L)
{
    lua_pushcfunction(L, ngx_http_lua_ngx_sleep);
    lua_setfield(L, -2, "sleep");
}
// 具体实现，只包含主体
static int ngx_http_lua_ngx_sleep(lua_State *L)
{
    // 添加回调函数
    coctx->sleep.handler = ngx_http_lua_sleep_handler;
    // 添加计时器
    ngx_add_timer(&coctx->sleep, (ngx_msec_t) delay);
    //使用yield 挂起
    return lua_yield(L, 0);
}
// 回调函数，只包含主体
void ngx_http_lua_sleep_handler(ngx_event_t *ev)
{	
    if (ctx->entered_content_phase) {
    	// resume
        (void) ngx_http_lua_sleep_resume(r);
    } else {
        ctx->resume_handler = ngx_http_lua_sleep_resume;
        ngx_http_core_run_phases(r);
    }

    ngx_http_run_posted_requests(c);
}
```

OpenResty提供的API有上下文限制，使用时需要注意上下文。OpenResty中提供的API是同步非阻塞的，当请求需要等待某些操作完成时，将去处理其他请求。

### 变量和生命周期

在OpenResty中，除了`init_by_lua`和`init_worker_by_lua`两个阶段外，其他阶段都会有一个隔离的全局变量表，避免处理过程中污染其他请求。通常情况下应该避免全局变量，尽量使用局部变量。如果一定要使用全局变量，可以使用模块变量代替，并且最好保证只读，避免高并发出现race问题。同一个worker进程中，模块只会被VM加载一次，因此该进程中的所有请求将共享该模块。

针对跨阶段、需要进行读写的变量，需要在nginx配置文件中相应的阶段，进行定义。OpenResty提供了`ngx.ctx`来负责处理该问题。

```nginx
location /test {
    rewrite_by_lua_block{
        ngx.ctx.foo=76
    }
    content_by_lua_block{
        ngx.say(ngx.ctx.foo)
    }
}
```

`ngx.ctx`也存在自己的局限性：

- 使用`ngx.location.capture`创建的子请求，会有自己独立的 `ngx.ctx`。
- 使用`ngx.exec`创建的重定向，会新建`ngx.ctx`。

## API

学习OpenResty中的API，最佳学习方法是阅读官方文档和阅读测试案例。这里以`shdict get API`为例，`shareddict`由`lua-nginx-module`提供。

```nginx
 http {
    # 定义一块共享内存空间
 	lua_shared_dict dogs 10m;
    server{
        location /demo{
            content_by_lua_block{
                # 获取共享内存
                local dogs=ngx.shared.dogs
            	dogs:set('name','wangwang')
                local value,err=dogs:get('name')
                ngx.say(value)
            }
        }
    }
 }
```

- 哪些阶段不能使用共享内存的API？

  通过API的`context`确定API的作用范围。

- `get`什么情况下会返回多个值？

  通过文档可知，当有错误时将返回`nil`和错误描述。

- `get`函数的入参是什么类型？是否有长度限制？

  入参可以是数字和字符串，最大长度为65535。

## 修改测试

测试用例的位置在`t`目录下，其命名规律是`数字-功能名`。

```perl
=== TEST 1: string key, int value
--- http_config
    lua_shared_dict dogs 1m;
--- config
    location = /test {
        content_by_lua '
            local dogs = ngx.shared.dogs
            dogs:set("foo", 32)
            dogs:set("bah", 10502)
            local val = dogs:get("foo")
            ngx.say(val, " ", type(val))
            val = dogs:get("bah")
            ngx.say(val, " ", type(val))
        ';
    }
--- request
GET /test
--- response_body
32 number
10502 number
--- no_error_log
[error]
--- ONLY

# 最后一个---ONLY是只运行该用例
# 测试启动方法
prove t/043-shdict.t
```

## 分类

OpenResty是由Lua API驱动，提供了更多的灵活性和可编程性。OpenResty中的API可以分为：

- 处理请求和响应
- SSL相关
- shared dict
- cosocket
- 处理四层
- process和worker
- 获取Nginx变量与配置
- 字符串、时间等通用功能。

OpenResty的API主要由`lua-nginx-module`提供，也有部分有`lua-resty-core`提供(FFI形式)，如`ngx.ssl`、`ngx.base64`、`ngx.errlog`、`ngx.process`、`ngx.re.split`、`ngx.resp.add_header`、`ngx.balancer`、`ngx.semaphore`、`ngx.ocsp`等API。不在`lua-nginx-module`中的API，需要通过`require`引入才能使用。

```lua
local ngx_re=require "ngx.re"
local res,err=ngx_re.split('a,b,c,d',',',nil,{pos=5})
```

### 请求处理

`ngx.req.*`负责处理请求相关的API，由`lua-nginx-module`提供。HTTP请求报文由三部分组成：

- 请求行
- 请求头部
- 请求体

请求行中的信息可以通过`ngx.var.*`获取，如`scheme`、`request_method`、`uri`，。这些参数和Nginx的参数相对应，可以参考`ngx_http_core_module`中的变量。OpenResty从性能(ngx.var效率低)、程序友好(返回字符串)和灵活性考虑(ngx.var中大多数只读)考虑，还提供了一些专门的API。

#### 请求行

- `ngx.req.http_version`：返回数字格式的版本号。
- `ngx.req.get_method`：返回字符串形式的方法名，不能和`ngx`中的方法常量进行比较。
- `ngx.req.set_method`：修改当前请求方法，参数是内置的数字常量，如`ngx.HTTP_POST`(数字8)，get和set方法参数格式尽量一致。
- `ngx.req.set_uri`：改写uri。
- `ngx.req.set_uri_args`：改写args，jump参数用于控制是否继续匹配下一个`location`，功能类似nginx中`return`的`break`。

#### 请求头部

- `ngx.req.get_headers`：只返回前100个header，超过返回`truncated`。
- `ngx.var.http_xxx`：获取具体的header参数。
- `ngx.req.set_header`：添加header，多个不覆盖。
- `ngx.req.clear_header`：清理header的值。

#### 请求体

出于性能考虑，OpenResty不会主动读取请求体的内容，除非在`nginx.conf`中开启`lua_need_request_body`指令。针对较大的请求体，OpenResty会通过磁盘的临时文件来进行缓存，因此正确的处理流程是：

```lua
local data=ngx.req.get_body_data()
if not data then
	-- 获得文件名
    local tmp_file = ngx.req.get_body_file()
    -- 打开临时文件，会有IO阻塞操作
    io.open(tmp_file)
end
```

请求体是否存入磁盘中，由`client_body_buffer_size`(64位操作系统，默认16K)决定，应该合理调整`client_body_buffer_size`和`client_max_body_size`(也和内存大小、并发请求数相关)。

改写请求体

- `ngx.req.set_body_data`：使用字符串。
- `ngx.req.set_body_file`：使用本地磁盘文件。

### 响应

响应也由三部分组成：

- 状态行
- 响应头
- 响应体

#### 状态行

状态行中，最核心的是状态码，正常情况下，返回的状态码是200，对应常量`ngx.HTTP_OK`(数字)。OpenResty中有两个特殊的状态码：

- `ngx.HTTP_BAD_REQUEST`：发现请求有问题，用于终止请求。`ngx.exit(ngx.HTTP_BAD_REQUEST)`。
- `ngx.OK`：退出当前处理阶段，进入下一阶段。`ngx.exit(ngx.OK)`。

OpenResty中可以使用`ngx.status=状态码`改写响应的状态码，具体的状态码信息参考文档：https://github.com/openresty/lua-nginx-module/blob/master/README.markdown#http-status-constants。

#### 响应头

设置响应头有两种方法：

- 操控table：`ngx.header`

  ```lua
  ngx.header.content_type='text/plain'
  ngx.header.content_type = {'a', 'b'}
  -- 删除
  ngx.header["X-My-Header"] = nil;
  ```

- `lua-resty-core`提供的API。

  ```lua
  local ngx_resp=require "ngx.resp"
  ngx_resp.add_header(key,value)
  ```

#### 响应体

响应体输出也有两种方法：

- `ngx.say(内容)`
- `ngx.print(内容)`

`ngx.say`和`ngx.print`相比，`say`方法会在最后多一个换行符，这两种方法都支持数组，避免字符串拼接的低效。

## 通信

### 进程间通信

OpenResty中有四种数据共享方式，适用场景各不相同：

- `ngx.var`：适用于C模块和`lua-nginx-module`之间共享数据，但由于涉及hash查找和内存分配，因此性能较差，而且只能用于存储字符串。
- `ngx.ctx`：可以在同一请求的不同阶段间共享数据，常用于缓存`ngx.var`中的信息。`ngx.ctx`不能在模块级别中进行缓存，因为它会随请求一起销毁，常在函数中使用。
- 模块级别的变量：同一个worker中的请求将共享数据。通常情况下只用于保存只读数据，如涉及写操作，可能会存在race(除非保证整个流程都不存在yield操作，那么该请求的处理不会被打断)。
- `shared dict`：不同worker之间共享数据。

OpenResty中`shared dict`不仅仅支持数据的存放和读取，还支持原子计数和队列操作。`shared dict`提供的API都是原子操作，因此不必担心多个worker和高并发下的竞争问题。

#### 创建

通过在`nginx.conf`中添加``lua_shared_dict `可以创建一个`shared dict`。

```nginx
 http {
     # 创建一个shared dict，名称为dogs 内存空间10m
     lua_shared_dict dogs 10m;
     server {
         location /set {
             content_by_lua_block {
                 # 获取shared dict
                 local dogs = ngx.shared.dogs
                 dogs:set("Jim", 8)
                 ngx.say("STORED")
             }
         }
         location /get {
             content_by_lua_block {
                 local dogs = ngx.shared.dogs
                 ngx.say(dogs:get("Jim"))
             }
         }
     }
 }
```

#### 读写操作

##### 写

- `set`：添加新的键值对，当内存不足时，采用LRU淘汰。
- `safe_set`：当内存不足时，不采用LRU淘汰旧数据，返回`no memory`。
- `add`：当key不存在时，才插入。
- `safe_add`：当key不存在时，才插入，如果内存不足，也不执行。
- `replace`：用于替换存在key对应的value。

##### 读

- `get`：获取键
- `get_stale`：多一个过期数据返回值。

##### 删除

- `delete`
- `set(key,nil)`

#### 队列操作

- `lpush/rpush`
- `lpop/rpop`
- `llen`

#### 管理操作

- `get_keys`：获取kv。
- `capacity`：`lua-resty-core`，获取共享内存大小。
- `free_space`：`lua-resty-core`，获取空闲页字节数，为0时，已经分配的页上也可能空间。

### cosocket

OpenResty提供cosocket来实现非阻塞网络IO，它依赖于Lua协程特性和Nginx中的事件机制。cosocket支持TCP、UDP和Unix Domain Socket。调用一个cosocket相关函数，其内部实现流程是：

![协程切换流程]()

出现网络I/O时，cosocket通过yield主动交出控制权，然后把网络事件注册到Nginx中；当条件满足后，Nginx通过resume唤醒协程继续处理。

#### TCP API

- `ngx.socket.tcp`：创建对象
- `tcpsock:settimeout`：设置超时时间，但不会影响`lua_socket_keepalive_timeout`，单位毫秒。
- `tcpsock:settimeouts`：分别设置读写超时。
- `tcpsock:connect`：建立连接。
- `tcpsock:send`：发送数据。
- `tcpsock:receive`：默认接收一行数据。
- `tcpsock:receiveany`：指定接收多大的数据。
- `tcpsock:receiveuntil`：遇到指定字符串就结束，返回一个迭代器，通过迭代器读取数据。
- `tcpsock:setkeepalive`：将该cosocket放入连接池，避免频繁创删cosocket。
- `tcpsock:close`：关闭连接。

#### socket指令

当指令和API冲突时，以API为主。

- `lua_socket_connect_timeout`：连接超时时间，默认60s
- `lua_socket_send_timeout`：发送超时，默认60s
- `lua_socket_send_lowat`：发送阈值，默认为0
- `lua_socket_read_timeout`：读取超时时间，默认60s
- `lua_socket_buffer_size`：读取数据的缓存区，默认4k、8k。
- `lua_socket_pool_size`：连接池大小，默认30.
- `lua_socket_keepalive_timeout`：连接池中，cosocket对象空闲时间，默认60s。
- `lua_socket_log_errors`：cosocket发生错误时，是否记录日志，默认on。

#### 示例

```nginx
resty -e "local sock=ngx.socket.tcp()
sock:settimeout(1000)
local ok,err = sock:connect('www.baidu.com',80)
if not ok then
	ngx.say('fail to connect:',err)
	return
end

local ok,err = sock:send('GET / HTTP/1.1\r\nHost:www.baidu.com\r\n\r\n')
if err then
	ngx.say('fail to send',err)
	return
end

local data,err,partial=sock:receive()
if err then
	ngx.say('fail to receive',err)
	return
end

sock:close()
ngx.say('response',data)"
```

#### 问题

- 在不能使用cosocket的阶段中如何使用cosocket呢？

  类似`init_worker_by_lua`这些阶段，可以通过创建定时器(时间为0，立即调用)，来使用cosocket。

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
  
  	init_worker_by_lua_block{
  		local timer=ngx.timer.at
  		local function my_print()
  			ngx.log(ngx.ERR,'hello')
  		end
          -- 注入一个定时器任务，立即执行
  		local suc,err=timer(0,my_print)
  		if not suc then
  			ngx.log(ngx.ERR,'failed',err)
  		else
  			ngx.log(ngx.ERR,'success')
  		end
  	}
      server {
          listen       8080;
          server_name  localhost;
  
          location / {
              root   html;
              index  index.html index.htm;
          }
      }
  }
  ```

## 定时任务

OpenResty提供了两种定时任务：

- `ngx.timer.at`：执行一次性定时任务。
- `ngx.timer.every`：执行固定周期任务。

定时任务是在后台运行的，而且无法取消，如果定时任务过多，很容易耗尽系统资源。OpenResty提供了两个指令，用于限制定时任务的数量：

- `lua_max_pending_timers`：限制等待执行的定时任务最大值。
- `lua_max_running_timers`：限制正在运行的定时任务最大值。

OpenResty也提供了两个API用于查询定时任务数量：

- `ngx.timer.pending_count()`
- `ngx.timer.running_count()`

## 特权进程

Nginx中主要分为master进程和worker进程，worker进程负责处理用户请求，master进程负责管理work进程。OpenResty中可以通过`lua-resty-core`提供的API`process.type()`，查看进程类型。使用`resty`时，只会启动worker进程。

```bash
$ ./resty -e "local process = require 'ngx.process'
> ngx.say(process.type())
> "
single
```

OpenResty在Nginx的基础上，增加了特权进程`privileged agent`：

- 不监听任何端口。
- 拥有和master相同的权限，能执行worker进程不能执行的任务。
- 特权进程只能在`init_by_lua`中开启。
- 特权进程只能在`init_worker_by_lua`中。

```nginx
	init_by_lua_block {
    local process = require "ngx.process"
    local ok,err = process.enable_privileged_agent()
    if not ok then
        ngx.log(ngx.ERR,"enable privileged agent failed",err)
    end
	}
# 特权进程只能在init_worker_by_lua中被触发，可以通过创建定时器来规避
init_worker_by_lua_block {
    local process = require "ngx.process"
    local function reload(premature)
    	local f,err=io.open(ngx.config.prefix().. "/log/nginx.pid",r)
        if not f then
        	ngx.log(ngx.ERR,"open nginx.pid failed",err)
        	return
       	end
        local pid = f:read()
        f:close()
        os.excute('kil -HUP '..pid)
    end
    
    if process.type()=="privileged agent" then
        -- 定时重启
    	local ok,err=ngx.timer.every(5,reload)
        if not ok then
       		ngx.log(ngx.ERR,err)
        end
    end
} 
```

## ngx.pipe

`os.excute`是一个阻塞操作，可以采用`lua-resty-shell`中提供的API，执行非阻塞操作。

```nginx
local shell = require "resty.shell"
local ok,stdout,stderr,reason,status=shell.run([[echo "hello"]])
ngx.say(stdout)
```

`lua-resty-shell`是通过`lua-resty-core`中的`ngx.pipe`API实现的。等价于

```nginx
local pipe = require "ngx.pipe"
local proc=pipe.spawn({'echo','hello'})
local data,err=proc:stdout_read_line()
ngx.say(data)
```

- 如何避免定时器在多个worker中被执行呢？

  通过shared dict来共享一个变量，在定时器中去判断该变量，决定是否运行。

## 正则

OpenResty中，处理正则应该使用`ngx.re.*`系列的API。

- `ngx.re.split`：由`lua-resty-core`提供，其使用温度在`lua-resty-core/lib/ngx/re.md`

OpenResty还提供一个指令：

- `lua_regex_match_limit`：：限制PCRE正则引擎的回溯次数，避免灾难回溯(ReDos)。

## 时间

- `ngx.time`：返回时间戳，单位为秒。
- `ngx.now`：返回时间戳，浮点数类型，能精确到毫秒
- `ngx.update_time`：更新nginx的缓存时间，会有系统消耗。
- `ngx.localtime`
- `ngx.utctime`
- `ngx.cookie_time`
- `ngx.http_time`
- `ngx.parse_http_time`

注意，如果有阻塞网络IO操作触发，会一直返回缓存的时间，而不是当前最新的时间。这是因为事件循环中会主动更新缓存的时间。

```lua
ngx.say(ngx.now())
os.excute('sleep 1')
ngx.say(ngx.now()) -- 前后时间相同

ngx.say(ngx.now())
ngx.sleep(1)   -- 非阻塞方法，长耗时密集运算可以通过该方法让出控制权，避免其他请求得不到处理
ngx.say(ngx.now())-- 前后时间不同
```

## 进程API

`lua-nginx-module`库提供`ngx.worker.*`和`lua-resty-core`库提供`ngx.process.*`系列API，通过这些API，可以获取进程相关的信息。

`ngx.worker.*`系列的API负责获取worker进程的信息：

- `ngx.worker.pid`：获得进程ID。
- `ngx.worker.id`：获得进程编号，从0开始。
- `ngx.worker.exiting`
- `ngx.worker.count`

`ngx.process.*`系列的API负责获取父进程和特权进程的相关信息。

- `ngx.process.type`
- `ngx.process.enable_privileged_agent`
- `ngx.process.signal_graceful_exit`
- `ngx.process.get_master_pid`

## 真值与空值

在Lua中，除了`nil`和`false`之外，都是真值，`nil`也是Lua中唯一的空值。但是为了处理一些情况，OpenResty还引入了几种空值：

- `ngx.null`：为了解决`nil`无法作为`table`的`value`，用于表达`table`中的空值，是一个`userdata`。

- `cdata:NULL`：`LuaJIT FFI`接口调用函数返回的`NULL`指针。`cdata:NULL`是真值，但却和`nil`相等。

  ```lua
  $ ./resty -e "
  local ffi=require 'ffi'
  local cdata_null=ffi.new('void*',nil)
  if cdata_null then
  ngx.say('true')
  end
  "
  true
  
  $ ./resty -e "
  local ffi=require 'ffi'
  local cdata_null=ffi.new('void*',nil)
  ngx.say(cdata_null==nil)
  "
  true
  ```

- `cjson.null`：`cjson`库会将`json`中的`NULL`用`cjson.null`表示。

## API性能和安全的平衡

`ngx.req.get_uri_args`、`ngx.req.get_post_args`和`ngx.req.get_headers`默认只返回100个参数。如果构造了一个攻击，攻击参数在第100个参数之后，可以绕过WAF的检测。这三个API都有一个可选参数`max_*`，可以指定获取参数的个数，设置为`0`时，将返回所有的参数，但这会导致新的攻击(DDOS)。攻击者可以通过构造海量参数的请求，导致worker进程CPU满载。

OpenResty为了保证向下兼容、不引入新的安全和性能问题，采用增加错误提示来解决这个问题。新的API为`args, err = ngx.req.get_post_args(max_args?)`。如果参数超过预设值，err会为`truncated`。这是一种平衡，由逻辑来进行判断如何处理。

在安全方面可以采用两种防护方式：

- 主动：身份验证，非白即黑
- 被动：黑名单，非黑即白

```python
if is_hacker():
	deny()
else:
	access()

if is_admin():
	access()
else:
	deny()
```

## 如何找到高质量第三方库

可以从`awesome-resty`中查找相关的第三方库，考虑因素有：作者、测试覆盖、star数、活跃度、接口封装。`lua-resty-requests`是一个不错的HTTP第三方库，类似Python的Request库，如`local r, err = requests.get({ url = url, ... })`。Lua在参数固定时，可以省略括号，但不推荐。

断点调试库`lua-resty-repl`

## 实战：实现Memcached Server

### 原始需求

- 目的：为什么要实现memcached server？

  有些老版本的浏览器，不支持HTTPS中的`Session Ticket`，只支持`Session ID`。因此服务器必须在内存中保存一份`Session ID`对应的信息，这些可以使用`Memcached`来保存。

- 为什么不使用已有的MemCached产品或Redis？

  引入新的产品需要引入一个新的进程，增加部署和维护成本。该Memcached只需要支持set、get和过期操作即可，使用OpenResty的Stream模块，可以很快实现该需求。

- Memcached的协议？

  Memcached支持tcp和udp，可以使用tcp来实现，其具备以下操作：

  - `get key`：返回值`VALUE key flags exptime value END`
  - `set key flags exptime bytes value`
  - 错误处理：为了兼容Memcached，采用和官方相同的错误信息
    - `ERROR\r\n`：客户端发送了不存在的请求。
    - `SERVER_ERROR <error>`：服务器发生错误。
    - `CLIENT_ERROR <error>`：客户端错误，如参数错误。

### 方案

- 采用`stream-lua-nginx-module`来处理四层流量。
- 采用`shared_dict`来存储数据，支持`get`、`set`和超时时间设置，并且能在进程间共享。

