# bash

## 常用命令

- 命令历史：`history`
- 补全功能：`tab键`
- 别名设置：
  - 创建别名：`alias 别名='命令串'`，`alias myll='ls -al'`
  - 取消别名：`unalias 别名`
- 查看是否为内建命令：`type 命令`

## 登录信息定制

- `/etc/issue`：本地打开`bash`时欢迎信息

| 符号 | 含义         |
| ---- | ------------ |
| `\d` | 日期         |
| `\t` | 时间         |
| `\l` | 终端号       |
| `\m` | cpu类型      |
| `\n` | 主机网络名称 |
| `\O` | domain name  |
| `\r` | 操作系统版本 |
| `\S` | 操作系统名称 |

- `/etc/issue.net`：定制`ssh`远程登录信息，具体调用那个文件需要查看`/etc/ssh/sshd_config`的Banner字段。

## 环境配置

- `login shell`：新建bash需要输入账号与密码。会读取以下几个配置文件：
  - `/etc/profile`：系统设置
    - `PATH`：根据UID确定`PATH`变量的具体内容。
    - `umask`：默认权限。
    - `/etc/profile.d/*.sh`：执行里面的文件，加载配置。
    - `/etc/locale.conf`：编码，由`lang.sh`加载。
    - `/usr/share/bash-completion/completions/*`：`tab`补全，由`bash_completion.sh`加载。
  - `~/.bash_profile或~/.bash_login或~/.profile`：用户自定义配置，根据次序，只读取一个。
- `non-login shell`： 新建bash不需要重新登录。
  - `~/.bashrc`：只读取这个配置文件。
- `source`：重新加载配置文件。

## 编码

- 查看支持的编码：`locale -a`
- 查看当前编码：`local`
- 编码文件位置：`/usr/bin/locale`
- 修改编码：`/etc/locale.conf`
- 主要参数
  - `LANG`：系统默认语言，显示乱码的话可以设置为`en_US.UTF-8`或为空。
  - `LC_ALL`：国际化设置，用于设置时间格式、排序规则等。
  
## 数据流重定向

Linux在执行命令时，为命令提供标准输入流、标准输出流、标准错误流来处理命令的各种需求。

- 标准输入流：为命令提供要处理的信息，默认为键盘输入，代码为0。
- 标准输出流：显示命令执行成功后返回的信息，默认为屏幕，代码为1。
- 标准错误流：显示命令执行失败后返回的信息，默认为屏幕，代码为2。
- `/dev/null`：所有重定向到该处的数据，都会丢失。

如果想要将输出和错误流输出到其他地方，这是就需要采用数据流重定向。

- 重定向输入：`<`或`<<`，`<<`用于指定结束符。
- 重定向输出：`>`或`>>`
- 重定向错误输出：`>`或`>>`

```bash
[root@HN_0_0 ~]# cat test 
abcdefg
[root@HN_0_0 ~]# cat 0<test 1>out
[root@HN_0_0 ~]# cat out 
abcdefg
# << 指示结束符
[root@HN_0_0 ~]# cat > test <<"EOF"
> hello
> nihao
> EOF
[root@HN_0_0 ~]# cat test 
hello
nihao
```

由于在同一个命令中，两个流同时对同一个文件写入数据的话，可能会发生数据混乱问题，可以将两个流重定向到一个流中

```bash
[root@HN_0_0 ~]# cat 0<test 1>out 2>&1
```

## 管道

如果想要依次执行多个命令，并且后面的命令依赖与前面命令的输出时，Linux提供管道，让后一个命令将前一个命令的输出当做输入。

```bash
[root@HN_0_0 ~]# ps -ef |grep bash
root       1457   1323  0 10:43 pts/0    00:00:00 -bash
root       3651   1457  0 10:43 pts/0    00:00:00 grep --color=never bash
```

## 命令输出操作

- `cut`：`cut -d '分割符' -f 选取字段`或`cut -c 区间`

```bash
[root@HN_0_0 ~]# export
declare -rx PROMPT_COMMAND="EulerOS_history"
declare -x PWD="/root"
declare -x SELINUX_LEVEL_REQUESTED=""
declare -x SELINUX_ROLE_REQUESTED=""
declare -x SELINUX_USE_CURRENT_RANGE=""
declare -x SHELL="/bin/bash"
declare -x SHLVL="1"
declare -x SSH_CLIENT="10.169.207.67 53144 22"
declare -x SSH_CONNECTION="10.169.207.67 53144 100.99.101.15 22"
declare -x SSH_TTY="/dev/pts/0"
declare -x TERM="vt100"
declare -x TMOUT="3000"
declare -x USER="root"
declare -x XDG_RUNTIME_DIR="/run/user/0"
declare -x XDG_SESSION_ID="175973"
# -c 用于取某个区间的字符
[root@HN_0_0 ~]# export | cut -c 12-
PWD="/root"
SELINUX_LEVEL_REQUESTED=""
SELINUX_ROLE_REQUESTED=""
SELINUX_USE_CURRENT_RANGE=""
SHELL="/bin/bash"
SHLVL="1"
SSH_CLIENT="10.169.207.67 53144 22"
SSH_CONNECTION="10.169.207.67 53144 100.99.101.15 22"
SSH_TTY="/dev/pts/0"
TERM="vt100"
TMOUT="3000"
USER="root"
XDG_RUNTIME_DIR="/run/user/0"
XDG_SESSION_ID="175973"
```

- `grep`：通过正则过滤。

```bash
[root@HN_0_0 ~]# ps -ef |grep bash
root       1457   1323  0 10:43 pts/0    00:00:00 -bash
root       3651   1457  0 10:43 pts/0    00:00:00 grep --color=never bash
```

- `sort`：排序

```bash
# -t 指定间隔符拆分为列
# -k 按第几列进行排序
[root@HN_0_4 ~]# cat /etc/passwd |sort -t ":" -k 3
root:x:0:0:root:/root:/bin/bash
operator:x:11:0:operator:/root:/sbin/nologin
bin:x:1:1:bin:/bin:/sbin/nologin
games:x:12:100:games:/usr/games:/sbin/nologin
```

- `wc`：
  - `wc -l` ：统计列数
  - `wc -m`：统计字符数
- `uniq`：用于去掉重复的数据。
- `split`：文件拆分命令。
