# 预编译

> 将C语言的源码变成可执行文件时，会经历三个阶段：预处理——>编译——>链接，这边文章着重介绍预编译的常用的知识点。

## 简介

预编译的操作类似一个自动化的编辑器，其目的是为编译提供良好的原材料，其需要经历如下流程：

- 使用字符集对字符字面常量进行映射。
- 将使用`\`续行的多行变为一行。
- 将注释替换为空格。
- 根据预编译执行进行处理。

通常预处理和编译操作是为一体的，但是某些编译器提供查看方法，这里以`gcc`举例。

```c
#define Bool int
#define PI 3.1415
Bool main(void) {
    //this is single annotation
    float pi = PI;
    /*
     * this is multi annotation
     *
     */
    return 0;
}
```

通过`gcc -E`可以查看预编译后的结果。

![](/home/martin/Documents/学习笔记/编程语言/C Prime Plus笔记/预编译/预编译示例.png)

## 预处理指令类型

根据其作用可以将预处理指令分为4大类：

- 宏操作：`#define`、`#undef`
- 文件包含：`#include`
- 条件编译：`#if`、`#else`、`#elif`、`#ifdef`、`#ifndef`、`#endif`
- 提示：`#error`、`#line`、`#pragma`

## 宏

通过`#define`定义了宏后，预处理器对宏进行宏展开时，执行替换操作，将所有的宏替换为相应的值，处理结果请看简介。

宏定义分为两种：简单宏定义、宏函数。

### 简单宏定义

- 定义：`#define 标识符 替换值`

```c
#define PI 3.14
```

- 简单宏定义主要用于定义各种明示常量，其优势如下：
  - 通过合理的命名避免魔法数。
  - 方便进行统一修改。
- 取消宏：`#undef 标识符`

### 宏函数

- 定义：`#define 宏函数名(参数) 表达式`

```c
#define MAX(x,y) x>y?x:y
```

- 优点：
  - 由于宏的替换特性，因此可以避免掉函数调用前后的准备与清理过程，提高效率。
  - 宏函数的参数没有类型检查，可以传入任意值。
- 缺点：
  - 成也替换，败也替换，如果大量调用宏函数，会导致编译出来的文件容量增加。
  - 没有类型检查，容易传递不支持的值。
  - 宏函数中不能对参数的值进行修改，会导致其结果不可预知。
  - 不能使用指针指向宏(还没到编译)。
- 定义参数可变宏函数：`#define 宏函数名(参数,...) 表达式`。

```c
#define ECHO(format,...) printf(format,__VA_ARGS__)
```

### 泛型选择(C11)

C11中提供`_Generic`用于泛型选择。

```c
# 当x为int 时，返回0
#define TYPE(x) _Generic(x,\
	int:0,\
	float:1,\
	double:2,\
	default;4\
)(x)
```

### 内联函数(C99)

C99中提供内联函数来实现和宏函数相同的功能，内联函数必须和调用处在同一文件中。

```c
inline static eatline(){	//既是定义也是原型
    //清理掉输入流该行其他字符
    while (getchar()!='\n') continue;
}
```

### 扩展

- `#参数名`：生成参数的字符串字面量。
- `参数名##a或a##参数名`：用于粘合，生成标识符：`参数名a a参数名`

```c
#include <stdio.h>

#define MAX(type) type type##_max(type x,type y) \
{ return x>y?x:y;}

//宏展开时，展开为int_max(int x,int y) { return x>y?x:y;}
MAX(int)

int main(void) {
    int x = 3;
    int y = 4;
    printf("%d", int_max(x, y));
    return 0;
}
```

- 宏的作用范围从定义位置到`#undef`或文件尾。
- 常量表达式的宏一定要再最外层加括号，否则宏展开的结果出乎意料。

```c
#define A 3+4

int main(void) {
    int result;
    result=A*A;
    return 0;
}
// 展开结果
// int main(void) {
//    int result;
//    result=3+4*3+4;
//    return 0;
//}
```

- 常见预定义宏
  - `__STDC__`：当编译器为C89或C99标准时，为1。
  - `__LINE__`：行号。
  - `__FILE__`：文件名。
  - `__func__`：实际上不是宏，表示当前的函数名。

## 文件包含

通过`#include`指令引入头文件，预处理器会将文件的内容插入到当前指令的位置。

- 指令格式：
  - `#include <文件名>`：标准库文件，从系统头文件目录查找(`/usr/include`)。
  - `#include “文件名”`：自编写文件，先从当前目录查找，再去系统目录。

```c
#include <stdio.h>
// 预处理结果
//# 1 "main.c"
//# 1 "<built-in>"
//# 1 "<command-line>"
//# 31 "<command-line>"
//# 1 "/usr/include/stdc-predef.h" 1 3 4
//# 32 "<command-line>" 2
//# 1 "main.c"
//# 1 "/usr/include/stdio.h" 1 3 4
//# 27 "/usr/include/stdio.h" 3 4
// .....
```

- 使用场景
  - 共享宏定义与类型定义。
  - 共享函数原型定义。
    - 函数调用时需要通过函数原型进行类型检查。
    - 函数定义时需要函数原型进行类型匹配。
    - 可以将函数原型存放在头文件中，调用和定义处都进行引用。
  - 共享变量声明。
    - 定义处对变量进行定义。
    - 调用处需要通过`extern`声明变量来自其他文件。
    - 将声明存放到头文件中，通过在定义处引入头文件，确保声明的类型与定义类型相同。
  - 防止重复加载头文件
    - 同一个文件中多次加载同一个头文件会出现冲突(相同定义多次出现)。
    - 通过`#ifndef`和`#endif`封闭文件内容，进行条件加载。

## 条件编译

预处理器提供`#if`、`#else`、`#elif`、`#ifdef`、`#ifndef`、`#endif`指令来进行条件判断。

- `#if 常量表达式 内容 #endif` ：当常量表达式值为1，则保留内容。
- `#ifdef 标识符 内容 #endif `:当标识符存在时，保留内容。与之对应的还有`#ifndef`，用于判断标识符不存在。
- `defined(标识符)`：`defined`运算符用于判断标识符是否存在，存在返回1，否则为0。
- 多条件判断：`#else   #elif`

