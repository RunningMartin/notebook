# Redis学习笔记—原理

## IO模型

Redis是一个单线程程序，在使用复杂度为O(n)的指令时，会出现卡顿。Redis的数据存储在内存中，避免了磁盘IO读写，因此其运算速度很快。

Redis采用多路复用IO模型(非阻塞IO)，并发处理多个请求。

- 阻塞IO：必须在缓冲区读写一定字节，若条件不满足，阻塞至任务完成。
- 非阻塞IO：在缓存区中读写尽可能多字节，通过返回值告知实际读写字节数。

非阻塞IO面临一个问题：任务完成部分，条件满足后，如何通知线程继续任务。`select|epoll`函数提供事件轮询API，调用`select(read_fds,write_fds,timeout)`，返回读写描述符对应的读写事件(这一步是阻塞)，线程拿到事件后，处理相关事件，然后继续轮询。

Redis在处理多个客户端的请求时构建了：

- 指令队列：客户端关联指令队列，客户端发送的指令在队列中进行排序，先到先服务。
- 响应队列：客户端关联响应队列，服务器通过响应队列将结果返回客户端，如果队列为空，则不调用写事件，避免无效消耗CPU。

针对Redis的定时任务，为了避免线程调用`select`时阻塞，导致定时任务无法准时调度。Redis维护一个最小堆用于记录最快要执行的任务，每个循环周期，处理已经到点的任务，并将到执行下一个任务的事件差作为`select`的timeout参数。

## 持久化

持久化机制用于保证数据不会因为故障而丢失，Redis的持久化机制有两种：快照和AOF日志。

### 快照

- 原理

  快照是一次全量备份，将内存中的数据二进制序列化后存储在磁盘中，因此存储上十分紧凑。为了避免生成快照时内存中数据的变化以及频繁文件IO(不能多路复用)对服务器性能的影响，Redis采用操作系统的多进程COW机制实现持久化。

  Redis在持久化时，会通过fork函数，创建子进程，由子进程负责快照持久化，子进程生成后，与父进程共享内存资源。子进程遍历内存中的数据，将其序列化后写入磁盘，与此同时，父进程对数据修改时，会通过COW机制进行数据段页面分离(一个数据段由多个页面组成)，当父进程对一个页面进行修改时，会将共享的页面复制一份，因此不会影响子进程的内存资源，也不会导致内存消耗大幅度增加。

- 优点

  - 适用于灾难恢复：快照会将内存中的数据全部备份。
  - 最大化Redis性能：快照任务由子进程负责，不影响父进程的性能。
  - 恢复大数据集时比AOF日志恢复速度快。

- 缺点

  - 不能实时备份数据。
  - 当数据集过大，`fork`子进程时，耗时过大。

### AOF日志

- 原理

  AOF日志是增量备份，记录会修改内存数据的指令，Redis收到一条指令后，验证参数，存储到磁盘中，再执行指令，因此如果出现宕机，可以重放AOF日志中的指令，恢复到宕机之前的状态。写AOF日志时，会先将内容写入内核的内存缓存中，由内核异步将数据写入磁盘，可以通过`fsync`策略强制刷盘，AOF默认间隔事件为`1S`。

  AOF日志会随着运行时间的增加而增加，数据库重启时，会重放AOF日志，如果容量过大，会导致重启耗时过多，需要定期对AOF日志瘦身，瘦身后，新的AOF日志只包含重建当前数据集所需的最少命令。

- 优点

  - `fork`子进程速度快。
  - 备份的时间粒度更小。

- 缺点

  - 体积大。

### 混合持久化

快照和AOF日志都会消耗一定资源，通常不会在Redis主节点进行持久化操作，持久化操作主要在从节点执行。为了避免AOF日志大和快照的时间粒度大的问题，通常将二者结合使用。

## 管道

Redis客户端下发一条指令会需要两个操作：写、读，需要一个网络读写时间，如果是N条指令，则需要花费N个网络读写时间。如果调整N条指令的读写顺序从

![管道—读写顺序未调整](Raw/原理/管道—读写顺序未调整.png)

调整为

![管道—读写顺序调整](Raw/原理/管道—读写顺序调整.png)

则可大幅节省IO时间。

Redis中一个完整的请求交互流程为

![管道—请求交互流程](Raw/原理/管道—请求交互流程.png)

- write在发送缓冲写数据，基本没有耗时，只有当发送缓冲满了，才需要等待缓冲空出空闲空间。
- read从接收缓冲读数据，也基本没有耗时，当接收缓冲为空，需要等待数据到来。
- 因此对于管道来说，连续的write操作基本没有耗时，而第一个read操作需要等待一个网络数据包往返开销，后续read直接从缓冲中拿数据。

Python可以通过管道执行任务

```python
import redis
pool = redis.ConnectionPool(host="localhost",port=6379)
client = redis.StrictRedis(connection_pool=pool)
pipline = client.pipeline(transaction=True)
pipline.set('a',1)
pipline.incr('a')
pipline.incr('a')
pipline.execute()
```

## 事务

事务通常用于确保多个操作的原子性，但在Redis中，事务只具备隔离性(单线程特性，不必担心执行队列会被其他指令干扰)而不具备原子性(指令执行失败后，后续指令会继续执行，在Redis中，只有语法错误或键不支持该命令才会出现命令失败，这都是使用者带来的错误)。

通过客户端，下发`MULTI`指令，启动一个事务。Redis会将后续指令存入事务队列中，当遇到`EXEC`指令时，执行事务队列中所有指令，也可以通过`DISCARD`指令清空事务队列，放弃执行事务。

![事务—执行](Raw/原理/事务—执行.png)

客户端发送一条指令到事务缓存队列中需要消耗一个网络读写时间，当事务中指令较多时，会导致网络IO时间过长，因此通常情况下事务需要搭配管道使用。

在多并发的场景下，为了避免修改数据时出现冲突，可以采用分布式锁(悲观锁：假设拿数据时会有用户修改，因此每次都上锁)或watch(乐观锁：假设拿数据时不会有用户修改，不会上锁，更新数据时，需要判断期间是否有其他用户更新，可以使用版本号和CAS算法实现)。watch命令需要在multi之前执行，wach会在事务开始之前获取多个关键变量的数据，当事务执行前，会检查是否关键变量信息是否被修改，修改则告知事务执行失败。执行exec前，新开cli，修改age的值。

![事务—watch](Raw/原理/事务—watch.png)

- 为什么Redis中的事务在失败时不会进行回滚？

只有当Redis命令有语法错误或键不支持该指令时，才会导致命令失败，这两种错误都是程序带来的错误，而回滚并不能解决任何程序错误，这些问题应该在开发期间会被解决，因此Redis在系统内部对功能进行了简化，确保更快的运行速度。

## 消息多播

### 发布者订阅者模型

消息的多播允许生产者生成一次消息，中间件将消息复制到多个消息队列中，由消息队列的消费者组进行消费。Redis中通过PubSub(发布者订阅者模型)来实现消息多播。

![消息多播—示意图](Raw/原理/消息多播—示意图.png)

PubSub支持的命令有：

- 订阅：subscribe 主题
- 发送消息：publish 主题 消息
- 取消订阅：unsubscribe 主题
- 订阅模型：psubscribe 匹配符
- 订阅模型：punsubscribe 匹配符

PubSub的实验(开启两个窗口，一个窗口订阅信息，一个窗口发布消息)：

![消息多播—执行](Raw/原理/消息多播—执行.png)

Python中可以通过pubsub方法创建一个消费者

```python
# 消费者(要先启动)
import redis
pool = redis.ConnectionPool(host="localhost", port=6379)
client = redis.StrictRedis(connection_pool=pool)
sub = client.pubsub()
sub.subscribe('user')
for msg in sub.listen():
    print(msg)

# 生产者
import redis
pool = redis.ConnectionPool(host="localhost", port=6379)
client = redis.StrictRedis(connection_pool=pool)
client.publish('user',1)
client.publish('user',2)
client.publish('user',3)
```

PubSub模式有一个缺点：当消费者重连后，这段时间内生产者发送的消息彻底丢失(没有消费者，消息直接丢弃)。

### Stream

为了解决这个问题，Redis通过Stream来提供一个支持多播的可持久化消息队列(灵感来自Kafka)。

![stream—结构图](Raw/原理/stream—结构图.png)

通过创建一个消息链表，将所有的消息串联起来，并为每个消息添加一个ID，一个Stream支持多个消费者组，每个消费者组通过游标`last_delivered_id`用于标记该消费者组消费到哪条消息。同一个消费者组中消费者之间存在竞争关系，任意一个消费者读取消息都会导致消费者组的`last_delivered_id`前移。消费者内维护`pending_ids`，记录当前客户端读取，但是未ack的消息ID，用于确保消息不会因网络传输丢失而没处理。消息ID的形式为` timestampInMillis-sequence`，消息的内容为键值对。

消费者通过`pending_ids`维护正在处理的消息ID列表PEL，若消费者处理完消息后没有ack，PEL列表不断增长。

![stream—PEL](Raw/原理/stream—PEL.png)

通过PEL列表，当客户端断开重连后，可以通过`xreadgroup 0-0`指令能再次读取PEL列表中的消息以及`last_delivered_id`之后的新消息。

stream的高可用建立在主从复制的基础上，但Redis的复制是异步执行的，因此可能会丢失部分数据。Redis还能通过分配多个stream来实现分区，客户端采用一定的策略(哈希)将生产的消息发送到不同的stream中，实现负载均衡。

与stream相关命令有：

- 流管理
  - 添加消息：`xadd 流 消息ID(*代表自动) 键 值`
  - 定长stream：`xadd 流 maxlen 长度 ID 键 值`
  - 删除消息：`xdel 流 消息ID(只设置标志位)`
  - 独立消费消息：`xread 指令 streams 流 起始ID(0-0代表从头，$代表从尾部开始接收新消息)`
    - `count 数量`：指定消费数量
    - `block 时间(毫秒)`：阻塞超时时间，`0`为一直阻塞
  - 删除流：`del 流`

  - 获取消息列表：`xrange 流 起始ID 结束ID(过滤已被删除的消息，-代表开始 +代表结尾)`
  - 消息长度：`xlen 流(包含被删元素)`
  - 查看流信息：`xinfo stream 流`

- 消费者组管理

  - 创建消费者组：`xgroup create 流 组 消费起始序号(0-0代表从头，$代表从尾部开始接收新消息)`
  - 查看消费者组信息：`xinfo groups 流`
  - 查看消费者信息：`xinfo consumers 流 组`
  - 消费信息：`xreadgroup GROUP 组 消费者 指令 streams 流 >`
    - `count 数量`：指定消费数量
    - `block 时间(毫秒)`：阻塞超时时间，`0`为一直阻塞
  - ack消息：` xack 流 组 消息ID`

命令行实战：

```bash
# 添加消息
127.0.0.1:6379> xadd users * name martin age 24
"1562814476559-0"
127.0.0.1:6379> xadd users * name kevin age 26
"1562814492173-0"
127.0.0.1:6379> xadd users * name elune age 24
"1562814503526-0"
# 查看消息长度
127.0.0.1:6379> xlen users
(integer) 3
# 获取消息列表
127.0.0.1:6379> xrange users - +
1) 1) "1562814476559-0"
   2) 1) "name"
      2) "martin"
      3) "age"
      4) "24"
2) 1) "1562814492173-0"
   2) 1) "name"
      2) "kevin"
      3) "age"
      4) "26"
3) 1) "1562814503526-0"
   2) 1) "name"
      2) "elune"
      3) "age"
      4) "24"
# 查看流信息      
127.0.0.1:6379> xinfo stream users
 1) "length"
 2) (integer) 3
 3) "radix-tree-keys"
 4) (integer) 1
 5) "radix-tree-nodes"
 6) (integer) 2
 7) "groups"
 8) (integer) 0
 9) "last-generated-id"
10) "1562814503526-0"
11) "first-entry"
12) 1) "1562814476559-0"
    2) 1) "name"
       2) "martin"
       3) "age"
       4) "24"
13) "last-entry"
14) 1) "1562814503526-0"
    2) 1) "name"
       2) "elune"
       3) "age"
       4) "24"
# 独立消费消息
127.0.0.1:6379> xread count 1 streams users 0-0
1) 1) "users"
   2) 1) 1) "1562814476559-0"
         2) 1) "name"
            2) "martin"
            3) "age"
            4) "24"
# 创建消费者组
127.0.0.1:6379> xgroup create users client 0-0
OK
# 查看消费者组信息
127.0.0.1:6379> xinfo groups users
1) 1) "name"
   2) "client"
   3) "consumers"
   4) (integer) 0
   5) "pending"
   6) (integer) 0
   7) "last-delivered-id"
   8) "0-0"
# 消费者消费消息
127.0.0.1:6379> xreadgroup GROUP client client_1 count 1 streams users >
1) 1) "users"
   2) 1) 1) "1562814476559-0"
         2) 1) "name"
            2) "martin"
            3) "age"
            4) "24"
# ack消息
127.0.0.1:6379> xack users client 1562814476559-0
(integer) 1
127.0.0.1:6379> xreadgroup GROUP client client_1 count 1 streams users >
1) 1) "users"
   2) 1) 1) "1562814492173-0"
         2) 1) "name"
            2) "kevin"
            3) "age"
            4) "26"
127.0.0.1:6379> xreadgroup GROUP client client_1 count 1 streams users >
1) 1) "users"
   2) 1) 1) "1562814503526-0"
         2) 1) "name"
            2) "elune"
            3) "age"
            4) "24"
# 查看消费者信息
127.0.0.1:6379> xinfo consumers users client
1) 1) "name"
   2) "client_1"
   3) "pending"
   4) (integer) 2
   5) "idle"
   6) (integer) 57623
```

Python实战：

```python
import redis

pool = redis.ConnectionPool(host='localhost', port='6379')
client = redis.StrictRedis(connection_pool=pool)
users = [
    {
        'name': 'martin',
        'age': 24
    },
    {
        'name': 'kevin',
        'age': 26
    },
    {
        'name': 'elune',
        'age': 24
    }
]
for user in users:
    client.xadd(name='users', fields=user, id='*')

client.xgroup_create(name='users', groupname='clients', id='0-0')
print(client.xreadgroup(groupname='clients', consumername='client_1', count=1,
                        streams={'users': '>'}))
print(client.xreadgroup(groupname='clients', consumername='client_1', count=1,
                        streams={'users': '>'}))
print(client.xreadgroup(groupname='clients', consumername='client_1', count=1,
                        streams={'users': '>'}))
```

## 小对象压缩

## 主从同步

## 学习资料

- 掘金小册：《Redis 深度历险：核心原理与应用实践》
- Redis命令参考：http://redisdoc.com