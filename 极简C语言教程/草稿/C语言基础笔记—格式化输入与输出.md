# 格式化输入与输出

## 格式化输出

`stdio.h`的`printf`和`fprintf`函数通过提供的格式化字符串进行格式化输出。

- `printf(const char * restrict format,....)`：往`stdout`写入内容。
- `fprintf(FILE *restrict stream, const char * restrict format,....)`：往指定的stream中写入内容。
- 二者写入成功后，返回写入字符数，若失败，则返回负值。

- format的格式为：`%[标志符][m].[n][长度修饰符][转换说明符]`
  - 标志符：
    - `+`：显示正负。
    - `-`：左对齐。
    - `0`：当输出长度小于m时，以0填充。
    - `空格`：显示正负，用空格替换`+`。
    - `#`：配合转换说明符，输出相应的格式。
  - m：输出内容的最小长度，默认用空格补全，若为`*`则有对应的参数位提供。
  - n：
    - 针对整型(`d、i、o、u、x、X`)：最小位数。
    - 针对浮点型(`f、F、a、A、e、E`)：为小数点后位数。
    - 针对`G、g`：数字个数。
    - 字符串：字符最大输出个数。
    - `*`：由参数控制。
  - 整数转换说明符
    - `d、i`：十进制。
    - `u`：无符号十进制。
    - `o`：八进制。
    - `x、X`：十六进制。
  - 浮点型转换说明符
    - `f、F`：`double`的浮点数，也支持`float`。
    - `e、E`：十进制科学计数法。
    - `a、A`：十六进制科学计数法。
    - `g、G`：自动选择`F`或`E`。
  - 字符说明符
    - `%`：输出`%`。
    - `s`：字符串。
    - `c`：字符
  - 其他转换说明符
    - `p`：指针地址。
- 示例

```c
#include <stdio.h>

int main(void) {
    printf("format\n");
    printf("+:%10d\n", 10);
    printf("-:%-10d\n", 10);
    printf("0:%010d\n", 10);
    printf(" :% -10d\n", 10);
    printf(" :% -10d\n", -10);
    printf("#:%#10X\n", 10);

    printf("m:\n");
    printf("10:%10d\n", 10);
    printf("*:%*d\n", 5, 10);

    printf("n:\n");
    printf("int:%5.3d\n", 12);
    printf("float:%5.3f\n", 1.2345);
    printf("G:%5.3g\n", 1.2345);
    printf("string:%5.3s\n", "abcdf");
    printf("*:%5.*d\n", 3, 12);

    printf("int type:d\n");
    printf("%d\n", 10);
    printf("%d\n", -10);

    printf("int type:i\n");
    printf("%i\n", 10);
    printf("%i\n", -10);

    printf("int type:u\n");
    printf("%u\n", 10);
    printf("%u\n", -10);

    printf("int type:o\n");
    printf("%o\n", 10);

    printf("int type:x\n");
    printf("%x\n", 10);
    printf("%X\n", 10);

    printf("float:\n");
    printf("f:%f\n", 12.345);
    printf("e:%e\n", 12.345);
    printf("a:%a\n", 12.345);
    printf("g:%g\n", 1.234);
    printf("g:%g\n", 12444456.34544444);

    printf("char：\n");
    printf("%%\n");
    printf("%s\n", "abcd d");
    printf("%c\n", 'a');

    printf("point：\n");
    int m;
    printf("point:%p\n", &m);
}
```

## 格式化输入

`stdio.h`的`scanf`和`fscanf`函数通过提供的格式化字符串进行格式化输出。

- `scanf(const char * restrict format,....)`：从`stdin`读取内容。
- `fscanf(FILE *restrict stream, const char * restrict format,....)`：往指定的stream中写入内容。
- 返回读入数据项个数。
- 当不匹配时，将把不匹配的字符放回，并返回读取字符数。
- 格式化串说明
  - 会跳过开始的空白字符。
  - 空白字符能匹配>=0个空白字符。
  - 非空白字符，要求输入流中有字符相匹配。
- format格式：`%[最大长度][长度修饰符][转换说明符]`
  - 赋值屏蔽：`*`，读入但不进行赋值。
  - 最大长度：限制匹配的最大读取字符数(刚开始空白不算)。
  - 转换说明符：同`printf`。
    - `[]`提供匹配字符。
    - `[^]`：提供不匹配的字符。
    - 匹配负数时：`-`。
- 示例

```c
#include <stdio.h>

int main(void) {
    printf("format:*\n");
    int p;
    scanf("%*d,%d", &p);
    printf("%d", p);
}
```

