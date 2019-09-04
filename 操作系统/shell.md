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
