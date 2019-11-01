# OpenResty性能优化

## 优化理念

性能优化技巧只是如何去做，属于术的方向，而性能优化背后的道才是核心。

### 处理请求短、平、快

为了保证最高性能，必须保证以最快的速度处理单个请求，并回收相关资源。

- 短：请求的生命周期短，及时释放占用的资源。针对长连接，设置时间或请求次数阈值，定期释放资源。
- 平：一个API只做一件事，保证代码简洁。
- 快：避免阻塞主线程，占用大量CPU资源。

### 避免产生中间数据

临时数据会带来初始化和GC性能损耗，当产生临时数据的代码出现在热代码中时，将带来极大的性能损耗。这里面最经典的问题是字符串拼接。

## 避免使用阻塞函数

### 为什么要避免使用阻塞函数？

OpenResty的高性能基于Nginx的事件处理和Lua的协程机制：遇到网络IO等需要等待返回结果的操作时，使用yield将协程挂起，在Nginx中注册回调。操作完成后(完成、超时或出错)，Nginx回调resume，唤醒协程。通过这一流程，OpenResty能一直高效使用CPU资源，来处理所有的请求。这个流程中如果出现了阻塞函数，LuaJIT则不会将CPU交给Nginx的事件循环，其他请求需要等待该事件完成后，才会得到处理。通常情况下都采用cosocket来处理非阻塞操作。

### 常见的阻塞函数有哪些？

- 使用`os.excute`执行外部命令

  - 使用LuaJIT的[FFI库](https://wiki.luajit.org/FFI-Bindings)
  - 使用基于`ngx.pipe`的`lua-resty-shell`库。

- 使用`io.open`执行磁盘I/O

  - `lua-io-nginx-module`：利用nginx的线程池，将I/O操作从主线程移到其他线程处理，避免阻塞主线程。使用时需要重新编译Nginx。

    ```lua
    local ngx_io = require "ngx.io"
    local path = ""
    local file,err=ngx_io.open(path,"rb")
    local data,err=file:read("*a")
    file:close()
    ```

  - 调整架构，避免读写本地磁盘，转移到远端日志服务器。可以使用`lua-resty-logger-socket`。

- `luasocket`：`luasocket`是一个lua内置库，功能和cosocket一致，但不支持非阻塞操作，常用于`cosocket`不能使用的阶段，如`init_by_lua_*`、`init_worker_by_lua_*`

## 避免出现临时字符串

### 为什么要避免出现临时字符串？

处理字符串时，要牢记Lua中，字符串是不可变的，如果有所修改，那么一定是生成了新的字符串对象，如果原对象没有引用，将被GC回收。

字符串不可变最大的优点是节约内存，相同的字符串内容在内存中只有一份，通过不同的变量引用即可。这导致，新增加一个字符串时，会调用`lj_str_new`去判断字符串是否存在，不存在时才会创建新字符串。

### 常用的优化手段？

通过table来存储需要拼接的数据，然后使用`concat`进行拼接，避免了中间变量的产生和GC时间。

```lua
./resty -e "
local begin = ngx.now()
local s= ''
-- 做了10万次字符串拼接，中间产生了很多碎片
print('before concat,memory used:',collectgarbage('count'))
for i=1 ,100000 do
    s=s..'a'
end
-- 更新时间
ngx.update_time()
print('after concat,memory used:',collectgarbage('count'))
print(ngx.now()-begin)
"
before concat,memory used:157.8857421875
after concat,memory used:5364.6201171875
0.62400007247925

-- 自己维护下标
./resty -e "
local begin = ngx.now()
local t={}
print('before concat,memory used:',collectgarbage('count'))
-- 通过循环，使用数组存储数据
for i=1 ,100000 do
    t[#t+1]='a'
end
-- 更新时间
local s = table.concat(t,'')
ngx.update_time()
print('after concat,memory used:',collectgarbage('count'))
print(ngx.now()-begin)
"
before concat,memory used:158.0048828125
after concat,memory used:1409.517578125
0.015000104904175
```

### 产生临时字符串的操作有哪些？

- `string.sub('abcd',1,1)`：截取字符串，将返回临时字符串。
  - `string.char(string.byte("abcd"))`：先用byte取第一个字符的编码，再用编码转化为字符，不会产生临时字符串。
- OpenResty与Lua的API中，有很多接受字符串的API也支持table，可以避免一次字符串的查找、生成与GC。
  - `ngx.say`
  - `ngx.print`
  - `ngx.log`
  - `cosocket:send`

## 避免滥用table

### 为什么要避免滥用table？

table创建后，每次新增或删除元素，都会带来空间分配、resize和rehash操作。

### 常用的优化手段

- 使用`table.new`进行预分配：预先为table分配额外的空间。

  ```lua
  ./resty -e "
  local begin = ngx.now()
  local t = {}
  for i = 1,10000 do
      t[i]=i
  end
  ngx.update_time()
  print(ngx.now()-begin)
  "
  -- 优化方案
  ./resty -e "
  local new_tab = require 'table.new'
  -- 预先分配10000个数组元素空间和0个哈希元素空间
  local begin = ngx.now()
  local t = new_tab(10000,0)
  for i = 1,10000 do
      t[i]=i
  end
  ngx.update_time()
  print(ngx.now()-begin)
  "
  ```

- 自己计算下标，避免使用获取长度`O(n)`的方法。

  ```lua
  -- 添加元素
  local new_tab = require 'table.new'
  -- 预先分配100个数组元素空间和0个哈希元素空间
  local t = new_tab(100,0)
  -- insert会先去获取长度
  for i = 1,100 do
      table.insert(t,i)
  end
  
  --或者
  for i = 1,100 do
      t[#t+1]=i
  end
  ```

- 循环使用单个table：使用`table.clear`清空原数据，避免污染。`clear`只是将每个元素置为`nil`，而不会释放空间。常用于模块级别。

- table池：`lua-tablepool`提供缓存池的用法。

  ```lua
  local tab_pool=require 'tablepool'
  local tab_pool_fetch=tab_pool.fetch
  local tab_pool_release=tab_pool.release
  
  local pool_name = 'storage'
  -- 申请table
  local t = tab_pool_fetch(pool_name,10,0)
  -- 释放,no_clear表示回收时，是否清空table
  tab_pool_release(pool_name,t,[no_clear])
  ```

## OpenResty编码规范

编码规范能让开发者统一思想，统一风格，为代码维护、代码阅读提供了很大的便利性。OpenResty中常用的代码风格检查工具为`luacheck`和`lj-releng`，CI也会使用这两个工具进行检测。

```
luacheck -q lua
./utils/js-releng lua/*.lua
```

- 缩进：4个空格

- 空格：操作符两端都要有一个空格

- 空行：

  - 避免不必要的空行

    ```lua
    if a then
        ngx.say('a');
    end;
    ```

  - 避免多行变为一行

    ```lua
    if a then ngx.say('a') end
    ```

  - 函数之间用两个空行

  - 多个分支时，每个分支用一个空行分隔

- 每行最多80个字符

  - 换行时要体现上下两行对应关系。
  - 字符拼接，需要将`..`放置下一行首部。

- 变量：尽量使用局部变量。风格采用蛇形。常用采用全大写模式。

- 数组：

  - 采用`table.new`预分配。
  - 不要使用`nil`，一定要使用时，请用`ngx.null`。

- 字符串：避免在热代码中拼接字符串。

- 函数：命名采用蛇形命名，且遵循尽可能早返回。

- 模块：所有模块必须采用local。

  ```lua
  local ngx = ngx
  loca require = require
  local core = require("api.core")
  local timer_at = ngx.timer.at
  local function foo()
  	local ok,err = timer_at(delay,handler)
  end
  ```

- 错误处理：有错误信息返回的函数，必须对错误信息进行判断和处理。如果自己编写函数，错误信息作为第二个参数，以字符串的个数返回。

https://github.com/apache/incubator-apisix/blob/master/CODE_STYLE.md

https://github.com/openresty/luajit2

## 调试手段

### 断点和日志打印

- 针对能复现的bug，可以通过断点和增加日志：`ngx.say`、`ngx.log`。
- Mozilla RR：录制程序的行为，反复播放。

### 分布式场景

- 采用二分查找排除
- OpenTracing、ZipKin

### 动态调试工具

动态调试主要针对线上环境。

- systemtap

systemtap拥有自己的DSL，用于设置探测点。

```bash
# 安装sudo apt install systemtap
# hello-world.stp
probe begin{
    print("hello world");
    exit();
}
sudo stap hello-world.stp
```

工作原理：systemtap将脚本转换为C，运行系统C编译器创建kernel模块，当模块被加载时，会hook内核，激活探测事件。可以参考《Systemtap tutorial》。

- ebpf：启动速度快，内核支持，并且直接使用C语言。
- Vtune
- 火焰图

## OpenResty工具包

OpenResty中有两个开源项目：`openresty-systemtap-toolkit`和`stapxx`，提供了与nginx和OpenResty相关的systemtap工具包。覆盖on CPU、off CPU、共享字典、垃圾回收、请求延迟、内存池、连接池、文件访问等场景。

OpenResty 1.15.8默认开启LuaJIT GC64模式，因此这两个工具包可能不能使用，建议使用1.13。

- 共享字典

  ```bash
  # -p worker pid
  # -f 指定dict和key
  ./ngx-lua-shdict -p worker_pid -f --dict doct_name --key key --luajit20
  # -w 追踪指定key的字典写操作
  ./ngx-lua-shdict -p worker_pid -w --key key --luajit20
  # 核心是探针，探测ngx_http_lua_shdict_set_helper，在lua-nginx-module/src/ngx_http_lua_shdict.c中
  probe process("$nginx_path").function("ngx_http_lua_shdict_set_helper")
  ```

- CPU：常见的性能问题表现为两类，即CPU占用过高(性能瓶颈，on cpu)和CPU占用过低(阻塞函数，off cpu)，可以通过火焰图确认。

  - C级别的on CPU火焰图：`systemtap-toolkit`中的`sample-bt`，可以针对任意进程的调用栈取样。

    ```bash
    ./sample-bt -p pid -t 采样时间长度 -u > a.bt
    stackcollapse-stap.pl a.bt > a.cbt
    # 生成火焰图
    flamegraph.pl a.cbt >a.svg
    ```

  - Lua级别的on CPU火焰图：`stapxx`中的`lj-lua-stacks`。

  - C级别的off CPU火焰图：`systemtap-toolkit`中的`sample-bt-off-cpu`

    ```bash
    ./sample-bt-off-cpu -p pid -t 采样时间长度 -u > a.bt
    stackcollapse-stap.pl a.bt > a.cbt
    # 生成火焰图
    flamegraph.pl a.cbt >a.svg
    ```

  - Lua级别延迟工具`epoll-loop-blocking-distr`，对指定用户进程进行采样，并输出连续的`epoll_wait`系统调用之间的延迟分布。

    ```bash
    epoll-loop-blocking-distr.sxx -x pid --arg time=60
    ```

- 上游和阶段跟踪：cosocket或proxy_pass上游模块。可以使用`ngx-lua-tcp-recv-time`、`ngx-lua-udp-recv-time`和`ngx-single-req-latency`分析。`ngx-single-req-latency`分析单个请求在OpenResty中各个阶段的耗时。

  ```bash
  ./ngx-single-req-latency.sxx -x pid
  ```

## wrk和火焰图使用

demo位置：https://github.com/iresty/lua-performance-demo

- 压测工具：`wrk`
- CPU查看：`htop`
- 火焰图：查找性能分析点

## 缓存

设计缓存的参考资料《高性能Mysql》，缓存的原则：

- 越靠近用户的请求越好
- 尽量使用本进程和本机缓存。

OpenResty提供了两个缓存的组件：

- shared dict缓存：只能缓存字符串，且只有一份，每个worker都可以访问。
- lru缓存：能缓存所有的lua对象，只能由单个worker进程访问。

使用缓存时，应该搭配使用环境：

- 不在worker之间共享：lru
- 在worker之间共享：lru的基础上加shared dict。

### 共享字典缓存

shared dict必须在配置文件中使用，因此如果空间不足，只能修改配置文件后，重新加载才可以，不能动态扩缩容。

- 缓存数据的序列化：共享字典只能缓存字符串，因此其他对象必须使用cjson做序列化和反序列化，这个操作耗CPU，因此最好避免序列化与反序列化，一定要使用的话，可以缓存在lru中。
- stale数据：共享字典可以通过`get_stale`获取已经过期的数据，但是如果过期数据占用的资源被回收时时，则没有过期数据(LRU)。过期数据使用场景：当MySQL中获取的数据过期后，可以先判断MySQL的数据是否发生变化，没有发生变化，则修改缓存的过期时间。

### lru缓存

lru缓存只支持5个接口：

- `new`
- `set`
- `get`
- `delete`
- `flush_all`

```lua
local lrucache = require "resty.lrucache"
local cache, err =lrucache.new(200)
cache:set('dog',21,0.01)
ngx.sleep(1)
-- 数据过期后，将返回过期数据
local data,stale_data=cache:get("dog")
```

通常采用版本号来标识不同的数据，因此可以将get方法进行修改。

```lua
local function get(key,version,create_obj_func,...)
    local obj,stale_obj=lru_obj:get(key)
    -- 数据存在，且未过期，返回缓存数据
    if obj and obg._version == version then
        return obj
    end
    
    -- 数据过期，且版本未修改，则返回过期数据
    if stale_obj and stale_obj._version==version then
    	lru_obj:set(key,stale_obg,ttl)
         return stale_obj;
    end
    
    -- 找不到数据或版本不对，则重新获得数据，缓存
    local obj,err = create_obj_func(...)
    obj._version=version
    lru_obj:set(key,obj,ttl)
    return obj,err
end
```

将版本信息从key中隔离还有一个好处，如果key_version作为key，则会创建多个键值对，但是分离后，永远只有一份。

### 缓存风暴

#### 什么是缓存风暴？

缓存风暴(Dog-Pile)指的是，当缓存失效时，有大量请求到达，这些请求将全部去查询数据库，导致数据库服务器卡顿，甚至卡死。

```lua
-- 存在缓存风暴的伪代码
local value = get_value_from_cache(lua)
if not value then
	value = query_db(key)
    set_value_to_cache(key,value,ttl)
end
```

#### 如何避免缓存风暴？

- 主动更新缓存：创建定时任务主动更新缓存。OpenResty中定时器是有上限的，而且缓存过期时间和定时计划间隔时间相对应。

  ```lua
  local function query_db(premature,sql)
      local value = query_db(sql)
      set_to_cache(value,timeout=60)
  end
  local ok,err=ngx.timer.every(60,query_db,sql)
  ```

- `lua-resty-lock`：该锁基于共享字典，提供非阻塞的API，并且不必担心死锁。

  ```lua
  local resty_lock = require "resty.lock"
  -- 创建锁对象，lock是一个shared dict，可以添加锁过期时间、等待锁的超时时间
  local lock,err = resty_lock:new('lock')
  -- 加锁，加锁失败，err为timeout或locked
  local elapsed,err = lock:lock('my_key')
  -- 释放
  local ok,err = lock:unlock()
  ngx.say('unlock：',ok)
  ```

  通过锁，可以保证只有一个请求去数据源处请求数据，如果加锁失败，则返回缓存中的旧数据。通过该方案，可以完美解决缓存风暴问题。锁的源代码为https://github.com/openresty/lua-resty-lock/blob/master/lib/resty/lock.lua。

```lua
-- 尝试在共享字典中添加key，共享字典中的操作为原子操作，因此不怕竞争问题    
local ok, err = dict:add(key, true, exptime)
if ok then
    cdata.key_id = ref_obj(key)
    self.key = key
    return 0
end
```

- `lua-resty-shcache`：CloudFlare开源的`lua-resty`库，在共享字典和外部存储基础上做了一层封装，并提供序列化和反序列化接口。

  ```lua
  local shcache = require("shcache")
  local my_cache_table = shcache:new(
      ngx.shared.cache_dict{
          external_lookup=lookup,
          encode=cmsgpack.pack,
          decode=cmsgpack.decode,
      },
      {
          positive_ttl=10,
          negative_ttl=3,
          name='my_cache'
      }
  )
  local my_table,from_cache=my_cache_table:load(key)
  ```

### 多级缓存

- lua-resty-memcached-shdict：使用shared_dict为memcached做了一层封装，处理了缓存风暴和过期数据等细节。默认没有打包， 需要将源码下载到OpenResty查找目录下。其核心是：利用锁，缓存失效的情况下，只有一个请求去Memcached中获取数据，如果没有获取最新数据，则返回stale数据。

  - 优化方面：利用lua-resty-lrucache增加worker层的缓存。
  - 使用ngx.timer，异步更新缓存

- lua-resty-mlcache：使用shared dict和lua-resty-lrucache，实现多级缓存。

  ```lua
  local mlcache = require "resty.mlcache"
  -- 执行初始化，输入缓存名，字典名，其他参数，如lru缓存大小
  -- 设计接口时，应该让接口尽可能的简单，同时保留足够的灵活性(默认参数)
  local cache, err = mlcache.new("cache_name","cache_dict",{
          lru_size=500,
          ttl=3600,
          neg_ttl=30
      })
  if not cache then
      error()
  end
  ```

  ![mlcache架构图]()

  整个架构中有将数据分为三层：

  - L1：L1由lru_cache实现，每个worker一份，不会触发锁，性能很高。
  - L2：L2由shared dict实现，worker之间共享，共享字典由自旋锁提供原子性，不必担心竞争问题。
  - L3：L3由lua-resty-lock来保证只有一个请求去获取数据，避免数据风暴。

  缓存的更新是由请求被动触发，以最大的程度保证缓存的安全性。

  mlcache需要注意一点：L1能存储各种类型的数据，但是L2中只能存储字符串，因此L2与L1之间需要一个序列化与反序列化的操作，new和get中有一个可选参数`l1_serializer`负责L2到L1的数据处理。

## 常用的第三方库

- 寻找库：[`awesome-resty`](<https://github.com/bungle/awesome-resty>)、luarocks、opm

### ngx.var性能提升

`lua-var-nginx-module`能有效提升`ngx.var`的性能，不必使用`ngx.ctx`作为缓存。采用FFI接口。可以去提交pr，添加更多的变量

安装方法：

```bash
./configure --add-module=lua-var-nginx-module源码路径
# 安装
luarocks install lua-resty-ngxvar
```

使用方法：

```lua
content_by_lua_block{
    local var = require("resty.ngxvar")
    -- 等价于ngx.var.remote_addr
    ngx.say(var.fetch("remote_addr"))
}
```

源码分析：

```c
// 这段代码其实从nginx源码中搬运，使用FFI的方式直接获取变量，跳过ngx.var的查找逻辑
ngx_int_t
ngx_http_lua_var_ffi_remote_addr(ngx_http_request_t *r, ngx_str_t *remote_addr)
{
    remote_addr->len = r->connection->addr_text.len;
    remote_addr->data = r->connection->addr_text.data;

    return NGX_OK;
}
```

### json schema

lua-rapidjson支持json schema，用于检测接口的参数是否正确，以性能见长。

```json
# stringArray是一个array，元素类型为string，且不能为空，元素也不能重复
"stringArray":{
    "type":"array",
    "items":{"type":"string"},
    "minItems":1,
    "uniqueItems":true
}
```

前端可以直接复用该schema描述，用于前端页面的开发和参数校验。

后端可以使用该schema去校验接口合法性。`lua-rapidjson`提供函数`SchemaValidator`进行判断。

### worker间通信

[进程通信](<https://github.com/Kong/lua-resty-worker-events>)库提供worker进程间的通信。OpenResty不支持worker进程之间的通信，进程通信库是采用shared-dict实现的，具体思路是维护版本号，当新消息发布后，版本号加1，并将内容放在以版本号位key的字典中，每个worker都启动一个间隔为1秒的定时任务，不断检查版本号，一旦变化，则加载新内容，存在1秒的延迟。

## 限流

应用的性能需要关注突发流量对性能的影响，如突发事件、DDoS攻击。流量控制是采用一定的算法对入口流量进行疏导和控制，保证上游服务能正常运行。流量控制是在业务稳定和用户体验之间做平衡。常用的流量控制算法有漏桶和令牌桶。

### 漏桶

漏桶算法的目的是让请求速率保持恒定，让突发的流量变得平滑。

![漏桶算法示意图]()

漏桶算法的核心是建立一个缓冲区，通过固定的速率消费缓冲的请求，如果缓冲区满，则拒绝掉请求。OpenResty自带[漏桶算法](https://github.com/openresty/lua-resty-limit-traffic)。漏桶算法是以终端IP作为key来进行限流。

```lua
-- 当前请求和上一次请求之间的毫秒数
local elapsed = now - tonumber(rec.last)
-- rate速率最小0.001 s/r
-- excess 表示排队的请求数
excess = max(tonumber(rec.excess)-rate*abs(elapsed)/1000 + 1000,0)
-- burst表示桶满了
if excess > self.burst then
    return nil, "rejected"
end
-- 返回等待时间 excess/1000
return excess/rate, excess/1000
```

### 令牌桶

漏桶算法以IP作为依据限流时，如果某个客户端请求频繁，则会出现拒绝该客户端的部分请求。令牌桶允许突发流量进入后端服务，通过一个固定的速度向桶内放入令牌，请求需要先从桶中获取令牌，才能被后端处理，否则会被拒绝。[又拍云实现](<https://github.com/upyun/lua-resty-limit-rate>)

```lua
local limit_rate = require "resty.limit.rate"
-- global 20r/s 6000r/5m
-- 全局令牌桶
local lim_global = limit_rate.new("my_limit_rate_store",100,6000,2)
-- single 20r/s 6000r/5m
local lim_single = limit_rate.new("my_limit_rate_store",500,600,1)
-- 设置为全局
local t0,err = lim_global:take_available('__global',1)
-- 设置为按用户分配的令牌桶，以user_id为key
local t1,err = lim_single:take_available(ngx.var.arg_userid,1)
if t0==1 then
    return -- global bucket is not hungry
else 
    if t1==1 then
        return -- single bucket is not hungry
    else
        return ngx.exit(503)
    end
end
```

设置两个令牌桶，如果全局令牌桶有令牌，直接使用，尽可能多地服务用户的突发请求。如果全局没有，则判断单个用户的令牌桶，把突发请求多个用户的请求拒绝掉，不会影响其他用户的请求。

### nginx限速模块

nginx下的`ngx_http_limit_req_module`模块可以进行限速。

```nginx
# 将终端IP作为key，申请一块one的10M的内存地址，并且速率现在为1个请求每秒
limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;
server{
    location /search/{
        # 允许有5个排队，超出则拒绝，类似漏桶
        limit_req zone=one burst=5;
    }
}
```

nginx限速无法实现动态修改。

### 动态限流

通过配置文件来控制nginx的限流策略有两个问题：

- 限流策略不能灵活配置，如根据不同的身份IP进行限流。
- 每次修改都需要重载服务。

OpenResty中推荐使用[漏斗算法模块来](<https://github.com/openresty/lua-resty-limit-traffic>)，采用shared dict 保存key和计数，包含了三种限制方式：

- `limit-req`：采用漏桶算法，限制请求速率，access阶段生效。

  ```lua
  local limit_req=require "resty.limit.req"
  -- 200为每秒钟的速率 200+100是缓冲区大小
  local lim,err=limit_req:new('shared_dict',200,100)
  -- incoming处理终端的请求，key为用于限速，可以在前面动态生成key
  -- true表明该请求将被记录到共享字典中统计，用于多个限速限制时，前面的通过，但是后面不通过时，将不被计数
  local delay,err=lim:incoming("key",true)
  if not delay then
      if err=='rejected' then
          return ngx.exit(503)
      end
      return ngx.exit(500)
  end
  
  if delay>=0.001 then
      ngx.sleep(delay)
  end
  
  -- 多个限制时，只有当所有的限制都通过时，才计数，前面的只做演戏
  -- n为限制个数
  for i=1,n do
      local lim = limiters[i]
      -- 只有最后一个限制时，第二个参数才是true
      local delay,err=lim:incoming(keys[i],i==n)
  	if not delay then
          return nil,err
       end
  end
  ```

- `limit-count`：限制请求数，access阶段生效。

  ```lua
  local limit_count=require "resty.limit.count"
  -- 3600s内只能有5000次请求
  local lim,err = limit_count:new('shared_dict',5000,3600)
  local key = ngx.req.get_headers()['Authorization']
  -- 第二个参数为剩余调用次数
  local delay,remaining=lim:incoming(key,true)
  ```

- `limit-conn`：限制并发连接数，不仅仅在access阶段生效，还必须在log阶段调用leaving接口，将连接数减1，如果没有做这个操作，连接数很快达到阈值

  ```lua
  local limit_conn=require "resty.limit.conn"
  -- 连接数限制为1000，但是允许有1000个等待，等待延迟为0.5秒
  local lim,err = limit_conn:new('shared_dict',1000, 1000, 0.5)
  local key = ngx.req.get_headers()['Authorization']
  -- 第二个参数为剩余调用次数
  local delay,remaining=lim:incoming(key,true)
  
  log_by_lua_block{
      local latency = tonumber(ngx.var.request_time)-ctx.limit_conn_delay
      local key = ctx.limit_conn_key
      local conn,err=lim:leaving(key,latency)
  }
  ```

- `limit-traffic`：聚合使用，其核心是通过预演，直到最后才进行计数。

  ```lua
  local lim1,err=limit_req:new('shared_dict',200,100)
  local lim2,err = limit_count:new('shared_dict',5000,3600)
  
  local limiters={lim1,lim2}
  local host=ngx.var.host
  local client=ngx.var.binary_remote_addr
  local keys={host,client}
  local status={false,true}
  local delay,err=limit_traffic.combine(limiters,keys,status)
  ```

### 动态

OpenResty通过脚本语言Lua实现了动态，即程序在运行时，可以在不重新加载的情况下，修改参数、配置，甚至修改自身的代码。可以通过将字符串转换为函数，实现动态加载代码。

```lua
local s=[[ngx.say('hello world')]]
-- loadstring将字符串加载为函数
local func,err=loadstring(s)
func()
```

- FaaS：函数即服务

  ```lua
  local s=[[
  return function()
  	ngx.say("hello world")
  end
  ]]
  local func1,err=loadstring(s)
  -- 函数是一等公民，应该让函数在沙盒里面运行
  local ret,func=pcall(func1)
  func()
  ```

- 边缘计算，将计算移动到CDN边缘节点，能更快的响应用户的请求。由边缘节点处理原始数据，然后汇总给远端的服务器，减少数据传输量。

  - 从数值数据库集群中获取到有变化的代码文件(后台timer轮询或者发布订阅模式)。
  - 用更新的代码文件替换本地磁盘的旧文件，然后使用loadstring和pcall方式来更新内存中加载的缓存。

- 动态上游：`lua-resty-core`提供`ngx.balancer`来设置上游，在balancer阶段运行。

  ```lua
  balancer_by_lua_block{
      local balancer = require("ngx.balancer")
      local host='127.0.0.2'
      local port=8000
      -- 不支持域名
      local ok,err = balancer.set_current_peer(host,port)
      if not ok then
          ngx.log(ngx.ERR,'failed',err)
          return ngx.exit(500)
      end
  }
  ```

  balancer前面还需要两个功能：

  - 上游选择算法：一致性哈希还是roundrobin
  - 上游健康检查机制

  <https://github.com/openresty/lua-resty-balancer>提供了`resty.chash`和`resty.roundrobin`来解决第一个问题，`lua-resty-upstream-healthcheck`来解决第二个问题，但是只实现了主动健康检查（主动检查通过timer定期询问，被动检查由终端的请求触发，分析上游返回值，判断是否健康）。通常使用`lua-resty-healthcheck`完成上游的健康检查，可以参考[APISIX中](<https://github.com/apache/incubator-apisix/blob/master/lua/apisix/balancer.lua>)，动态上游检查的完整实现。
