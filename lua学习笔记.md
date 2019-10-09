# Lua学习

## 注释

- 单行注释：`--`

- 多行注释：

  ```lua
  --[[
  print('zhushi 1')
  --]]
  
  --[=[
  print('zhushi 2')
  ]=]
  ```

- 标识符标准：字母或下划线开头，只能使用字母、数字、下划线

- 全局变量：变量默认为全局变量，访问一个不存在的变量，结果为`nil`，删除一个变量，只需要赋值为`nil`。

## 数据类型

### `nil`

`nil`表示无效数据类型。

```lua
print(type(nil))
nil
print(type(type(nil)))
string
```

删除一个变量，只需要赋值为`nil`。比较一个值是否是`nil`，使用`type(nil)=='nil'`。

### boolean

布尔量，`false`和`true`。

`false`和`nil`被视作为假，其余为真。

```lua
print(type(true))
print(type(false))
print(type(nil))
 
if false or nil then
    print("至少有一个是 true")
else
    print("false 和 nil 都为 false!")
end
```

### number

双精度类型的实浮点数。

### string

字符串。

```lua
-- 单行字符串
string1='this is string1'
string2='this is string2'
print(string1)
print(string2)
-- 多行字符串
string3=[[
第一行
第二行
]]
print(string3)
-- 针对数学字符串进行算术操作，会尝试将字符串转换为数字
'2'+'1'
3
-- 获取字符串长度用#
print(#'nihao')
```

### 表

表是一个kv结构，其key可以为数字和字符串，默认为从1开始的下标。

```lua
a={1,2,3,4}
for k, v in pairs(a) do
    print(k .. " : " .. v)
end
-- 1:1 2:2 3:3 4:4
a = {}
a["key"] = "value"
a[10] = 22
for k, v in pairs(a) do
    print(k .. " : " .. v)
end
-- key:value 10:22
-- key不存在是对应nil
-- 表的创建方法
a={1,2,3}
a={b='1',c='2'}
tab={
[1]='a',
[2]='b',
[3]='c'
}
-- 表中的数据是按key的哈希值排序
```

### function

由C或Lua编写的函数。函数存储在变量中。

```lua
function factorial1(n)
    if n == 0 then
        return 1
    else
        return n * factorial1(n - 1)
    end
end
print(factorial1(5))
factorial2 = factorial1
print(factorial2(5))
-- 匿名函数
function testFun(tab,fun)
	for k ,v in pairs(tab) do
		print(fun(k,v))
	end
end


tab={key1="val1",key2="val2"}
--function是匿名函数
testFun(tab,
function(key,val)
	return key.."="..val
end
);
```

### userdata

存储在变量中的C数据结构。

### thread

实现协程。

## 变量

### 变量

Lua变量有三种类型：全局变量、局部变量、表中域。Lua中变量默认为全局变量，声明局部变量请使用local，局部变量的作用域是声明位置到所在语句块结束。尽量使用局部变量，避免命名冲突，并且访问局部变量速度更快。

```lua
a='a'
local b='b'

function joke()
	print('in joke')
	print(a)
	print(b)
	c='c'
	local d='d'
	print(c)
	print(d)
end

joke()
print('out joke')
print(c,d)
```

### 赋值语句

```lua
-- 赋值
a=1
-- 多变量赋值
a,b=1,2
--连接字符串
a='a'..'b'
-- 交换变量
a,b=b,a
-- 多变量赋值是，必须依次对每个变量赋值
a,b,c=1
-- a=1,b=nil,c=nil
```

### 索引

表中可以使用`[]`或`.`替换索引。`t[i]等价于t.i`。

```lua
> site = {}
> site["key"] = "www.runoob.com"
> print(site["key"])
www.runoob.com
> print(site.key)
www.runoob.com
```

## 循环

### while循环

```lua
a=10
while( a < 20 )
do
   print("a 的值为:", a)
   a = a+1
end
```

### for循环

```lua
--数值for
--[=[
for var=start_value,end_value,step do  
    <执行体>  
end  
]=]

function f(x)  
    print("function")  
    return x*2  
end
-- f(5)只执行一次
for i=1,f(5) do print(i)  
end

-- 泛型for
--[=[
fir i,v in ipairs(tables) do
   	<执行体>
end
]=]
a = {"one", "two", "three"}
for i, v in ipairs(a) do
    print(i, v)
end
```

### 执行循环

```lua
-- 执行循环，类似do while，当条件为真时，退出循环
repeat
    语句
until(条件)
--[ 执行循环 --]
a = 10
repeat
   print("a的值为:", a)
   a = a + 1
until( a > 15 )
```

### 嵌套循环

```lua
-- for、while、repeat until支持 嵌套循环
-- 退出循环，break 退出当前循环
-- continue 
for i = 10, 1, -1 do
  repeat
    if i == 5 then
      print("continue code here")
      break
    end
    print(i, "loop code here")
  until true
end
```

## 流程控制

### if语句

```lua
if(布尔表达式)
then
    <执行体>
end
```

### if else

```lua
if(布尔表达式)
then
    <执行体>
else
    <执行体>
end

-- if elseif else
if(布尔表达式)
then
    <执行体>
elseif(表达式)
then
    <执行体>
else
    <执行体>
end
```

### if 嵌套

```lua
if( 布尔表达式 1)
then
   --[ 布尔表达式 1 为 true 时执行该语句块 --]
   if(布尔表达式 2)
   then
      --[ 布尔表达式 2 为 true 时执行该语句块 --]
   end
end
```

## 函数

### 定义函数

```lua
-- 函数默认为全局函数，如果想定义局部函数，使用local
-- return 返回值，多个返回值用逗号隔开。
optional_function_scope function function_name( argument1, argument2, argument3..., argumentn)
    function_body
    return result_params_comma_separated
end

--实例
function max(num1,num2)
	if (num1>num2) then
		result = num1
	else
		result=num2
	end
	return result
end

print(max(5,4))
```

### 可变参数

Lua函数和C语言类似，使用`...`接受可变参数，只能放在最后的位置。

```lua
function average(...)
	-- 创建一个表
	local args={...}
	local sum=0
	for i,v in ipairs(args) do
		sum=sum+v
	end
	print('参数总数'..#args)
	return sum/#args
end
print(average(1,2,3,4,5,6,7,8,9,10))
```

针对变长参数可能包含`nil`，可以使用`select`访问变长参数。

- `select('#', …)`：返回可变参数的长度。
- `select(n, …)` ：返回第n个参数。

```lua
function foo(...)
	print(#{...})
    for i = 1, select('#', ...) do  -->获取参数总数
        local arg = select(i, ...); -->读取参数
        print("arg", arg);
    end
end

foo(1, 2, nil,3, 4)
```

## 运算符

### 算术运算符

+、-、*、/、%、^(乘幂)、-(负号)

### 关系运算符

==、~=（不等于）、>、<、>=、<=

### 逻辑运算符

and、or、not(非)

### 其他

- `..`：连接两个字符串
- `#`：返回字符串或表长度

```lua
a={1,2,3,4,5}
print(#a)
a={}
a[1]=1
a[2]=2
a[5]=5
print(#a) --结果为2
```

注意，如果table中存在nil时，`#table`可能会返回任何一个指向`nil`值的前一位置下标。

```lua
a={1,2,3,4,5}
print("{1,2,3,4,5}的长度为："..#a)
a={}
a[1]=1
a[2]=2
a[5]=5
print("a={1:1,2:2,5:5}的长度为："..#a)

a={1,nil,3}
print("{1,nil,3}的长度为："..#a)
a={1,nil,3,nil}
print("{1,nil,3,nil}的长度为："..#a)
a={1,nil,3,nil,4}
print("{1,nil,3,nil,4}的长度为："..#a)
a={1,nil,3,nil,4,nil}
print("{1,nil,3,nil,4,nil}的长度为："..#a)

a={1,nil,3,nil,4,nil,5}
print("{1,nil,3,nil,4,nil,5}的长度为："..#a)
a={1,nil,3,nil,4,nil,5,nil}
print("{1,nil,3,nil,4,nil,5,nil}的长度为"..#a)
print("{1,nil,3,nil,4,nil,5,nil}的长度为："..select('#',a))
```



## 字符串

Lua中字符串表达形式有三种：`'字符串'`、`"字符串"`、`[[字符串]]`。

```lua
string1='string1'
string2="string2"
string3=[[
string3
string3
]]
print(string1)
print(string2)
print(string3)
```

Lua能通过转义符`\`，表示不能直接显示的字符：`\n`、`\0`(控制符)、`\ddd`(八进制表示字符)、`\xhh`(十六进制表达字符)。

### 字符串操作

```lua
strings='this is a world'
-- string.upper(argument)
print("upper:"..string.upper(strings))
-- 	string.lower(argument)
print("lower:"..string.lower(strings))
-- string.reverse(arg)
print("reverse:"..string.reverse(strings))
-- 	string.len(arg)
print("len:"..string.len(strings))
-- 	string.rep(string, n) 返回string n个拷贝
print("string rep 2:"..string.rep(strings,2))
-- string.gsub(mainString,findString,replaceString,num) num为次数，默认全部
print("gsub:"..string.gsub(strings,'a','一个'))
-- string.find (str, substr, [init, [end]]) 在init到end的范围内查找substr的索引，不存在返回nil
print("find:"..string.find(strings,'is'))
-- string.format(...) 类似C语言的printf
print("format:"..string.format('the value is %d',4))
-- string.char(arg) 整数转换为字符 ASCII
print("char:"..string.char(97,65))
-- string.byte(arg[,int]) 将字符转换为整数，默认第一个字符，int可以指定字符
print("byte:"..string.byte('abcd',1))
print("byte:"..string.byte('abcd',3))
-- string.gmatch(str, pattern) 返回一个迭代器，每次返回下一个pattern描述的子串，不存在返回nil
print("gmatch:")
for i in string.gmatch(strings,'is') do
print(i)
end

-- string.match(str, pattern,init) 返回一个迭代器，每次返回下一个pattern描述的子串，不存在返回nil
print("match:"..string.match(strings,'is'))
```

## 数组

### 一维数组

Lua中一维数组是由表组件的，可以通过下标直接访问。

```lua
array = {"Lua", "Tutorial"}

for i= 1, 2 do
   print(array[i])
end
```

### 多维数组

```lua
-- 初始化数组
array = {}
for i=1,3 do
   array[i] = {}
      for j=1,3 do
        -- 设置索引值，避免nil出现
         array[i][j] = i*j
      end
end

-- 访问数组
for i=1,3 do
   for j=1,3 do
      print(array[i][j])
   end
end
```

## 迭代器

迭代器用于遍历集合中的元素。

### 泛型for迭代器

for在自己的内部保存三个值：迭代函数、状态常量、控制控制变量。

```lua
array = {"Google", "Runoob"}

for key,value in ipairs(array)
do
   print(key, value)
end
--[=[
流程：
1、初始化，inpaires返回for所需的迭代函数、状态常量和控制变量
2、for使用状态常量和控制变量调用迭代函数
3、将迭代函数返回值赋值给变量列表
4、如果变量列表中第一个变量为nil，则循环结束，否则到第二步继续执行
]=]

-- 实现ipairs
function iter (a, i)
	print(a,i)
    i = i + 1
    local v = a[i]
    if v then
       return i, v
    end
end

function ipairs(a)
    return iter, a, 0
end

for i,j in ipairs({1,2,3})
do
	print(i,j)
end
--[=[
table: 0048BB60	0
1	1
table: 0048BB60	1
2	2
table: 0048BB60	2
3	3
table: 0048BB60	3
]=]
```

pairs和ipairs的区别

```lua
local tab={
[1]='a',
[4]='b',
[5]='c'
}
-- 将所有的值遍历出来
-- 将所有的信息打印出来
for i,v in pairs(tab)
do
	print(i,type(v),tab[i])
end
-- ipairs将按索引值递增遍历
-- 当i=2时，退出，因为为nil
for i,v in ipairs(tab)
do
	print(i,type(v),tab[i])
end
```

### 无状态迭代器

无状态的迭代器不会保留任何状态，每次迭代，迭代函数都是用两个变量（状态常量和控制变量）的值作为参数被调用，一个无状态的迭代器只利用这两个值可以获取下一个元素。

```lua
-- 无状态迭代器
function square(iteratorMaxCount,currentNumber)
	print("iteratorMaxCount："..iteratorMaxCount,"currentNumber："..currentNumber)
	if currentNumber<iteratorMaxCount
	then
		currentNumber = currentNumber+1
		return currentNumber, currentNumber*currentNumber
	end
end
-- square为迭代函数 3状态常量 0 控制变量 
for i,n in square,3,0
do
   print(i,n)
end
--[=[
结果：
iteratorMaxCount：3	currentNumber：0
1	1
iteratorMaxCount：3	currentNumber：1
2	4
iteratorMaxCount：3	currentNumber：2
3	9
iteratorMaxCount：3	currentNumber：3
]=]
```

### 多状态迭代器

迭代器会保留状态信息，下一次访问时，会返回上一次状态下的结果，通常采用闭包实现。

```lua
array = {"Google", "Runoob"}

function elementIterator (collection)
   local index = 0
   -- 长度
   local count = #collection 
   -- 闭包函数
   return function ()
      index = index + 1
      if index <= count
      then
         -- 返回迭代器的当前元素
         return collection[index]
      end
   end
end

for element in elementIterator(array)
do
   print(element)
end
```

## 表

### 表构造

```lua
-- 初始化
tab={1,2,3}
tab={b='1',c='2'}
tab={[1]='a',[2]='b',[3]='c'}
-- 修改值
tab['name']='martin'
-- 移除引用，垃圾回收自动删除
tab=nil
```

### 操作表

```lua
-- table.concat (table_a [, sep [, start [, end]]]):将table_a中从start到end的元素，以sep作为连接符，连接起来。
fruits = {"banana","orange","apple"}
-- 连接后的字符串 	banana3orange
print("连接后的字符串 ",table.concat(fruits,3,1,2))

-- table.insert (table_a, [pos,] value):在table_a的pos位置插入value，默认末尾
fruits = {"banana","orange","apple"}
table.insert(fruits,3)
for i,v in pairs(fruits)
do
	print(i,v)
end
-- table.remove (table [, pos]) 移除指定位置的元素 默认末尾
fruits = {"banana","orange","apple"}
print(table.remove(fruits,3))
for i,v in pairs(fruits)
do
	print(i,v)
end
-- table.sort (table [, comp]) 对给定的table进行升序排序。
fruits = {"banana","orange","apple","grapes"}
print("排序前")
for k,v in ipairs(fruits) do
        print(k,v)
end

table.sort(fruits)
print("排序后")
for k,v in ipairs(fruits) do
        print(k,v)
end
-- 自定义排序
my_table={3,1,2,5,8,6,5,7,8,9}
table.sort(my_table,function (a,b) return a>b end)

print("排序后")
for k,v in ipairs(my_table) do
	print(k,v)
end
```

### 表长度获取

表中存在索引中断时，`#`无法获取真实长度。

```lua
function table_leng(t)
  local leng=0
  for k, v in pairs(t) do
    leng=leng+1
  end
  return leng;
end
```

### table去重

```lua
function contains(tab,value)
	for k,v in pairs(tab)
	do
		if v==value
		then
			return true
		end
	end
	return false
end

function removeRepeated(tab)
	local new_table={}
	len=0
	for k,v in pairs(tab)
	do

		if not contains(new_table,v)
		then
			len=len+1
			new_table[len]=v
		end
	end
	return new_table
end

my_table={3,1,2,5,8,6,5,7,8,9}
removed=removeRepeated(my_table)

table.sort(removed)
print("去重后")
for k,v in pairs(removed) do
	print(v)
end
```



## 模块

模块类似一个封装好的库，通过将公共代码放在文件中，以API的形式展现出来，有利于代码的重用和降低代码耦合度与复杂度。

```lua
-- 模块是以表的形式展现出来的，因此只需创建一个表，最后返回这个表就行。
module = {}

-- 模块内部使用的函数
local function contains(tab,value)
	for k,v in pairs(tab)
	do
		if v==value
		then
			return true
		end
	end
	return false
end

-- 对外提供的api
function module.removeRepeated(tab)
	local new_table={}
	len=0
	for k,v in pairs(tab)
	do

		if not contains(new_table,v)
		then
			len=len+1
			new_table[len]=v
		end
	end
	return new_table
end

return module
```

模块的加载可以通过`require`来实现。

```lua
-- 加载模块
local sort_module=require('模块名')
my_table={3,1,2,5,8,6,5,7,8,9}
removed=sort_module.removeRepeated(my_table)

table.sort(removed)
print("去重后")
for k,v in pairs(removed) do
	print(v)
end
```

lua的加载机制由自己的文件路径加载策略，会尝试从Lua文件或C程序库中加载模块。`require('package_name')`，将从Lua文件或C程序库的位置加载模块。Lua文件的位置由全局变量`package.path`决定，Lua启动时，根据环境变量`LUA_PATH`初始化该变量。从路径中找到文件后，使用`package.loadfile`加载模块。
C程序库的位置由全局变量`package.cpath`决定，该变量使用`LUA_CPATH`进行初始化。在路径中找到文件后，使用`package.loadlib`加载。

Lua中使用C包前必须加载并连接，通过`loadlib(path,'package_name')`能实现动态连接。

```lua
local path = "/usr/local/lua/lib/libluasocket.so"
-- path 绝对路径 初始化函数，loadlib将返回初始化函数，不会打开库，因此加载失败或寻找失败时，loadlib将返回nil和错误信息
local f = loadlib(path, "luaopen_socket")
-- 检查是否存在错误
assser(f)
-- 打开库
f()
```

## 元表

Metatable允许我们修改table的行为，每个行为都关联了对应的元方法。比如两个table执行加法操作时，Lua会尝试对两个表进行相加，先检查表中是否有Metatable，然后检查是否有`__add`的字段，如果有，则调用。`__add`对应相应的元方法。

- **setmetatable(table,metatable)：**设置metatable，如果metatable已经存在`__metatable`键值，将失败
- **getmetatable(table):** 返回对象的元表(metatable)。

```lua
mytable = {}                          -- 普通表
mymetatable = {}                      -- 元表
setmetatable(mytable,mymetatable)     -- 把 mymetatable 设为 mytable 的元表
-- 等价于
mytable = setmetatable({},{})
```

### 常见的元方法

- `__index`。访问表中不存在的键，会使用`__index`来处理。如果`__index`包含一个表格，Lua在表格中查找相应的键。如果`__index`是一个函数，Lua会调用该函数，并传递table和键，如果键不存在，则返回nil。

  ```lua
  -- 表
  other={foo=3}
  table=setmetatable({},{__index=other})
  print(table.foo)
  print(table.bar)
  -- 函数
  print(table.foo)
  print(table.bar)
  ```

- `__newindex`。对表进行更新，如果给一个不存在的索引赋值，会使用`__newindex`来处理。如果存在，则调用该函数，而不进行赋值。如果`__newindex`是函数，将传递table、键、值

  ```lua
  -- 表
  metatable={}
  table=setmetatable({key1='key1'},{__newindex=metatable})
  print(table.key1)
  -- key1
  table.key2='key2'
  print(table.key2,metatable.key2)
  -- nil	key2
  table.key1='new key1'
  print(table.key1,metatable.key1)
  -- new key1	nil
  -- 函数
  table=setmetatable({key1='key1'},{__newindex=
  function(table,key,value)
  	rawset(table,key,value)
  end
  })
  print(table.key1,table.key2)
  -- key1	nil
  table.key1 = "new value"
  table.key2 = 4
  print(table.key1,table.key2)
  -- new value	4
  ```

- 常见操作符

  | 模式     | 描述               |
  | -------- | ------------------ |
  | __add    | 对应的运算符 '+'.  |
  | __sub    | 对应的运算符 '-'.  |
  | __mul    | 对应的运算符 '*'.  |
  | __div    | 对应的运算符 '/'.  |
  | __mod    | 对应的运算符 '%'.  |
  | __unm    | 对应的运算符 '-'.  |
  | __concat | 对应的运算符 '...' |
  | __eq     | 对应的运算符 '=='. |
  | __lt     | 对应的运算符 '<'.  |
  | __le     | 对应的运算符 '<='. |

- `__call`。定义作为函数时的动作。

  ```lua
  function table_maxn(t)
      local mn = 0
      for k, v in pairs(t) do
          if mn < k then
              mn = k
          end
      end
      return mn
  end
  
  -- 定义元方法__call
  mytable = setmetatable({10}, {
    __call = function(mytable, newtable)
          sum = 0
          for i = 1, table_maxn(mytable) do
                  sum = sum + mytable[i]
          end
      for i = 1, table_maxn(newtable) do
                  sum = sum + newtable[i]
          end
          return sum
    end
  })
  newtable = {10,20,30}
  print(mytable(newtable))
  ```

- `__tostring`。修改表的输出行为。

  ```lua
  mytable = setmetatable({ 10, 20, 30 }, {
    __tostring = function(mytable)
      sum = 0
      for k, v in pairs(mytable) do
                  sum = sum + v
          end
      return "表所有元素的和为 " .. sum
    end
  })
  print(mytable)
  ```

## 协程

协程和协程的区别是，多线程程序中，切成的切换由操作系统决定，而协程是基于单线程的，有用户决定切换。

| 方法                        | 描述                                         |
| --------------------------- | -------------------------------------------- |
| coroutine.create(function)  | 创建协程                                     |
| coroutine.resume(协程,参数) | 重启协程                                     |
| coroutine.yield()           | 将协程设置为挂起状态resume                   |
| coroutine.status()          | 查看协程的状态(dead，suspended，running)     |
| coroutine.wrap()            | 创建协程，返回一个函数，调用函数时，协程启动 |
| coroutine.running()         | 返回正在运行协程的线程号                     |

```lua
function foo (a)
    print("foo 函数输出", a)
	print('status',coroutine.status(co))
    return coroutine.yield(2 * a) -- 返回  2*a 的值 暂停，返回值为2*a
end

co = coroutine.create(function (a , b)
    print("第一次协同程序执行输出", a, b) -- co-body 1 10
    local r = foo(a + 1)

    print("第二次协同程序执行输出", r)
    -- yield 将接受resume 传入的参数
    local r, s = coroutine.yield(a + b, a - b)  -- a，b的值为第一次调用协同程序时传入

    print("第三次协同程序执行输出", r, s)
    return b, "结束协同程序"                   -- b的值为第二次调用协同程序时传入
end)
print('status',coroutine.status(co))
print("main", coroutine.resume(co, 1, 10)) -- true, 4
print('status',coroutine.status(co))
print("--分割线----")
print("main", coroutine.resume(co, "r")) -- true 11 -9
print("---分割线---")
print("main", coroutine.resume(co, "x", "y")) -- true 10 end
print("---分割线---")
print("main", coroutine.resume(co, "x", "y")) -- cannot resume dead coroutine
print("---分割线---")
```

## 文件

Lua中处理文件分别有两种模式：

- 简单模式：同C语言。
- 完全模式：使用文件句柄实现。

文件打开：`file=io.open(filename[,mode])`。mode有`r、w、a、+、b`。

### 简单模式

简单模式使用标准I/O或当前输入文件。

```lua
file=io.open('1.lua','r')
-- 设置默认输入文件
io.input(file)
print(io.read())

io.close()

file=io.open('1.lua','a')
-- 设置默认输入文件
io.output(file)
io.write('-- 1.lua 注释')

io.close()
```

`io.read`的参数：

| 模式         | 描述                                                         |
| ------------ | ------------------------------------------------------------ |
| "*n"         | 读取一个数字并返回它。例：file.read("*n")                    |
| "*a"         | 从当前位置读取整个文件。例：file.read("*a")                  |
| "*l"（默认） | 读取下一行，在文件尾 (EOF) 处返回 nil。例：file.read("*l")   |
| number       | 返回一个指定字符个数的字符串，或在 EOF 时返回 nil。例：file.read(5) |

其他io方法

- `io.tmpfile()`：返回一个临时文件，该文件已更新模式打开，程序结束时自动删除。
- `io.type(file)`：检查file是否是一个可用文件句柄。
- `io.flush()`：将缓存中的信息写入文件。
- `io.lines(filename)`：按行迭代文件，读完后，返回nil，但不关闭文件。

### 完全模式

完全模式不再采用`io.x`进行操作，而是`file:x`。

```lua
file = io.open("1.lua", "r")

-- 输出文件第一行
print(file:read())

-- 关闭打开的文件
file:close()

-- 以附加的方式打开只写文件
file = io.open("1.lua", "a")

-- 在文件最后一行添加 Lua 注释
file:write("--test")

-- 关闭打开的文件
file:close()
```

其他方法：

- file:seek(起点，偏移量)：移动游标，并返回最终文件位置(字节)，失败返回nil，默认为文件开头
  - "set": 从文件头开始
  - "cur": 从当前位置开始[默认]
  - "end": 从文件尾开始
  - offset:默认为0
- file:flush()：刷新缓存。
- io.lines(文件名)，按行迭代文件，读完后，返回nil，但不关闭文件。默认input指定的文件。

## 错误处理

Lua中有两种错误类型

- 语法错误
- 运行错误

语法错误会导致程序无法运行。而运行错误只有在运行时才会出现。处理错误时有以下几种方法：

```lua
-- 检查参数
local function add(a,b)
   assert(type(a) == "number", "a 不是一个数字")
   assert(type(b) == "number", "b 不是一个数字")
   return a+b
end
add(10)
-- 终止执行，返回错误信息
error (message [, level])
-- 默认值 level=1 ，错误位置为调用error的位置
-- level=2， 错误位置为调用error函数的函数
-- level=0，不添加错误位置信息
```

pcall、xpcall、debug

- pcall(函数,参数)：将使用参数去执行函数，并返回true(成功)、false(失败)与errorinfo。pcall能捕获执行中的错误。
- xpcall(函数，错误处理函数，参数)：如果出现错误，将调用错误处理函数，函数能通过`debug`获取错误的信息，常用的错误处理
  - `debug.debug`：返回Lua提示信息
  - `debug.traceback`：堆栈信息

```lua
xpcall(function(i) print(i) error('error..') end, function() print(debug.traceback()) end, 33)
-- 返回lua提示信息
xpcall(function(i) print(i) error('error..') end, function(error) print(error) end, 33)
```

## 调试

debug库

## 垃圾回收

lua内部采用增量标记-扫描搜集器实现了自动内存管理。通过两个数字(百分比)来控制垃圾回收循环。

- 垃圾收集器间歇率：开启新的一轮回收循环时需要等多久。当值小于100时，会立即开启新的循环。如果设置为200，则表示收集器会等到总内存使用量达到设置时的两倍才开始新的循环。
- 垃圾收集器步进倍率：收集器运作速度相对于内存分配速度的倍率。默认为200，如果小于100，则会导致收集器工作很慢。

Lua中可以使用collectgarbage(opt[,arg])来控制自动内存管理。

- **collectgarbage("collect"):** 执行一次完整的垃圾收集循环。
- **collectgarbage("count"):** 返回Lua使用的总内存数，单位为K。
- **collectgarbage("restart"):** 重启垃圾收集器的自动运行。
- **collectgarbage("setpause"):**设置垃圾收集器间歇率。 返回之前的间歇率。
- **collectgarbage("setstepmul"):** 设置垃圾收集器步进倍率。 返回之前的步进倍率。
- **collectgarbage("step"):** 单步运行垃圾收集器。 步长由arg控制。传入0，收集器步进（不可分割的）一步。传入非0值， 收集器收集相当于 Lua分配这些多K字节内存的工作。如果收集器结束一个循环将返回 true。
- **collectgarbage("stop"):** 停止垃圾收集器的运行。 

## 面对对象

面对对象有四大特征：

- 封装：function实现。
- 继承：metatable实现
- 多态：
- 抽象：table+function模拟。

`:`调用时，将table作为self传入。

```lua
-- 定义类名和属性名称
Rectangle = {area, length, breadth}

-- 派生类的方法 new
function Rectangle:new(length,breadth)
  local o ={length = 0, breadth = 0,area = length*breadth}
  setmetatable(o, self)
  self.__index = self
  return o
end

-- 派生类的方法 printArea
function Rectangle:printArea ()
  print("矩形面积为 ",self.area)
end

r = Rectangle:new(10,20)
b = Rectangle:new(20,20)

-- 访问属性
print(r.length)
-- 调用成员函数
r:printArea()


-- 访问属性
print(b.length)
-- 调用成员函数
b:printArea()

-- 访问属性
print(r.length)
-- 调用成员函数
r:printArea()
```

继承

```lua
-- Meta class
Shape = {aree}
-- 基础类方法 new
function Shape:new (side)
  o = {area = 0,side=side,area = side*side}
  setmetatable(o, self)
  self.__index = self
  return o
end
-- 基础类方法 printArea
function Shape:printArea ()
  print("面积为 ",self.area)
end

-- 继承父类
Square = Shape:new()
-- Derived class method new
function Square:new (o,side)
  o = o or Shape:new(o,side)
  setmetatable(o, self)
  self.__index = self
  return o
end
```

## 数据库访问

使用LuaSQL操作库，支持ODBC, ADO, Oracle, MySQL, SQLite 和 PostgreSQL。

```lua
luasql = require "luasql.mysql"

--创建环境对象
env = luasql.mysql()
--连接数据库
conn = env:connect("数据库名","用户名","密码","IP地址",端口)
--设置数据库的编码格式
conn:execute"SET NAMES UTF8"
--执行数据库操作
cur = conn:execute("select * from role")
row = cur:fetch({},"a")
--文件对象的创建
file = io.open("role.txt","w+");

while row do
    var = string.format("%d %s\n", row.id, row.name)
    print(var)
    file:write(var)
    row = cur:fetch(row,"a")
end

file:close()  --关闭文件对象
conn:close()  --关闭数据库连接
env:close()   --关闭数据库环境
```

