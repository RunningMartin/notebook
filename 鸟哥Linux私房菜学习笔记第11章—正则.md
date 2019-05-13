# 正则表达式

## 基础正则表达式

| 正则      | 意义                                                   |
| --------- | ------------------------------------------------------ |
| `^word`   | 进行行首匹配字符。`^martin`，匹配以martin开头的行。    |
| `word$`   | 进行行尾匹配字符。`martin$`，匹配与martin结尾的行。    |
| `\`       | 转移字符，`\'`，匹配字符`'`。                          |
| `[list]`  | 提供可能匹配到的字符。`[abc]`，匹配a或b或c             |
| `[^list]` | 不匹配提供的字符。`[^abc]`，不匹配a、b、c              |
| `.`       | 任意字符。                                             |
| `*`       | \>=0个字符。                                           |
| `{n,m}`   | 提供重复次数的最小值与最大值，使用时`{}`要添加转移符。 |

## 正则表达式工具

### grep

```bash
# -n 直接从文本中匹配
➜  Desktop grep -n '^aa' test   
2:aabcd
➜  Desktop grep -n 'a\{1,2\}' test
1:abcdefg
2:aabcd
➜  Desktop ll |grep 's\{1,2\}'
-rw-r--r-- 1 martin martin 2.6M 5月  12 21:51 sslkey.log
-rw-r--r-- 1 martin martin   14 5月  12 22:19 test
```

### sed

- 提供增删改查功能

```bash
# sed [选项] [动作]
# 选项
# -i 直接作用于文本
# 常用动作
# a：后一行新增行 '1a abc' 在第一行后插入一行abc
# c：整行替换 '3,5c hello' 将第三行到第五行替换为hello
# d：删除目标行，'3,5d' 将第三行到第五行删除
# i：前一行新增行 '1a abc' 在第一行后插入一行abc
# p：打印
# s：使用正则表达式替换 '1,20s/old/new/g' 将1到20行的old替换为new
➜  Desktop cat test       
abcdefg
aabcd
12345
67890
# 删除
➜  Desktop sed -i '1,2d' test                                              
➜  Desktop cat test          
12345
67890
# 新增
➜  Desktop sed -i '1a hello' test
➜  Desktop cat test              
12345
hello
67890
# 整行替换
➜  Desktop sed -i '2,3c hello martin' test
➜  Desktop cat test                       
12345
hello martin
# 打印
➜  Desktop sed -n '1p' test
12345
➜  Desktop cat test
12345
hello martin
# 前一行新增行
➜  Desktop sed -i '1i mar' test
➜  Desktop cat test            
mar
12345
hello martin
# 正则替换
➜  Desktop sed -i '1,$s/mar/fang/g' test 
➜  Desktop cat test                     
fang
12345
hello fangtin
```

### awk

- 格式：`awk ‘条件类型1{动作1}条件类型2{动作2}....’ filename`，其中条件是可以省略的。
- awk通常将一行数据按分隔符(默认空格或tab键)拆分为多个字段处理。

```bash
[root@HN_0_0 ~]# last -n 5 |awk '{print $1 "\t" $3}'
# $0 代表整行数据 $1 代表该行第一列
root    100.99.65.176
root    100.99.65.176
root    100.99.65.176
root    10.183.177.90
root    10.169.207.67
```

- 常用变量

| 变量 | 说明                    |
| ---- | ----------------------- |
| `NF` | 每行中拥有的字段总数    |
| `NR` | 当前处理第几行          |
| `FS` | 分隔符，默认空格或tab键 |

```bash
[root@HN_0_0 ~]# last -n 5 |awk '{print "colume:"NR "\t" $1}'
colume:1        root
colume:2        root
colume:3        root
colume:4        root
colume:5        root
colume:6
colume:7        wtmp
```

- 逻辑运算符

| 运算符 | 含义     |
| ------ | -------- |
| `>`    | 大于     |
| `<`    | 小于     |
| `>=`   | 大于等于 |
| `<=`   | 小于等于 |
| `==`   | 等于     |
| `!=`   | 不等于   |

## 扩展正则表达式

| 正则              | 含义                                                   |
| ----------------- | ------------------------------------------------------ |
| `+`               | 大于等于1个字符                                        |
| `？`              | 0个或1个字符                                           |
| `表达式1|表达式2` | 表达式1或表达式2                                       |
| `(表达式)`        | 将表达式作为一个整体，([abc]\|[ABC])+，不分大小匹配abc |

- 表达式工具`egrep`或`grep -E`

## 文件格式化与相关处理

- 格式化打印：`printf '格式' 内容`，其格式支持C语言的常用格式化字符串，`printf`不是管道命令，所以使用其他命令的结果时需要使用`$(命令)`。

```bash
➜  Desktop cat test 
name chinese english
martin 75 70
➜  Desktop printf '%s\t%s\t%s\t\n' $(cat test) 
name	chinese	english	
martin	75	70	
```

- 数据处理工具`awk`
- 文本对比工具
  - `diff 文本1 文本2`：按行对比文本1和文本2的区别。
  - `cmp 文本1 文本2`：按字节对比两个文本之间的区别。
