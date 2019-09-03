# HTTP 工具

## Nginx

### IO 多路复用

Nginx是一款轻量级web服务器，它采用进程池+单线程的工作模式提供高性能服务。Nginx在启动时会预先创好固定数量的worker进程，放入进程池。Nginx启动后不会fork新进程，而且可以将进程绑定到独立的CPU上，消除进程创建和切换成本，能充分利用多核CPU的计算能力。进程池上层还有一个master进程，用于监控进程，自动恢复异常的worker，保持进程池的稳定和服务能力。

Nginx采用单线程，避免了线程切换带来的时间损耗，并避免了多线程中互斥锁的开销。单线程采用I/O 多路复用接口(epoll)。Web服务器是I/O密集型应用，其瓶颈在网络收发能力而不是CPU的性能，网络I/O会因为各种原因导致不得不等待，如数据未到、对端未响应、缓冲区慢不能发送，从而导致线程停下来等待。epoll只有当连接真正准备好后，才会通知线程去处理，如果发送阻塞，则切换到其他可处理的请求，提高了CPU利用率，而且避免了进行、线程切换带来的无效CPU开销。epoll的连接管理有内核复杂，减轻了Nginx的负担，只需为每个连接分配少量内存维护状态，因此nginx能处理大并发。

### 多阶段处理

nginx内部将整个请求处理流程分为多段，可以在配置文件中进行组合，主要有四大模块：

- handler模块：直接处理HTTP请求。
- filter模块：不处理请求，过滤响应报文。
- upstream模块：反向代理，转发请求到其他服务器。
- balance模块：实现反向代理时的负载均衡算法。

handler模块和filter模块是按责任链模式设计的，请求报文将在处理流水线上完成处理，整个流水线有11段。

![nginx 请求流水线处理流程]()

## OpenResty

Nginx使用磁盘上的静态配置文件，每次修改后都需要重启才能生效，这在业务频繁变动时十分致命。OpenResty基于Nginx，利用Nginx模块化、可扩展的特性，开发了一系列的增强模块。其关键在于加入了ngx_lua模块，嵌入了Lua语言，采用脚本操作nginx内部的进程、多路复用、阶段式处理等构件(脚本语言具备随写随执行的优点，避免C的开发周期)。OepnResty将Lua自身的协程和nginx的事件机制结合在一起，能实现同步非阻塞编程范式。

Lua具备代码热加载特性，不需要重启进程就可以从其他地方加载数据，替换内存中的代码片段，带来了动态配置的优点，实现微秒、毫秒级别的实时更新。

Lua通过协程实现同步非阻塞操作，这是应用级别的IO 多路复用，发生阻塞时，协程自动切换出，执行其他的程序。还可以使用LuaJIT将Lua编译为机器码，让其和原生C代码一样快。OpenResty的流水线由Lua脚本组成。

## WAF

WAF(Web Application FireWall)网络应用防火墙，工作在七层，因此可以看到IP、端口号和HTTP报文，能根据HTTP报文进行过滤，WAF是HTTP入侵检查和防御系统。

功能：

- IP黑名单和白名单
- URI黑名单和白名单
- 防护DDos
- 过滤请求和响应报文，防御代码注入和敏感信息外泄。
- 审计日志

最全面的WAF解决方案：ModSecurity，核心组件：

- 规则引擎：定义了自定义的SecRule语言，通常基于正则表达式，需要编译为动态模块，在nginx中集成。

- 规则集：nginx中配置

  ```nginx
  modsecurity on;  # 启动
  modsecurity_rules_file 路径.conf# 规则集 默认只检测，不提供入侵阻断，防止误杀
  SecRuleEngine on; # 打开全面防护
  # 提供owasp modsecurity 核心规则集合(CRS)  
  # https://github.com/SpiderLabs/owasp-modsecurity-crs
  # 可以编辑crs-setup.conf.example 添加各种规则 
  Include 文件名
  ```

WAF实质上是对HTTP报文进行模式匹配和数据过滤，会消耗CPU并增加计算成本，降低服务能力。

## CDN

CDN(Content Delivery Network)内容分发网络，是用于为传输加速的。互联网中有一个个小网组成，然后小网之间互联，因此跨网络通信是其瓶颈就在于网络之间的连接点，而且网络之中还有很多路由器、网关会带来一定的延迟。CDN的核心是就近访问，CDN在互联网中搭建专用网络，利用缓存代理技术，将源站的内容缓存到每个网络中的每个节点中，用户上网时，直接访问最近的一个CDN节点(边缘节点)。资源分为静态资源和动态资源，CDN只能缓存静态资源。

CDN由两部分组成：

- 全局负载均衡(Global Server Load Balance)：负责用户接入时，选择一个最佳节点提供服务。DNS解析时，权威DNS返回CNAME，指向CDN的GSLB，本地DNS访问GSLB，GSLB给出最佳的节点IP。
- 缓存系统：缓存最常用的资源
  - 命中：资源被缓存，直接返回。
  - 回源：资源未被缓存，访问源站。

CDN对动态资源有两点好处：

- 提供边缘计算
- 优化路由

## WebSocket

WebSocket实际上是基于TCP的，只是搭Web的顺风车，和HTTP属于同级。WebSocket提供全双工通信，便于实时通信。WebSocket采用URI的格式提供服务发现，协议名为`ws|wss`，默认端口为80和443，使用上WebSocket伪装成HTTP协议，穿透互联网上的防火墙。

WebSocket采用二进制帧，其结构非常简单，最少两个字节，最多14个字节。

![WebSocket帧结构]()

第一个字节的第一位表示FIN，消息结束，后三位保留，后四位Opcode为操作码，表示帧类型，1为纯文本，2为二进制数据，8为关闭连接，9,10为保活的ping和pong。

第二个字节的第一位为掩码标志位，是否采用异或操作加密，客户端必须加密，服务器必须不加密，后7位为帧内容长度，可以扩展8个字节。长度后为掩码密钥，使用则有4个字节随机数，不使用，则不存在。

结构：结束标志位+操作码+长度+掩码。

### 握手

握手时，使用HTTP的GET请求，包含四个头部字段：

- `Connection:Upgrade`：要求升级协议
- `Upgrade:websocket`：升级为websocket。
- 避免误识别，添加Challenge。
- `Sec-WebSocket-Key:16字节base64编码随机数`：简单认证密码。
- `Sec-WebSocket-Version:13`：协议版本号。

服务器收到后，发送101响应，切换协议，`Sec-WebSocket-Accept:sha-1(Sec-WebSocket-Key+专用UUID)`防止误连接。

## 性能优化

HTTP性能优化可以从客户端、服务器和传输链路三方面考虑

### HTTP服务器

衡量服务器性能有三个指标：

- 吞吐量：QPS，每秒钟请求的次数。
- 并发数：服务器同事能负载多少个客户端。
- 响应时间：响应时间，反应服务器的处理能力。

性能测试工具`ab`、系统资源监控：uptime、top、vmstat、netstat、sar

优化方案：

- 开源：采用nginx或OpenResty高性能服务器，开启长连接和使用TCP fast Open。初次握手就传输数据，达到0-RTT，提高服务器性能。

```nginx
server{
    listen 80 deferred reuseport backlog=4096 fastopen=1024;
    keepalive_timeout 60;
    keepalive_requests 10000;
    # 静态资源
    location ~* 、.(png)${
        root /var/images/png;
    }
    # 动态资源
    location ~* 、.(php)${
        proxy_pass http://php_back_end;
    }
}
```

- 节流：压缩报文，去除掉无关信息。
  - 去除图片中无关的源信息，降低分辨率，缩小尺寸，有损选jpeg，无损选Webp。
  - 小文本和小图片合并发送。
  - 减少无关字段。
  - 减少Cookie使用量，通过Cookie中的domain和path限制作用域。针对HTML5可以使用Web Local Storage，避免Cookie。
  - 域名限制在2-3个，减少域名解析。
  - 减少重定向。
- 缓存：利用好缓存的相关字段，核心就是没有请求。
  - 服务器的缓存。
  - CDN缓存和加速
- 采用HTTP/2：适用于长连接，一个域名只是用一个TCP连接即可，发送的数据最好是小资源，避免更新导致资源失效。

### HTTP客户端

客户端最核心的是延迟，影响延迟的因素有：

- 距离
- 带宽
- DNS查询
- TCP握手

测试网站：SSLLabs和WebPageTest网站，也可以使用浏览器的开发者工具，查看瀑布图。

优化方案：DNS缓存、TCP复用和使用CDN
