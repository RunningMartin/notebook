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

### 修改测试

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

### 分类

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

#### 请求处理

`ngx.req.*`负责处理请求相关的API，由`lua-nginx-module`提供。HTTP请求报文由三部分组成：

- 请求行
- 请求头部
- 请求体

请求行中的信息可以通过`ngx.var.*`获取，如`scheme`、`request_method`、`uri`，。这些参数和Nginx的参数相对应，可以参考`ngx_http_core_module`中的变量。OpenResty从性能(ngx.var效率低)、程序友好(返回字符串)和灵活性考虑(ngx.var中大多数只读)考虑，还提供了一些专门的API。

##### 请求行

- `ngx.req.http_version`：返回数字格式的版本号。
- `ngx.req.get_method`：返回字符串形式的方法名，不能和`ngx`中的方法常量进行比较。
- `ngx.req.set_method`：修改当前请求方法，参数是内置的数字常量，如`ngx.HTTP_POST`(数字8)，get和set方法参数格式尽量一致。
- `ngx.req.set_uri`：改写uri。
- `ngx.req.set_uri_args`：改写args，jump参数用于控制是否继续匹配下一个`location`，功能类似nginx中`return`的`break`。

##### 请求头部

- `ngx.req.get_headers`：只返回前100个header，超过返回``truncated`。
- `ngx.var.http_xxx`：获取具体的header参数。
- `ngx.req.set_header`：添加header，多个不覆盖。
- `ngx.req.clear_header`：清理header的值。

##### 请求体

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

#### 响应

响应也由三部分组成：

- 状态行
- 响应头
- 响应体

##### 状态行

状态行中，最核心的是状态码，正常情况下，返回的状态码是200，对应常量`ngx.HTTP_OK`(数字)。OpenResty中有两个特殊的状态码：

- `ngx.HTTP_BAD_REQUEST`：发现请求有问题，用于终止请求。`ngx.exit(ngx.HTTP_BAD_REQUEST)`。
- `ngx.OK`：退出当前处理阶段，进入下一阶段。`ngx.exit(ngx.OK)`。

OpenResty中可以使用`ngx.status=状态码`改写响应的状态码，具体的状态码信息参考文档：https://github.com/openresty/lua-nginx-module/blob/master/README.markdown#http-status-constants。

##### 响应头

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

##### 响应体

响应体输出也有两种方法：

- `ngx.say(内容)`
- `ngx.print(内容)`

`ngx.say`和`ngx.print`相比，`say`方法会在最后多一个换行符，这两种方法都支持数组，避免字符串拼接的低效。

