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

## 元表

## 协程

## 文件

## 错误处理

## 调试

## 垃圾回收

## 面对对象

## 数据库访问
