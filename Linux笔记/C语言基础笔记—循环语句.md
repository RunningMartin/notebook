# 循环语句

## while语句

- 格式

```c
//当条件为真时，执行语句块
whiel(条件) 
	语句块；
```

## do while语句

- 格式

```c
// 先执行语句块后再判断是否需要继续执行
do 
    语句块 
while(条件)；
```

## for语句

- 格式

```c
//当执行条件为真，执行语句块
for(初始化;执行条件;自变量变化)
    语句块
```

- 说明
  - 初始化、执行条件与自变量变化快能够使用逗号运算符执行多个表达式。

## 循环退出

- `break`：退出本层循环。
- `continue`：跳过该次循环。
- `goto 标签`：跳到指定标签。
  - 标签定义：`标签:语句`

