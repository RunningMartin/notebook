# OpenResty学习笔记

## 开篇词

- 为什么要学习OpenResty？

OpenResty是一个兼具开发效率和性能的服务器端平台，基于Nginx实现，但其使用范围已经突破反向代理和负载均衡。它通过`lua-nginx-moudle`模块，将LuaJIT嵌入到Nginx中，并对外提供一套完整的Lua API，支持非阻塞IO，并提供了轻量级线程和定时器等抽象。通过OpenResty，你可以在拥有脚本语言的开发效率同时，获得Nginx的高并发和高性能优势。

- 入门书籍：《OpenResty最佳实践》
- 目标：搭建一个简单但高性能的API网关

## OpenResty的特性

- 详尽的文档和测试用例。

  OpenResty文档非常详细，可以通过查看文档解决大量问题，可以通过命令`restydoc`来使用shell查看文档。文档中只有少量的通用代码片段，通过查看`/t`目录，可以查看所有的测试用例。

- 同步非阻塞

  OpenResty支持协程，并基于此实现了同步非阻塞的编程模式。

  ```lua
  local res,err=query-mysql(sql)
  local value,err=query-redis(sql)
  ```

  同步指的时，等到`query-mysql`返回结果后，才能执行`query-redis`；异步指的是不用等`query-mysql`的结果返回，继续执行`query-redis`。而阻塞是指，加速查询MySQL需要等待1S，这1S中，操作系统只能傻等着；而非阻塞指，在这一秒内，操作系统去处理其他的请求。非阻塞是解决C10K、C100K的关键。

- 动态

  Nginx如果修改了配置文件，需要重新加载才能生效。我们通过Lua使用OpenResty中`lua-nginx-module`模块提供的Lua API，动态控制路由、上游、SSL 证书、请求、响应，甚至还能在不重启OpenResty的前提下，修改业务逻辑。

- 学习重点

  - 同步非阻塞的编程模式
  - 不同阶段的使用
  - LuaJIT和Lua的区别
  - OpenResty API和周边库
  - 协程和cosocket
  - 单元测试框架和性能测试工具
  - 火焰图和周边工具链
  - 性能优化

## hello world

- 安装：

  - 推荐采用OpenResty的仓库，然后通过包管理工具安装。这是因为OpenResty为了避免编译时，需要解决外部依赖，维护了自己的依赖相关的打包脚本，而官方仓库不会接受第三方维护的包，导致自带版本比较陈旧。通过使用OpenResty自己仓库中的包，可以省去这些麻烦。
  - 编译安装：依赖`pcre`、`zlib`、`openssl`，官方维护`/usr/local/openresty`

- 代码

  ```nginx
  resty -e "ngx.say('hello world');ngx.ngx.sleep(60)"
  ps -ef |grep nginx # 可以查看到一个nginx进程
  # 不会启动worker进程，因此不监听端口
  ```

- OpenResty CLI：提供命令行，可以通过resty -h或查看官方文档查看完整列表。

  ```nginx
  # 结合nginx 创建一个共享内存字典，并进行操作
  # dogs 1m  创建一个共享内存，名字为dogs 大小为1m 
  # 在Lua中通过字典来使用共享内存
  resty --shdict='dogs 1m' -e 'local dict=ngx.shared.dogs
  							dict:set("Tom",56)
  							print(dict:get('Tom'))
  							'
  # 返回值56
  
  # 通过--http-include和--main-include来配置nginx文件
  resty --http-conf 'lua_shared_dict dogs 1m;' -e 
  					'local dict=ngx.shared.dogs
  					dict:set("Tom",56)
  					print(dict:get('Tom'))
  					'
  ```

- 在Nginx的配置文件中嵌入Lua。

  ```nginx
  # -p 指定工作目录 pwd为当前目录
  # 通过OpenResty -p `pwd` -c conf/nginx.conf
  # 通过curl -i 127.0.0.1:8080 访问
  event {
      worker_connections 1024;
  }
  
  http {
      server {
          listen 8080;
          location / {
              # 通过content_by_lua指令嵌入lua代码
              content_by_lua 'ngx.say("hello world")';
          }
      }
  }
  ```

- 改进：通过`content_by_lua_file`引用类库代码，如果有require需求，可以通过`lua_package_path`和`lua_package_cpath`设置类库加载目录。

  ```nginx
  # hello.lua
  ngx.say("hello world")
  
  # nginx.conf
  event {
      worker_connections 1024;
  }
  
  http {
      server {
          listen 8080;
          location / {
              # 通过content_by_lua_file指令载入lua文件
              content_by_lua_flie lua/hello.lua;
          }
      }
  }
  # 重启OpenResty
  sudo kill -HUP `cat logs/nginx.pid`
  ```

## 目录结构

- 疑问：

  - `content_by_lua_flie`使用的是相对路径，OpenResty如何找到该文件？

    启动OpenResty时，通过`-p`指定了工作目录，OpenResty将通过`-p`参数指定的目录与相对路径拼接出绝对路径。

  - 更改Lua文件内容后，如何才能及时生效？

    Lua代码在第一个请求是会被加载，然后缓存起来，因此只能通过重新加载OpenResty，才能让Lua代码生效。在调试过程中，可以通过关闭`lua_code_cache`来避免重新加载，但在线上时，必须打开，不然每次都需要加载Lua代码。

  - 如何将Lua代码所在的文件夹放入OpenResty的查找路径？

    OpenResty提供`lua_package_path`指令，来设置Lua模块的查找路径，可以通过将其设置为`$prefix/lua/?.lua;;`

    - `$prefix`：表示启动参数`-P`。
    - `lua/?.lua`：指`lua`目录下所有以`.lua`结尾的文件。
    - `;;`：代表内置的代码搜索路径

- 子目录：通过`OpenResty -v`可以查看安装目录

  - `bin`
    - `resty`：OpenResty CLI
    - `openresty`：启动文件，为nginx的软连接
    - `opm`：包管理工具
    - `restydoc`：文档工具
  - `luajit`：LuaJIT的可执行文件和依赖文件
  - `lualib`：OpenResty提供的Lua库
    - `ngx`：存放`lua-resty-core`的Lua代码，是基于FFI实现的OpenResty API
    - `resty`：存放`lua-resty-*`项目包含的Lua文件。
  - `nginx`：nginx的可执行文件和依赖文件
  - `pod`：用于给Perl的模块编写文档

- OpenResty概览
  - nginx C模块：OpenResty中包含20多个Nginx的C模块，通过`openresty -v`命令回显`--add-module`可以查看包含的ngixn。和redis、memcached交互的模块不推荐使用，`redis2-nginx-module`、`redis-nginx-module`、`memc-nginx-module`。OpenResty不会开发更多的nginx C库，开发基于cosocket的lua库。
  - `lua-resty-周边库`
  - `LuaJIT`分支
  - 测试框架`test-nginx`、`mockeagain`用于模拟慢速网络。
  - `systemtap`工具
  - 打包工具：`openresty-packaging`
  - 开发工具集：`openresty-devel-utils`
    - `lh-releng`：LuaJIT代码检测工具
    - `reindex`：格式化test-nginx测试用例，重新排列测试用例的工具。
    - `opsboy`：自动化部署

## 包管理工具

- OPM

  OPM是OpenResty自带的包管理器，可以通过命令`opm search`查询，如`opm search http`查询和http请求相关的库，这些库都是采用`cosocket`实现的。规定采用`cosocket`实现的库，必须用`lua-resty-前缀`。OPM工具的缺陷是需要自己去甄别出那些lua-resty库才是正确的选择。

  ```
  # opm search http
  # 不太友好
  openresty/lua-resty-upload
  # opm search lua-resty-http
  # 将以Github ID/repo name的形式返回相应的第三方库
  ```

- LUAROCKS

  LUAROCKS能搜索Lua世界中的库，LUAROCKS还支持C源码，可以查看Kong的rockspec文件。LUAROCKS不支持私有库。

  ```
  # luarocks search http 将返回一堆库
  # luarocks search lua-resty-http 会返回一个库，可以去官网查看相关信息
  ```

- AWESOME-RESTY

  [awesome-resty](https://github.com/bungle/awesome-resty)这个项目维护了所有OpenResty可用的包。

## OPM

OPM的官方网站是用OpenResty+Postgre驱动的，其官方仓库为：https://github.com/openresty/opm。通过该参考，可以查看nginx和lua是如何配合的，目录结构为

- bin
- utils
- web
  - conf：nginx配置文件
  - lua：
    - opmserver：opm的具体实现
    - vendor：使用的lua库

Nginx和lua的配合

```nginx
http {
    # 设置lua脚本位置 prefix变量对应 -p参数
    lua_package_path "$prefix/lua/?.lua;$prefix/lua/vendor/?.lua;;";
    # 注入nginx执行 
    # init阶段 执行初始化
    init_by_lua_block {
        # 预加载，在master中进行，fork到worker进程中
        -- preload Lua modules
        require "opmserver"
    }
    # content阶段 运行lua中的逻辑代码
    location = /api/pkg/exists {
		# 加载额外的配置文件
        include get-limiting.conf;
        content_by_lua_block {
                require("opmserver").do_pkg_exists()
            }
    }
}
```

OpenResty中提倡的是函数式编程，而不是面对对象编程。

https://github.com/openresty/openresty.org

## OpenResty需要使用的Nginx知识

开发OpenResty中，为了提供可读性、可维护性和可扩展性，请尽量遵循如下准则：

- 尽可能少配置nginx.conf。
- 避免`if`、`set`、`rewrite`指令的搭配
- 能使用Lua解决，就不要使用Nginx的配置、变量和模块。

### nginx配置

Nginx在进程启动时读取配置文件，因此修改了配置文件，需要重新加载Nginx才行。配置nginx的配置文件时，要注意指令的上下文，涉及的模块有`ngx_core_module`、`ngx_http_core_module`和`ngx_stream_core_module`。选择OpenResty时，要查看版本号，有些Nginx支持了的功能，OpenResty不一定支持。

### Master-Worker模式

![Master-Worker模式]()

Nginx中的Master进程只负责管理Worker进程，负责接受信号量、控制Worker进程的状态。Worker进程负责处理客户端的请求。采用多进程模式，可以避免多线程模式下，某个线程导致整个服务不可用。OpenResty中还添加了特权进程，不监听任何端口，拥有和Master进程相同的权限，负责处理一些高权限的操作。特权进程和Nginx二进制热升级机制互相搭配，可以实现自我二进制升级流程，而不需要依赖外部程序。尽量在OpenResty进程内解决问题，方便部署和运维，也降低了程度出错的概率。

### 执行阶段

nginx中处理http请求有11个阶段：

```c
typedef enum {
    NGX_HTTP_POST_READ_PHASE = 0,

    NGX_HTTP_SERVER_REWRITE_PHASE,

    NGX_HTTP_FIND_CONFIG_PHASE,
    NGX_HTTP_REWRITE_PHASE,
    NGX_HTTP_POST_REWRITE_PHASE,

    NGX_HTTP_PREACCESS_PHASE,

    NGX_HTTP_ACCESS_PHASE,
    NGX_HTTP_POST_ACCESS_PHASE,

    NGX_HTTP_PRECONTENT_PHASE,

    NGX_HTTP_CONTENT_PHASE,

    NGX_HTTP_LOG_PHASE
} ngx_http_phases;
```

OpenResty中也有11个`*_by_lua`的指令，可以查看`lua-nginx-module`的文档

![OpenResty阶段指令]()

- `init_by_lua`：创建Master进程时执行，可以预先加载Lua模块和公共只读数据，利用COW特性，节约内存。
- `init_worker_by_lua`：创建worker进程时执行。
- `set_by_lua`：设置变量
- `rewrite_by_lua`：转发、重定向
- `access_by_lua`：准入、权限
- `content_by_lua`：生成返回内容
- `header_filter_by_lua`：响应头过滤
- `body_filter_by_lua`：响应体过滤
- `log_by_lua`：日志记录

通过拆分为不同阶段的指令，流水线般处理请求。

### 二进制热升级

- 启动新的master进程：向master进程发送USR2信号量
- 关闭旧worker进程：向旧master进程发送WINCH信号量
- 关闭旧master进程
- 回退：向旧master进程发送HUP信号量

## LuaJIT

OpenResty中使用的是LuaJIT，只支持Lua 5.1版本。OpenResty的安装目录下`luajit/bin/luajit`中包含LuaJIT的可执行文件，可以通过两种方法测试lua：

- `luajit *.lua`
- `resty -e '内容'`

### 数据类型

lua中有六种基本数据类型：

- `string`

  Lua中的字符串是不可变的值，如果修改某个字符串时，等于创建一个新的字符串。这样有缺点也有优点：优点是，同一个字符串出现多次，内存中只有一份；缺点是修改、拼接字符串时，会额外创建很多不必要的字符串。字符串的表达方式有三种：单引号、双引号和双括号(`[[字符串内容]]`)，双括号的特点是字符串中不会做任何的转义，如果字符串中包含中括号，可以使用添加等号`[=[this is my [[]. ]=]`。

- `function`

  函数时Lua的一等公民，通过变量指向一个函数。

- `boolean`

  布尔量只有true和false，但是Lua中只有nil和false是假，其他都是真。因此判断时，需要显式写出比较的对象。

- `number`

  Lua中的数字采用双精度实现。LuaJIT还支持双数模式，即根据上下文，用整型存储整数，用双精度浮点数存储浮点数，还可以通过后缀`LL`，存储长长整型的大整数。

- `table`

  table是Lua中唯一的数据结构。

- `nil`

### 库函数

OpenResty中的优先级时：OpenResty的API > LuaJIT库函数 > 标准的Lua的函数。

#### string库

字符串处理中，如果遇到正则表达式的问题，一定要使用`ngx.re.`处理。

#### table库

table库只推荐`table.concat`和`table.sort`。`table.concat`常用于字符串的拼接，不会产生无用的字符串`table.concat({'a','b','c'})`。

#### math库

math库中常用的两个函数是：`math.randomseed`和`math.random`。`randomseed`

用于设置随机种子，常用`os.time()`。设置随机种子方法：

- `math.randomseed(tostring(os.time()):reverse():sub(1,6))`：通过reverse操作，即使时间间隔很小，随机种子的值变化也很大。

  ```lua
  -- 两次产生的随机种子和随机数相同
  seed=tostring(os.time()):reverse():sub(1,6)
  math.randomseed(tostring(seed))
  print(math.random())
  print(math.random())
  print(seed)
  
  seed=tostring(os.time()):reverse():sub(1,6)
  math.randomseed(tostring(seed))
  print(math.random())
  print(math.random())
  print(seed)
  ```

- 从`/dev/random`和`/dev/urandom`中读取随机数。

  ```lua
  urand = assert (io.open ('/dev/urandom', 'rb'))
  rand  = assert (io.open ('/dev/random', 'rb'))
  
  function RNG (b, m, r)
  	b = b or 4
    	m = m or 256
    	r = rand or urand
    	local n, s = 0, r:read (b)
  
    	for i = 1, s:len () do
      	n = m * n + s:byte (i)
    	end
      
    	return n
  end
  ```

#### 虚变量

当函数返回多个值时，有些返回值不需要接收，这时需要虚变量(下划线)来表示丢弃不需要的数据，仅仅起占位左右。

### LuaJIT的区别

OpenResty中，所有的Worker和Master进程都有一个LuaJIT VM，同一个进程中的所有协程都将共享该虚拟机。LuaJIT的语法兼容Lua 5.1，OpenResty使用的是自己维护的LuaJIT分支，并扩展了很大特有的API。

- 为什么不直接使用标准Lua？

  标准Lua处于性能考虑，内置了虚拟机，因此Lua代码会先被编译为字节码，再由Lua虚拟机执行。LuaJIT除了有一个汇编实现的Lua解释器，还有一个可以直接生成机器码的JIT编译器。LuaJIT在执行时，也会将Lua代码编译为字节码，字节码由解释器解释执行，但是执行过程中，会记录一些运行时信息，如函数调用次数，循环执行次数。当这些次数触发一个阈值后，JIT编译器会将这些函数或循环编译为机器码。因此LuaJIT的性能优化是通过将尽可能多的Lua编译为机器码。

### Lua的特点

- Lua的下标从1开始

  ```nginx
  t={100}
  print(t[1])
  ```

- 使用`..`拼接字符串

  ```lua
  print('hello'..',world')
  ```

- 只有table一种数据结构：核心是键值对，如果不显式用键值对，默认用数字作为下标，从1开始。

  ```lua
  local color={first='red','blue',second='green','yellow'}
  print(color['first'])
  print(color[1])
  print(color['second'])
  print(color[2])
  -- lua只有在table为一个序列时，才能获取其长度
  print(table.getn(color)) -- 2
  print(table.getn({1,2,3,4,5})) --5
  ```

- 默认为全局变量，除非采用`local`声明，OpenResty强烈推荐采用local，即使是`require module`。

### FFI(Foreign Function Interface)

LuaJIT紧密结合FFI，可以在Lua代码中调用C函数和使用C的数据结构。

```lua
local ffi = require('ffi')
ffi.cdef[[
int printf(const char *fmt, ...);
]]
ffi.C.printf("Hello %s","world");
```

通过FFI可以调用Nginx、OpenSSL的C函数，通过FFI方式比Lua/C API更高效，这是lua-resty-core存在的意义。为了性能考虑，LuaJIT还扩展了两个table函数，`table.new`和`table.clear`，用于性能优化。

### lua-resty-core

Lua中可以通过Lua C API调用C函数，在Lua JIT还可以通过FFI调用C函数。在OpenResty中，可以通过两种方法调用：

- `lua-nginx-moduole`通过Lua C API完成。
- `lua-resty-core`则是将`lua-nginx-module`中的部分API通过FFI重新实现。

#### lua-nginx-module工作原理

`lua-nginx-module`通过Lua C API来调用C函数，其核心是编写符合Lua要求的C API，然后在API中调用相应的C函数即可，这里以`decode_base64`为例。

- 注册C Function：将`ngx_http_lua_ngx_decode_base64`和API`decode_base64`绑定。

  ```c
  // ngx_http_lua_base64.c
  lua_pushcfunction(L, ngx_http_lua_ngx_decode_base64);
  lua_setfield(L, -2, "decode_base64");
  ```

- 定义C函数

  ```c
  // 必须满足lua的要求 typedef int (*lua_CFunction)(lua_State* L))
  static int ngx_http_lua_ngx_decode_base64(lua_State *L)
  {
      ngx_str_t p, src;
      src.data = (u_char *) luaL_checklstring(L, 1, &src.len);
  	// ngx_base64_decoded_length 是由nginx提供的C函数
      p.len = ngx_base64_decoded_length(src.len);
  
      p.data = lua_newuserdata(L, p.len);
  	// ngx_decode_base64是由nginx提供的C函数
      if (ngx_decode_base64(&p, &src) == NGX_OK) {
          lua_pushlstring(L, (char *) p.data, p.len);
  
      } else {
          lua_pushnil(L);
      }
      return 1;
  }
  ```

C编写的函数是无法将返回值传递给Lua，因此只能通过栈来传递Lua和C之间的调用参数和返回值。而且这些函数不能被JIT追踪，无法优化。

#### LuaJIT FFI

FFI的交互部分是通过Lua是实现的，因此这部分代码能被JIT追踪，并被优化。还是以`base64_decode`为例。

```lua
-- bundle\lua-resty-core-0.1.17\lib\resty\core\base64.lua
ngx.decode_base64 = function (s)
    if type(s) ~= 'string' then
        error("string argument only", 2)
    end
    local slen = #s
    local dlen = base64_decoded_length(slen)
    -- print("dlen: ", tonumber(dlen))
    local dst = get_string_buf(dlen)
    local pdlen = get_size_ptr()
    -- 调用 lua-nginx-module仓库中的中的ngx_http_lua_ffi_decode_base64
    local ok = C.ngx_http_lua_ffi_decode_base64(s, slen, dst, pdlen)
    if ok == 0 then
        return nil
    end
    return ffi_string(dst, pdlen[0])
end

-- bundle\ngx_lua-0.10.15\src\ngx_http_lua_string.c
int
ngx_http_lua_ffi_decode_base64(const u_char *src, size_t slen, u_char *dst,
    size_t *dlen)
{
    ngx_int_t      rc;
    ngx_str_t      in, out;

    in.data = (u_char *) src;
    in.len = slen;

    out.data = dst;

    rc = ngx_decode_base64(&out, &in);

    *dlen = out.len;

    return rc == NGX_OK;
}
```

#### LuaJIT FFI GC

LuaJIT只负责自己分配的资源，而使用ffi.c分配的空间需要自己手动释放。

```lua
-- 分配内存
local p=ffi.gc(ffi.C.malloc(n),ffi.C.free)
p=nil --释放
```

`p`是一个`cdata`，由LuaJIT负责释放。当`p`被LuaJIT GC时，`ffi.gc`会自动调用`ffi.C.free`释放内存。推荐使用`ffi.C.malloc`而不是`ffi.new`，因为`ffi.new`返回的是`cdata`，由LuaJIT负责管理，而LuaJIT GC管理的内存是由上限的，默认OpenResty没有打开GC64，因此单个worker内存上限为2G，超出时会报错。

使用FFI时，要时刻注意内存泄露问题，可以通过Valgrind检测。在测试框架test::nginx中，需要将环境变量`TEST_NGING_USE_VALGRIND`设置为1。

在测试工具集stapxx中，可以找到`lj-gc`和`lj-gc-objs`这两个工具。针对core dump问题，可以通过gdb工具集openresty-gdb-util中查找`lgc`、`lgcstat`、`lgcpath`三个工具。

#### lua-resty-core

OpenResty已经放弃`lua-nginx-module`中的C API方式，全新的API都是通过FFI的方式在`lua-resty-core`仓库中实现。`1.15.8.1`默认不开始`lua-resty-core`，因此会带来很大性能问题，可以通过`init_by_lua`中添加`require 'resty.core'`打开。`1.15.8.1`中添加了`lua_load_resty_core`指令，默认开启了`lua-resty-core`。`lua-resty-core`中不仅仅重新实现了lua-nginx-module中的部分API，还添加了很大新的API。`1.15.8`版本还默认开启了`GC64`，因此`ffi.C.malloc`和`ffi.new`区别不大。





