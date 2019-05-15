# 文件操作

##　文件

- 流：输入或输出时连续的字节序列。
- `stdio.h`中提供了三个标准流
  - `stdin`：标准输入流，默认为键盘。
  - `stdout`：标准输出流，默认为屏幕。
  - `stderr`：标准错误流，默认为屏幕。
- 运行程序时可以通过
  - `程序 > 输出流`或`程序 1>输出`重定向输出流。
  - `程序 < 输入流`或`程序 0<输出`重定向输入流。
  - 程序 `2>错误`重定向错误输出流。
- 文本文件：文件内容由字符组成，例如：`12345`是由字符`1`、`2`、`3`、`4`、`5`组成，占5个字节。
- 二进制文件：文件存储目标值的二进制码，例如`12345`只为一个int大小，占2个字节。

## 文件操作

- 文件指针：`FILE *file`，用于指向包含文件信息的数据对象。
- 打开：`FILE *fopen(const char *restrict filename,const char *restrict mode)`，打开目标文件变为流，打开失败时返回空指针(一定要检测)。
  - mode：
    - `r`：读。
    - `w`：重新写(文件存在则删除内容重写，不存在则创建文件)。
    - `a`：追加写入。
    - `+`：添加读写中缺失功能，`a+`为追加写入、并能读(追加写入功能时，默认为`w`)。
    - `b`：二进制模式。
- 关闭：`int fclose(FILE *stream)`：关闭目标流，成功则返回`0`，失败返回`EOF`。
- 删除：`remove(const char *filename)`
- 重命名：`rename(const char *filename1,const char *filename2)`
- 附加流：`FILE *freopen(const char *restrict filename,const char *restrict mode,FILE *restrict stream)`：可以将stream与filename的流相关联，这样所有对stream的操作将作用到filename的流中。

```c
#include <stdio.h>

int main(void) {
    FILE *file;
    file = fopen("./out.file", "w+");
    fputs("hi", file);
    fclose(file);
	# 将会在out.file中写入hello
    file = freopen("out.file", "w+", stdout);
    printf("hello");
    return 0;
}
```

## 从命令行中获得参数

通过`程序 参数`可以向`main`函数传递参数，`main`函数通过形参获得参数信息。

```c
#include <stdio.h>
//argc为argv的长度，argv存储将整个命令按空格隔开的字符串数组。
int main(int argc, char *argv[]) {
    printf("%d\n", argc);
    for (int i = 0; i < argc; i++) {
        printf("%s\n", argv[i]);
    }
    return 0;
}
```

## 文件缓冲操作

由于IO读取速度较慢，为了提供性能，为流提供缓冲，当把缓冲区存储慢后，在写入或读取。缓冲类型有块缓冲、行缓冲(按行进行读写)和无缓冲(立即响应)。

- `fflush(FILE *fp)`：刷新指定文件的缓冲区，当fp为`NULL`时，数学所以输出流，成功返回0，失败返回`EOF`。
- `setvbuf (FILE *restrict stream, char *restrict buf,int mode, int n)`：将流`stream`的缓冲区指定为`buf`，并通过`mode`指定缓冲类型，`n`指定缓冲区大小。
  - `_IOFBF`：块缓冲。
  - `_IOLBF`：行缓冲。
  - `_IONBF`：无缓冲。

## 打开文件流程解读

`fopen`打开文件时，会根据`mode`为其创建相应的缓冲区，并创建一个文件对象，会存储以下字段：

- 当前文件位置
- 缓冲区位置
- 错误指示器：当读写出错时，会设置该指示器。
- 文件末尾指示器：当文件读完后，会设置该指示器。
- 文件位置指示器：已经读取的字节数。
- 缓冲区计数器

然后返回文件指针，指向该对象。

因此当`scanf`读取时，返回成功读取项数量和预期不同时，可以根据`int feod(FILE *stream)`来判断流是否读完了(判断文件末尾指示器)或`int ferror(FILE *stream)`判断是否读取错误，如果二者皆排除，则意味着是匹配失败。

`stdio.h`还提供`clearerr(FILE *stream)`来重置错误指示器和文件末尾指示器。

## 文件读写位置操作

`stdio.h`中提供对五种方法用于操作文件读写位置，以二进制打开时，这五种方法将其视作为以字节为单位的数组。

- `int fseek(FILE *stream,long int offset,int whence)`：将指定流的读写位置从`whence`的位置偏移`offset`个字节。
  - `SEEK_SET`：文件起始处。
  - `SEEK_END`：文件结束处。
  - `SEEK_CUR`：文件当前位置。
- `long int ftell(FILE *stream)`：获得指定流当前的读写位置。
- `int fsetpos(FILE *stream,const fpos_t *pos)`：同`fseek`，用于处理超大文件。
- `int fgetpos(FILE *restrict stream,fpost_t *restrict pos)`：同`ftell`，用于处理超大文件。
- `void rewind(FILE *stream)`：将文件读写位置设置到文件起始位置。