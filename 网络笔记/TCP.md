## UDP

## TCP

### 设计原理



### 握手流程

- TCP建立连接的目的是：分配资源，初始化包序列号(seq)。

- 准备：服务端通过`listen()`监听端口，进入`LISTEN`状态。
- 第一次握手：客户端通过`connect()`函数发送`SYN seq=x`，客户端进入`SYN_SENT`状态。
- 第二次握手：服务端收到包后，发送`SYN seq=y`，并附上`ACK seq=x+1 `，服务端进入`SYN_RECV`状态。
- 第三次握手：客户端收到包后，发送`ACK seq=y+1`。

### 疑问



## HTTP与HTTPs

## Live

- TCP三次握手(connect函数)
- TCP四次挥手()
