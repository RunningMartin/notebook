# shell
## 什么是shell
- shell：Linux的命令解释器，解释用户对操作系统的操作。
- 查看支持的shell:`cat /etc/shells`
- Ubuntu和Centos默认支持：bash
- 用途：
  - Linux启动过程
  - 命令
## Linux启动过程
- BIOS引导-->MBR(硬盘的主引导记录)-->BootLoader(grub,启动和引导内核启动)-->kernel(内核启动)-->系统初始化(Centos7 1号进程systemd,Centos6 1号进程init)-->shell
- mbr查看：
```bash
# /dev/sda 为系统盘 bs为开始的446字节  512字节包括分区表
 dd if=/dev/sda of=mbr.bin bs=446 count=1
 # 查看 最后有一个55aa 表明可引导
 hexdump -C mbr.bin
```
- 查看grub
```
[root@HN_0_0 ~]# cd /boot/grub2/
[root@HN_0_0 grub2]# ls
device.map  fonts  grub.cfg  grubenv  i386-pc  locale
[root@HN_0_0 grub2]# grub2-editenv list
默认引导内核   uname -r 验证
```
- centos 6
```
# 使用init
top -p 1
先加载/etc/rc.d下的shell脚本
```
- centos 7
```
# 使用systemd
/etc/systemd/system
# 加载配置文件
/usr/lib/systemd/system
```
- 常用shell 脚本命令
```
/sbin/grub2-下的文件
可以用file命令查看类型
```

## Shell脚本格式
- 使用文本将命令组合在一起，保存下来，然后赋予其权限(chmod u+rx filename)
```
# 默认执行的bash工具，sha-bang
#!/bin/bash
# 注释
```
## 执行命令的方式
- bash ./filename.sh:启动一个bash子进程去执行，不影响当前的环境，可以不用赋予权限。
- ./filename.sh：使用sha-band指定的bash工具执行，不影响当前的环境，需要赋予权限。
- source ./filename.sh：当前进程执行，影响当前的环境。
- . ./filename.sh：当前bash进程运行，影响当前的环境。
- 内建命令：不需要创建子进程和对当前shell生效。
## 管道与重定向
- 管道：进程通信工具，方便两条命令通信
- 重定向：将命令输出重定向到文件中，还可以将文件视作为输入。
- 管道和管道符
```
# 管道符 |，将前一个命令的输出作为第二个命令的输入
cat 文件|more 分页显示
[root@HN_0_0 tmp]# cat|ps
  PID TTY          TIME CMD
 3020 pts/1    00:00:00 cat
 3021 pts/1    00:00:00 ps
30734 pts/1    00:00:00 bash
# 新建
[root@HN_0_0 ~]# cd /proc/3020/fd
[root@HN_0_0 fd]# ls -l
total 0
# 0为输入
lrwx------. 1 root root 64 Sep  5 11:04 0 -> /dev/pts/1
# 1位输出
l-wx------. 1 root root 64 Sep  5 11:04 1 -> pipe:[80927605]
# 
lrwx------. 1 root root 64 Sep  5 11:04 2 -> /dev/pts/1
```
- 子进程与子shell：管道会创建子进程，因此子进程中的内建命令信息是无法传递给父进程的，使用管道符时，需要规避内建命令
- 重定向符：将标准输入、标准输出、错误输出进行一个连接
  - 输入重定向：<   wc -l < /etc/passwd
  - 输出重定向：
    - >：将标准输出输出到文件中，会清空
    - >>：对文件追加
    - 2>：错误重定向
    - &>：将错误和标准都输出
```bash
read 遍历# 创建遍历
[root@HN_0_0 ~]# cat 2.sh 
#!/bin/bash
# 重定向输入输出，一般用于写配置文件，会生成1.sh
cat > 1.sh <<EOF
echo "hello world"  # 
EOF
```

## 变量
```
# 定义变量，名称为有意义名称，由字母，数字，下划线，不能以数字开头
a=123# 不允许出现空格
# 获取命令的结果
letc=$(ls -l /etc) 或`ls -l /etc`
# 内容包含空格，用""或''括起来
# 引用
$变量名  ${变量名} 后面有数据需要一起输出
${string1}23
# 作用范围，只作用于当前的进程，不会再子进程和平行进程起作用
# 定义变量时，export 变量名  子进程能获取父进程的变量名
# 删除变量，unset 变量名
# 环境变量
默认环境变量 env命令   $PATH 命令搜索路径
PATH=$PATH:新路径
set也可以查看更多的遍历
# 预定义变量
$?：上一条命令是否正确执行 0 true 1 false
$$：当前进程pid
$0：当前进程名称
# 位置变量
$1 $2...$9 ${10}
.filename.sh -a -l #$1 =-a $2=-l  ${2-_} 如果为空，则为下划线，规避空值
```
## 环境变量配置文件
- /etc/profile
- /etc/profile.d
- ~/.bash_profile：用户自定义
- ~/.bashrc：用户自定义
- /etc/bashrc
```
su - 用户：执行全部
su 用户：只加载.bashrc和/etc/bashrc
更新环境变量 source 路径
```
