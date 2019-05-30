# Linux常用配置

## 配置网络

- 查看网卡信息

```bash
[root@localhost client]# ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN qlen 1
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
# 网卡名 <网卡状态>
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP qlen 1000
    link/ether xx:xx:xx:xx:xx:xx brd ff:ff:ff:ff:ff:ff
    # ip 网关信息
    inet xxx.xxx.xxx.xxx/xx brd xxx.xxx.xxx.xxx scope global noprefixroute eth0
       valid_lft forever preferred_lft forever
    inet6 xxxx::xxxx:xxxx:xxxx:xxxx/xx scope link 
       valid_lft forever preferred_lft forever
```

- 通过配置文件配置网卡：修改`/etc/sysconfig/network-scripts/ifcfg-网卡名`

```bash
# 编辑网卡配置信息
[root@localhost network-scripts]# vi ifcfg-eth0
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static	# static代表采用静态网络 dhcp代表从dhcp服务器获取ip
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
NAME=eth0
# UUID用于操作系统识别网卡，可以通过uuidgen命令生成
UUID=9b134447-18e3-4fed-b7b5-28d5af51ed56
DEVICE=ens33		# 网卡名
ONBOOT=yes			# 是否启动
# BOOTPROTO设定为dhcp时，以下三个不填
IPADDR=				# 静态ip
GATEWAY=			# 网关
NETMASK=			# 子网掩码
# 重启网卡
[root@localhost network-scripts]# service network restart
```

- 通过命令临时配置网卡：`ifconfig`

```bash
# ifconfig配置的ip为临时的，重启会失效
# 设置IP和掩码
[root@localhost ~]# ifconfig eth0 你的ip netmask 子网掩码
# 设置网关
[root@localhost ~]# route add default gw 网关
```

- 通过命令配置永久网卡信息：`nmcli`

```bash
# nmcli 命令会修改配置文件
[root@localhost ~]# nmcli connection show 
NAME             UUID                                  TYPE      DEVICE 
System eth0     xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  ethernet  eth0   
# 通过NAME 查看配置信息
[root@localhost ~]# nmcli connection show System\ eth0
connection.id:                          System eth0
----
# 开机是否自动连接
connection.autoconnect:                 yes
---
# ipv4协议信息
ipv4.method:                            # manual代表手动配置  auto代表自动获取
ipv4.dns:								# dns服务器
ipv4.addresses:                         # IP地址
ipv4.gateway:                           # 网关
ipv4.routes:                            # 路由
# 修改网络参数
[root@localhost ~]# nmcli connection modify System\ eth0 \
属性名 属性值\
属性名 属性值
# 重启网卡
[root@localhost ~]# nmcli connection up System\ eth0
```

- 修改主机名

```bash
[root@localhost network-scripts]# hostnamectl 
   Static hostname: localhost
...
[root@HN_0_3 network-scripts]# hostnamectl set-hostname martin
[root@HN_0_3 network-scripts]# hostnamectl 
   Static hostname: martin
...
```

