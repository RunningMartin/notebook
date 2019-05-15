# 极简C语言教程—第1节 hello world

让我们使用编程中最经典的程序`hello world`来开启C语言的编程之路，并且通过其了解C语言程序的结构。

## hello world

- 编码

```c
#include<stdio.h>

void main(void){
    printf("hello world");
}
```

- 进行编译\==>链接\==>运行后，你的显示器将会有`hello world`字符的显示。

## 分析

我们的第一个程序虽然只有6行，但其体现了C语言程序的机构，这里先分析一下。

- `#include<stdio.h>`：`include`为预处理器命令，预处理器会引入`stdio.h`的内容，详细了解请阅读后面的预处理器篇。这里使用`#include<stdio.h>`来引入`printf`的函数原型，通过这个函数能让我们直观的观察程序的原因。
- `main`函数是一个十分特殊的函数，这个函数由操作系统调用，他是整个程序的入口。

## 总结

- `main`函数为一个特殊函数，为整个程序的入口函数。
- `printf`函数能在显示器上打印数据。
