# Shell

## 变量定义

- 定义：`变量名="值"`
- 调用：`$变量名`或`${变量名}` 

```bash
[root@HN_0_0 ~]# NAME="martin"
[root@HN_0_0 ~]# echo $NAME
martin
[root@HN_0_0 ~]# echo ${NAME}
martin
```

- 引用其他命令的返回值：`$(命令)`或\`命令\`(反单引号：1左边的字符)

```bash
[root@HN_0_0 ~]# PID=$(pidof bash)
[root@HN_0_0 ~]# echo $PID
109834 109814 5410
```

- 变量添加内容：`变量名="$变量名"[间隔]值`或`变量名=${变量名}[间隔]值`

```bash
[root@HN_0_0 ~]# PID=${PID}:512
[root@HN_0_0 ~]# echo $PID
109834 109814 5410:51
```

- 设置环境变量：`export 变量名`
- 取消变量：`unset 变量名`

## 变量输入输出

- 输出：`echo $变量名`
- 键盘输入：`read 变量名`，通过键盘输入变量的值。

```bash
[root@HN_0_0 coredump]# echo "please input your name";read NAME;
please input your name
martin
[root@HN_0_0 coredump]# echo $NAME
martin
```

- 声明变量类型：`declare 参数 变量`

```bash
# 默认字符串
# -a 数组
# -i 整数
# -x 环境变量
# -r 只读 不能更改、不能unset
[root@HN_0_0 coredump]# SUM=1+2+3
[root@HN_0_0 coredump]# echo $SUM 
1+2+3
[root@HN_0_0 coredump]# declare -i SUM=1+2+3
[root@HN_0_0 coredump]# echo $SUM 
6
# 数组
[root@HN_0_0 coredump]# declare -a var
[root@HN_0_0 coredump]# var[1]="1"
[root@HN_0_0 coredump]# var[2]="2"
[root@HN_0_0 coredump]# var[3]="3"
[root@HN_0_0 coredump]# echo ${var[1]}
1
```

## 变量内容删除、取代、替换

- 删除
  - `#`：使用正则从字符串首进行非贪婪匹配，将匹配数据删除。
  - `##`：使用正则从字符串首进行贪婪匹配，将匹配数据删除。
  - `%`：使用正则从字符串尾进行非贪婪匹配，将匹配数据删除。
  - `%%`：使用正则从字符串尾进行贪婪匹配，将匹配数据删除。

```bash
[root@HN_0_2 coredump]# path="hel:hello:hello martin"
[root@HN_0_2 coredump]# echo $path  
hel:hello:hello martin
[root@HN_0_2 coredump]# echo ${path#llo}
hel:hello:hello martin
[root@HN_0_2 coredump]# echo ${path#hel*:}
hello:hello martin
[root@HN_0_2 coredump]# echo ${path##hel*:}
hello martin
[root@HN_0_2 coredump]# echo ${path%:*llo*}
hel:hello
[root@HN_0_2 coredump]# echo ${path%%:*llo*}
hel
```

- 替换
  - `/旧/新`：使用正则从字符串首进行非贪婪匹配，将匹配数据替换。
  - `//旧/新`：使用正则从字符串首进行贪婪匹配，将匹配数据替换。

```bash
[root@HN_0_2 coredump]# echo ${path/h/H}
Hel:hello:hello martin
[root@HN_0_2 coredump]# echo ${path//h/H}
Hel:Hello:Hello martin
```

- 变量存在判断：

| 表达式             | str不存在             | str为空字符串         | str非空    |
| ------------------ | --------------------- | --------------------- | ---------- |
| `var=${str-expr}`  | `var=expr`            | `var=`                | `var=$str` |
| `var=${str:-expr}` | `var=expr`            | `var=expr`            | `var=$str` |
| `var=${str+expr}`  | `var=`                | `var=expr`            | `var=expr` |
| `var=${str:+expr}` | `var=`                | `var=`                | `var=expr` |
| `var=${str=expr}`  | `var=expr` `str=expr` | `var=expr`            | `var=$str` |
| `var=${str:=expr}` | `var=expr` `str=expr` | `var=expr` `str=expr` | `var=$str` |
| `var=${str?expr}`  | `expr`输出到`stderr`  | `var=`                | `var=$str` |
| `var=${str:?expr}` | `expr`输出到`stderr`  | `expr`输出到`stderr`  | `var=$str` |

