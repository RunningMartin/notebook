# Redis学习

## 灵魂拷问

- Redis是什么？
- Redis能用来做什么？
  - 缓存
  - 分布式锁

## 基础数据结构

- `Redis`中所有数据结构都是以唯一的`key`字符串作为名称，通过`key`来获取相应的`value`数据。不同类型的数据结构差异在`value`的结构。
- 字符串(`string`)：
  - 其`value`为一个字符串，其字符串是一个动态字符串，通过预分配冗余空间来避免频繁内存分配。当字符串长度小于`1M`，扩容每次都加倍，如果超过`1M`,每次只扩容`1M`，字符串最大长度为`512M`。
  - 应用场景：可以用于缓存用户信息(搭配序列化与反序列化)。
- 列表(`list`)：
  - 底部实现为链表，插入、删除操作非常快，时间复杂度为`O(1)`。索引的时间复杂度为`O(n)`(会进行遍历)。
  - 当列表为空时，内存会自动回收。
  - 应用场景：异步队列，将任务结构体序列化后，放入列表，另一端从列表中获取数据进行处理。
  - 类型：
    - 队列：一边进一边出。
    - 栈：固定一个方向进、出。
  - 快速列表：元素较少时，采用连续内存空间存储(压缩列表：`ziplist`)，当元素较多时，改为`quicklist`，这是因此指针也需要空间。`quciklist`将多个`ziplist`通过双向指针串起来，实现快速插入删除性能的同时，又不会出现太大的空间冗余。
- 集合(`set`)：集合是一个特殊的字典，其`value`值为`NULL`，内部的键值对是唯一且无序的。
- 哈希(`hash`)：
  - 哈希是无序字典，其采用数组+链表的二维结构，数组用于存储`hash`值，链表用于存储碰撞的元素。其值只能是字符串，`Redis`为了提高性能，不阻塞服务，采用渐进式`rehash`策略(rehash  的同时，保留新旧两个  hash  结构，查询时会同时查询两个hash结构，然后在后续的定时任务中以及hash的子指令中，循序渐进地将旧  hash  的内容一点点迁移到新的  hash  结构中)
  - 哈希可以用于存储、读取、修改用户属性，数据传输量比字符串小，但是其存储消耗高。
- 有序集合(`zset`)：
  - `zset`是一个集合，但是可以为每个元素赋予一个`score`，代表其排序权重。
  - 可以用于排行榜、需要使用权重信息。
  - 跳跃列表：`zset`要实现随机插入与删除，因此不能采用数组来存储，但是又要实现排序，也就意味着新元素插入时，需要知道要插入到哪里，这样才能维持链表有序。查找插入点最快的方法莫过于二分法，二分法其对象必须是数据，因此可以采用这种思想，为链表定制一个能快速定位的层级结构，以空间换时间。
- 基本库：`redis-py`

## 操作

- 添加键值对
  - 单个：`set key value`
  - 多个：`mset key1 value1 key2 value2 key3 value3`
- 查询`value`值
  - 单个：`get key`
  - 多个：`mget key1 key2 key3`
- 删除：`del key`
- 判断键是否存在
  - `exists key`
  - 不存在则只需`set`：`setnx key value`
- 设置过期时间(可以用于控制缓存失效时间)：
  - `expire key time(单位秒)`
  - 执行`set`且设置过期时间：`setex key time value`
- 计数(当value为一个整数时，可以进行递增，其范围为`signed long`)：`incrby 键 增量`
- 列表操作：
  - 添加元素：
    - `rpush 列表名 value1 value2`：在列表右边添加元素。
    - `lpush 列表名 value1 value2`：在列表左边添加元素。
  - 获取元素：
    - `rpop 列表`：从列表右边获取元素。
    - `lpop 列表`：从列表左边获取元素。
  - 获取长度：`llen 列表`。
  - `lindex 列表名 序号`：根据序号获取元素，可以为负值，表示倒数，通过遍历实现。
  - `lrange 列表名 起始 结束`：获取列表中一段元素。
  - `ltrim 列表 起始 结束`：定义区间，区间外的元素丢弃，实现定长列表。
- 字典操作
  - 创建：
    - 单个：`hset 字典名 key value`
    - 多个：`hmset 字典名 key1 value1 key2 value2`
  - 获取所有信息：`hgetall 字典名`，以键 值间隔出现
  - 获取字典长度：`hlen 字典名`。
  - 计数：`hincrby 字典名 键 增量`
- 集合
  - 添加元素：`sadd 集合名 key1 key2`。
  - 查看元素：`smembers 集合名`。
  - 判断是否存在：`sismember 集合名 key1`
  - 获取长度：`scard 集合名`
  - 弹出一个元素：`spop 集合名`
- 有序集合
  - 添加元素：`zadd 集合名 权重 元素`
  - 顺序排序：`zrange 集合名 起始位置 结束位置`
  - 倒序排序：`zrevrange 集合名 起始位置 结束位置`
  - 统计：`zcard 集合名`
  - 获取权重信息：`zscore 集合名 元素`
  - 获得排名：`zrank 集合名 元素`
  - 获得权重范围内的元素：`zrangebyscore 集合名 起始权重 结束权重`
  - 带权重信息：`zrangebyscore 集合名 起始(inf代表无穷大) 结束 withscores`
  - 删除元素：`zrem 集合 元素`
- 通用规则
  - 不存在则创建
  - 没有元素则删除
  - 过期时间：过期时间是以对象为单位的，而不是由其中一个子key决定，对一个字符串设置了过期时间，但是调用了`set`修改了，则过期时间会消失(是否所有都是的)。
    - 查看过期时间：`ttl 键`

## 应用

### 分布式锁

- 概念：并发编程中，当遇到修改共享资源时，必须确保其操作是原子的(不会被线程调度机制打断)，原子性操作很难实现，但是可以通过加锁来实现。分布式锁是用来保证分布式应用中，多个节点同一时刻只有一个线程在操作该资源。

- 实现：通过标志位来告知其他进程其已经被使用了。

  - 拥有锁：`setnx key value`
  - 设置超时时间：`expire  key timeout`（防止死锁）
  - 释放锁：`del key`

- 问题：`setnx`和`expire`是两条独立的指令，并非原子操作，如果执行完`setnx`后，线程就挂了，则会导致死锁。

- 解决方案：`set key value ex timeout nx（不存在）`

- 超时问题：分布式锁不能解决超时问题，加锁与释放锁的时间间隔大于了超时时间，则会导致另一个线程会获取该锁，因此不要用于较长时间的任务。安全的方案是：`value`设置一个id(随机值或线程id)，释放锁时要匹配ud是否相同，然后再决定是否删除，需要`Lua`脚本处理，`Lua`可以保证多个指令原子性执行。

- 可重入性(递归锁)：需要包装`set`方法，通过`ThreadLocal`统计当前持有锁的计数。

  ```python
  # -*- coding: utf-8 
  import redis 
  import threading 
  locks = threading.local() 
  locks.redis = {} 
  def key_for(user_id): 
  	return "account_{}".format(user_id) 
  def _lock(client, key): 
  	return bool(client.set(key, True, nx=True, ex=5)) 
  def _unlock(client, key): 
  	client.delete(key) 
  def lock(client, user_id): 
      key = key_for(user_id) 
      if key in locks.redis:
      	locks.redis[key] += 1 
      	return True 
      ok = _lock(client, key) 
      if not ok: 
      	return False 
      locks.redis[key] = 1 
      return True 
  def unlock(client, user_id): 
      key = key_for(user_id) 
      if key in locks.redis: 
     		locks.redis[key] -= 1   
      	if locks.redis[key] <= 0: 
      		del locks.redis[key] 
     		return True 
      return False 
  client = redis.StrictRedis() 
  print "lock", lock(client, "codehole") 
  print "lock", lock(client, "codehole") 
  print "unlock", unlock(client, "codehole") 
  print "unlock", unlock(client, "codehole") 
  ```

  - 集群情况下，客户端从主节点中申请了一把锁后，还未同步到从节点，主节点挂掉，从节点取代后，没有这个锁，这时可能会出现将一把锁同时分配给两个客户端。高可用。
    - `Redlock`算法，`redlock-py`实现了封装。采用大多数机制，加锁时，将命令向超过一半的节点发送，只有当一半的节点成功后，才认为加锁成功，释放锁时，向所有节点发送指令，由于需要向多个节点进行读写，因此性能会下降。使用时要多加考虑。

- 锁冲突问题(加锁没有加成功)

  - 直接抛出异常，用户自行决定是否重试。
  - 睡眠一定时间重试：睡眠会阻塞当前消息处理线程，从而导致后续消息处理出现延迟，极端情况下，死锁会导致一直加锁不成功，线程被彻底堵死。
  - 将请求放置延时队列，延后处理。

### 延时队列

- 通过列表来实现异步消息队列，通过`lpush`和`rpush`入队，`lpop`和`rpop`出队。
- 队空：消费者不停的pop，判断数据，从而导致空查询，降低性能。可以通过pop后，为空数据，则睡眠一定时间，但这会导致消息延迟增大。解决方案：`blpop`或`brpop`进行阻塞读，从而解决空查询和延迟问题。
- 空闲连接：消费者一直阻塞，则会变为闲置链接，通常超过一段时间，服务器会主动断开链接，减少闲置资源占用，这时会抛出异常。
- 实现

```python
# 采用zset实现，将消息序列化作为value，到期时间作为score
def delay(msg): 
    msg.id = str(uuid.uuid4())    # 保证 value 值唯一 
    value = json.dumps(msg) 
    retry_ts = time.time() + 5     # 5 秒后重试 
    redis.zadd("delay-queue", retry_ts, value) 
def loop(): 
    while True: 
    # 最多取 1 条 
    values = redis.zrangebyscore("delay-queue", 0, time.time(), start=0, num=1) 
    if not values:   
        time.sleep(1)    # 延时队列空的，休息 1s 
        continue 
    value = values[0]   # 拿第一条，也只有一条 
    success = redis.zrem("delay-queue", value)    # 从消息队列中移除该消息，用于抢夺任务 
    if success:     # 因为有多进程并发的可能，最终只会有一个进程可以抢到消息 
    msg = json.loads(value) 
    handle_msg(msg) 
```

- 优化：`zerm`抢夺不到任务的进行执行时会有浪费，可以通过`Lua`将`zrangebyscore`和`zrem`变为原子化操作。
- 为什么不能保证`100%`可靠性：消息被发送出去，消费者是否接收到消息redis不做保证，不像一般的mq，会有ack机制，要求消费者收到消息进行ack确认，超时未确认mq会再次投递消息，而redis没有这个机制。

### 位图

- 位图：每个数据只占一位，可以用于在签到中，大大节省空间。其内容实际也是普通字符串(byte数组)，可以通过`get`、`set`对整个位图进行操作，也可以通过`getbit`、`setbit`进行位数组操作。位数组是自动扩展的，扩展时，以0扩充。
  - `setbit 名 位置 值(0|1)`
  - `getbit 名 位置`
  - 统计指定范围1的个数：`bitcount 名 起始 结束`，以字节为索引，因此范围必须是8的倍数。
  - 查找第一个值的位置：`bitpos 名 值 起始 结束`
  - 多个位处理：`bitfield 名 指令(get|set|incrby) 类型连续位数 起始位`，最多64个连续位(无符号64位，有符号63位)。
    - `bitfield w get i4 0 指令2`：从w中的第一个为开始，取四个位，结果是有符号数。
    - 递增时，溢出默认折返(默认`wrap`)，还可以报错(`fail`)和截断(`sat`停留在最值)
      - `bitfield w incrby u4 2 1`
      - `bitfield w overflow sat incrby u4 2 1`
      - ` bitfield w overflow fail incrby u4 2 1`

### HyperLogLog

- **PV(Page View)**、**UV(Unique visitor)**，使用场景：去重计数。
- 统计`UV`
  - 访问量小时，可以采用为每个页面建立一个`set`去存储当天访问过该页面的用户ID。
  - 访问量大的话，`set`会浪费大量空间，而且访问量很大的情况下，`UV`统计不必太准确。`HyperLogLog`数据结构提供不精确的去重计数方案，其标准误差在`0.81%`。
- 操作：
  - 添加元素：`pfadd 名 用户`
  - 获取计数：`pfcount 名`
  - 累加`pf`计数值(对数据进行合并)：`pfmerge 名1 名2 名3`
- 注意事项：会占用12K的存储空间，Redis中，计数比较小时，采用稀疏矩阵存储，当空间使用较大时，才会转变为稠密矩阵，占12k的空间。

### 布隆过滤器

- 用途：判断一个值是否已经存在了，从而实现去重。但是对没有见过的数据可能会预判为见过。redis 4.0中作为一个插件存在。
- 使用：
  - 添加元素：
    - 单个：`bf.add 名 值`
    - 多个：`bf.madd 名 值1 值2`
  - 判断是否存在：
    - 单个：`bf.exists 名 值`
    - 多个：`bf.mexists 名 值1 值2`
- 误判：
  - `bf.reserve .error_rate`：错误率，错误率越低，需要的空间越大。
  - `bf.reserve .initial_size`：预计放入的元素个数，如果实际超过，则误判率上升。
- 原理：大型位数组+不同的无偏`hash`函数(将hash计算均匀)
  - 添加一个`key`时，对`key`进行多次`hash`，将多个位置置为1。
  - 判断存储与否时，多`key`进行hash，只要有一个位置为`0`，则该key不存在，如果都是，则极大概率存在。
  - 如果实际元素远大于初始化值，应该对布隆过滤器进行重建。
- 空间预估：
  - 预估数量$n$
  - 错误率$f$
  - 长度($l$)：$f=0.6185^{l/n}$
  - hash函数数量($k$)：$ k=0.7 *(l/n) $

### 简单限流

- 限流通常用于控制流量，控制用户行为，避免垃圾请求。

