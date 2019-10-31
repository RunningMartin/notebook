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

