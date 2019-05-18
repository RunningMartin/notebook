# 位操作

## 位字段

- 位字段：通过结构来创建只占一位的字段，字段类型为`signed int` 或`unsigned int` ，优势为节约空间，比如：哈弗曼编码。

```c
struct {
    unsigned int autfd:1;	// 占1位
    unsigned int bldfc:2;	// 占2位
    unsigned int 	  :4;	// 占4位的间隔
    unsigned int itals:8;	// 占8位
} prnt;
// prnt.autfd=0 或1
// prnt占一个int大小的内存单元，每个字段占一位。
```

- C99中添加了`_Bool`也可使用在位字段中，通过`stdbool.h`可以使用`bool`

## 字节对齐

- [对齐](<https://www.cnblogs.com/clover-toeic/p/3853132.html>)