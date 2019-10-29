# HTTP协议学习笔记(十)—HTTP性能优化

## 0X00 梗概

HTTP传输过程中有三个角色：

- 客户端
- 服务器
- 传输链路

因此性能优化将着手于这三部分。

## 0X01 服务器

服务器端优化的方向是充分利用系统资源，提供服务器吞吐率和并发数，降低响应时间。因此我们需要去观察服务器的性能和服务器系统资源的使用情况。

性能对服务器来说，是以最快速的速度、处理尽可能多的请求。衡量服务器性能的主要指标有三个：

- 吞吐量：每秒的请求次数。
- 并发数：同时支持的客户端数量。
- 响应时间：处理一个请求的耗时。

这三个指标可以使用性能测试工具`ab`(Apache Bench)。

```bash
➜  ~ sudo apt install apache2-utils
➜  ~ ab -c 100 -n 10000 'https://fangjie.site/'
This is ApacheBench, Version 2.3 <$Revision: 1757674 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking fangjie.site (be patient)
Completed 1000 requests
...
Concurrency Level:      100
Time taken for tests:   10.113 seconds
Complete requests:      10000
Failed requests:        0
Total transferred:      2550000 bytes
HTML transferred:       980000 bytes
Requests per second:    988.81 [#/sec] (mean)
Time per request:       101.131 [ms] (mean)
Time per request:       1.011 [ms] (mean, across all concurrent requests)
Transfer rate:          246.24 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:       12   98   7.5     97     133
Processing:     1    2   1.2      2      18
Waiting:        1    2   1.1      2      18
Total:         13  101   7.5     99     135
...
```

系统资源方面可以使用Linux自带工具。

- 内存和CPU使用：`top`
- 系统状态：`vmstat`
- 网卡流量：`sar`

## 0X02 客户端

客户端最看重的是延迟(等待响应到来所花费的时间)。延迟由几点原因导致：

- 光速：距离过远，必然延迟大。
- 带宽：传输中各个节点的带宽决定了同时能传输的数据量。
- DNS查询：没有域名缓存时，需要发起请求从DNS获取。
- TCP握手：由距离和带宽所决定(带宽小，网络拥塞时会出现丢包重传)。

客户端延迟可以采用`WebPageTest`进行测试。

![WebPageTest,资源来源于极客时间](raws/HTTP优化/WebPageTest.png)

通过浏览器的`开发者工具->网络`也可以查看客户端加载资源耗时时间。

![Chrome测试耗时,图片来源于极客时间](raws/HTTP优化/Chrome测试耗时.png)

## 0X03 传输链路

传输链路主要是通过CDN所建立的专用网络，以最快的速度传输数据。

