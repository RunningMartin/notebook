# 字符输入与输出

## 按字符输出函数

`stdio.h`提供三种函数写入单个字符，当写入错误时，会设置错误指示器并返回EOF，成功则返回写入字符数。

- `int fputc(int c ,FILE *stream)`：函数，在指定流中输出。
- `int putc(int c ,FILE *stream)`：宏函数，在指定流中输出。
- `int putchar(int c )`：在标准输出流`stdout`中写字符。

## 按字符输入函数

`stdio.h`提供三种函数读单个字符，当读取错误或文件末尾时，会设置相应指示器并返回EOF，成功则返回字符。

- `int fgetc(FILE *stream)`：函数，从指定流中读取。
- `int getc(FILE *stream)`：宏函数，从指定流中读取。
- `int getchar(void)`：从标准输入流`stdin`中读取字符。
- `int ungetc(int c,FILE *stream)`：把字符返回流中，并清楚文件末尾指示器，可以用来预先取数据。

## 按行输出函数

`stdio.h`提供两种函数按行输出字符串，当遇到错误时，会返回EOF，成功则返回非负数。

- `int puts(const char *s)`：在标准输出流`stdout`中按行写入字符串。
- `int fputs(const char *restrict s,FILE *restrict stream)`：向指定流中写入数据。

## 按行输入函数

`stdio.h`提供两种函数按行读取字符串，当遇到错误时，会返回空指针，成功则返回第一个实参。

- `char *gets(char *s)`：在标准输入流`stdin`中按行读取字符串，存储到`s`指向的字符串数组中，不会存储换行符，其有一个缺陷，如果行字符数量大于`s`的数组大小，则会导致使用非该数组的内存。
- `char *fgets(char *restrict s,int n,FILE *restrict stream)`：向指定流中写入数据，``n`指定读取字符最大个数，如果换行符的位置在`n`之内，则会存储换行符。

## 按块输入输出

`stdio.h`提供两种函数按行读取字符串，当遇到错误时，会返回空指针，成功则返回第一个实参。

- `size_t fread(void *restrict prt,size_t size,size_t nmemb,FILE *restrict stream)`
- `size_t fwrite(const void *restrict prt,size_t size,size_t nmemb,FILE *restrict stream)`
- `fread`根据`size`指定元素大小(字节)、从指定的流中读取`nmemb`个元素，存入`prt`指定的数组中，返回值为实际读取元素个数。
- `fwrite`根据`size`指定元素大小(字节)、将`prt`数组中前`nmemb`个元素，写入指定流中，返回值为实际写入元素个数。

## 字符串输入输出

`stdio.h`不仅提供对流今天输入输出，还提供了将字符串作为流，进行输入输出。

- `int sprintf(char * restrict s,const char *restrict format,...)`：同`printf`，写入字符串`s`中，返回写入字符数量，失败返回负数。
- `int snprintf(char * restrict s,size_t n,const char *restrict format,...)`：通过`n`限制写入字符串数量(包括空字符)，成功则返回写入字符数(不包含空字符)，失败返回负数。
- `int sscanf(char * restrict s,const char *restrict format,...)`：从字符串`s`中，按格式读取数据。