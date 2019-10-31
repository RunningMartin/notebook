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
