# Redis学习笔记—应用

## 分布式锁

### 并发锁

并发编程中，修改共享资源时，必须确保其操作是原子性(不会被线程调度机制打断)。原子性操作很难实现，但可通过在修改操作中加锁实现同一时刻只有一个线程在操作该资源。多线程访问本地Redis。

```python
import redis
import threading

lock = threading.Lock()

def multi_thread_set():
    import random
    import time
    client = redis.StrictRedis(host='127.0.0.1', port=6379)
    lock.acquire()
    try:
        info = client.get('info')
        time.sleep(random.random())
        client.set('info', int(info) + 1)
    finally:
        lock.release()

def test():
    client = redis.StrictRedis(host='127.0.0.1', port=6379)
    client.set('info', 0)

    threads = [threading.Thread(target=multi_thread_set) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert int(client.get('info')) == 5
    client.delete('info')

if __name__ == '__main__':
    test()
```

### 分布式锁

分布式应用中，必须确保同一时刻在多个节点中只能有一个线程在修改该共享资源。此时，线程锁将不再生效，因为线程锁只能保证本节点在同一时刻只有一个线程工作。这是就需要使用分布式锁来控制多个节点的并发操作。

![分布式锁]()

分布式锁的本质是在Redis中创建一个标准位：客户端先使用`setnx(set if not exist)` 指令尝试创建该标志位，若创建成果，则进行后续操作，完成操作后，再通过`del`指令释放标志位。这里存在一个问题，若客户端获取标志位后，出现了异常，导致无法调用`del`指令，则会陷入死锁。这是有两种解决方案：

- 客户端通过设置异常处理机制调用`del`指令(客户端没有崩溃的情况下)。
- 通过`set 锁 锁信息 ex 超时时间 nx OK`指令在创建标志位时为其添加超时时间。

```python
import redis
import threading

def multi_thread_set():
    import random
    import time
    client = redis.StrictRedis(host='127.0.0.1', port=6379)
    while client.set('lock', '1', ex=5, nx=True) is None:
        time.sleep(0.1)
    try:
        info = client.get('info')
        time.sleep(0.1 * random.randrange(1, 4))
        client.set('info', int(info) + 1)
    finally:
        client.delete('lock')

def test():
    client = redis.StrictRedis(host='127.0.0.1', port=6379)
    client.set('info', 0)

    threads = [threading.Thread(target=multi_thread_set) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert int(client.get('info')) == 5
    client.delete('info')

if __name__ == '__main__':
    test()
```

即使有了超时处理机制，也存在当逻辑操作时长大于锁的超时限制出现不安全操作：ABC三个线程同时请求锁，A线程拿到了锁，并处理逻辑，这是锁过期了导致B线程拿到了锁，在B执行逻辑操作时，A完成了逻辑操作，执行锁释放操作，因此会导致线程C也拿到了锁。

针对这种情况，需要在锁的value中存放一个随机数(线程ID)，释放锁时先判断随机数是否一致，然后再决定是否删除(但这里有一个问题：匹配value和删除锁不是原子操作，需要搭配Lua脚本)。

```python
import redis
import threading

def multi_thread_set():
    import random
    import time
    client = redis.StrictRedis(host='127.0.0.1', port=6379)
    while client.set('lock', threading.currentThread().ident, ex=5, nx=True) is None:
        time.sleep(0.1)
    try:
        info = client.get('info')
        time.sleep(0.1 * random.randrange(1, 4))
        client.set('info', int(info) + 1)
    finally:
        # 比较操作和删除操作 非原子操作
        if client.get('lock') and client.get('lock')==threading.currentThread().ident:
            client.delete('lock')

def test():
    client = redis.StrictRedis(host='127.0.0.1', port=6379)
    client.set('info', 0)

    threads = [threading.Thread(target=multi_thread_set) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert int(client.get('info')) == 5
    client.delete('info')

if __name__ == '__main__':
    test()
```

### 集群分布式锁

在集群环境下，分布式锁也存在缺陷：当客户端A在主节点获取锁后，主节点挂掉，从节点会取而代之，但此时由于异步同步，从节点可能没有该锁的信息，可能会存在客户端B也获得了该锁。为了解决这个问题，Redis添加了`Redlock`算法(`redlock-py`模块实现了封装)。`Redlock`算法采用大多数机制来解决该问题：加锁时，会将该指令同步给过半的节点，只要当过半节点执行成功后，则认为加锁成功；释放锁时，向所有节点下发`del`指令，由于涉及到多个节点读写，因此相比单实例性能有所下降。使用时需要使用多个相互独立的`Redis`实例。

```python
import redlock

addrs = [{
    "host": "localhost",
    "port": 6379,
    "db": 0
}, {
    "host": "localhost",
    "port": 6479,
    "db": 0
}, {
    "host": "localhost",
    "port": 6579,
    "db": 0
}]
dlm = redlock.Redlock(addrs)
success = dlm.lock("user-lck-laoqian", 5000)
if success:
    print('lock success')
    dlm.unlock('user-lck-laoqian')
else:
    print('lock failed')
```

## 消息队列

Redis可以通过`list`搭配`lpush`和`rpop`指令，实现只有一组消费者的消息队列，但是Redis的消息队列没有ack保证，不适用于对消息可靠性有很高要求的应用。

![消息队列]()

如果出现队列为空时，客户端频繁对队列使用`rpop`操作会导致Redis的性能下降，针对这种情况有两种解决方案：

- 当获取不到数据时，客户端主动睡眠，但会导致消息延迟大。
- 采用`brpop`指令，当队列没有数据时，会阻塞；如果有数据后，会立即恢复。

如果客户端被阻塞很长时间后，会导致该链接被视作为闲置链接。闲置时间过长，服务器会主动断开链接，减少闲置资源占用，因此`brpop`指令会抛异常`ConnectionError`，因此需要做好异常处理机制。

### 延时队列

分布式锁中，当客户端加锁失败后，我们采用的解决方案：客户端主动sleep一定时间，但是该方案会存在两个问题：

- sleep会阻塞当前线程，导致后续消息处理出现延迟。
- sleep时间不合适，线程可能会很迟才能获得锁。
- 线程因为死锁阻塞，导致后续消息无法处理。

针对这种情况，可以将冲突请求存放到一个延迟队列中延后处理避开冲突。在Redis中，可以使用`zset`实现延时队列，将消息序列化后存入value中，以消息的到期时间作为score，通过`zrangebyscore`指令获取最近一个要过期的消息，进行处理。然后使用多进程(保障可用性)来轮询`zset`，这里为了避免因为并发导致任务被多次执行，可以采用两种方案：

- 采用锁机制。
- 通过CAS机制，先获取消息，然后去删除消息，如果删除成功，则表明该进程获得了消息；删除失败，则获取消息失败。

```python
import random
import threading
import time
import pickle
import uuid
import redis
from datetime import datetime, timedelta

class Task(object):
    def __init__(self, msg):
        self._msg = msg
        self._id = uuid.uuid4()

    @property
    def msg(self):
        return "consumer" + self._msg

def handle_msg(task):
    time.sleep(0.1 * random.randrange(1, 4))
    print("{} handing {}".format(threading.current_thread().ident, task.msg))

class RedisDelayingQueue(object):
    def __init__(self, client, queue_name):
        self._client = client
        self._queue_name = queue_name

    def delay(self, msg):
        task = Task(msg)
        value = pickle.dumps(task)
        dt = datetime.now() + timedelta(seconds=5)
        self._client.zadd(self._queue_name, {value: int(dt.timestamp())})

    def loop(self):
        while True:
            now = datetime.now().timestamp()
            values = self._client.zrangebyscore(self._queue_name, 0, int(now),
                                                start=0, num=1)
            if not values:
                print(
                    "{} waiting task".format(threading.current_thread().ident))
                time.sleep(1)
                continue
            value = values[0]
            # 判断是否抢占任务成功
            success = self._client.zrem(self._queue_name, value)
            if success:
                task = pickle.loads(value)
                handle_msg(task)

def producer_task(delay_queue):
    for i in range(10):
        delay_queue.delay('task' + str(i))

def consumer_task(delay_queue):
    delay_queue.loop()

if __name__ == '__main__':
    client = redis.StrictRedis(host='127.0.0.1', port=6379)
    delay_queue = RedisDelayingQueue(client, 'tasks')
    producer = threading.Thread(target=producer_task, args=(delay_queue,))
    consumers = [threading.Thread(target=consumer_task, args=(delay_queue,))
                 for _ in range(2)]
    producer.start()
    for consumer in consumers:
        consumer.start()

    producer.join()
    for consumer in consumers:
        consumer.join()
```

该实现有一个小问题：同一个任务会被多个进程获取，但是只能有一个进程获抢占该任务，因此会出现大量的无效任务获取，可以采用`lua`脚本将`zrangebyscore`和`zrem`封装为一个原子化操作，因此可以避免多个进程之间抢占任务。

### 为什么Redis作为消息队列无法保证100%可靠性呢？

因为消息队列没有`ack`机制，因此只能保证消息被发送出去，但是不能保证消息被客户端收到，而且也不能保证消息被客户端正确处理了。

## 位图

位图可以用于需要存储bool类型数据的场景，如：用户一年的签到记录，每一位代表一天。通过位图可以节约大量存储空间。

![位图]()

在Redis中，位图实际是普通的字符串，只是可以进行位图操作`getbit/setbit`，也可以通过`get/set`进行字节操作，可以将其是作为位数组。

![通过位操作设置字母h]()

位数组支持自动扩展，当访问的位置超出现有内容范围，自动进行零扩充。

```python
import redis

client = redis.StrictRedis(host='127.0.0.1', port=6379)
for index, data in enumerate('01101000'):
    client.setbit('data', index, int(data))
assert client.getbit('data', 0) == 0
assert client.getbit('data', 1) == 1
assert client.getbit('data', 2) == 1
assert client.getbit('data', 3) == 0
assert client.getbit('data', 4) == 1
assert client.getbit('data', 5) == 0
assert client.getbit('data', 6) == 0
assert client.getbit('data', 7) == 0
assert client.get('data')==b'h'
client.delete('data')
```

Redis提供了三个位图指令：

- 位图统计指令`bitcount key [start end]`：统计指定范围内`1`的个数。
- 位图查找指令`bitpos key bit [start end]`：查找指定范围内出现的第一个`0`或`1`。
- start、end是字节索引，并不是位索引，因此必须是8的倍数。
- 多位处理指令`bitfield key 指令`：支持三个子指令`get/set/incrby`，用于对指定位片段进行读写操作，最多可以处理64个连续的位。
  - 子指令的格式
    - `get u4 0`：从第一位开始，将接下来的`4`位视作为无符号数。
    - `set u4 0 5`：从第一位开始，将接下来的`4`位用无符号数`5`替换。
    - `incrby u4 0 1`：从第一位开始，将接下来的`4`位无符号数`+1`。
  - 数据类型
    - `u`：无符号数。
    - `i`：有符号数。
  - 溢出策略`overflow`，只影响接下来第一条指令。
    - 默认折返(wrap)：溢出后，循环。
    - 失败报错不执行(fail)：溢出后报错
    - 饱和截断(sat)：超过范围后，只停留在最大|最小值。

```python
import redis

client = redis.StrictRedis(host='127.0.0.1', port=6379)
# 01101000
client.set('data', 'h')
assert client.bitcount('data', 0, 1) == 3
assert client.bitpos('data', 1, 0, 1) == 1
assert client.bitfield('data').get('u4', 0).execute() == [6]

client.bitfield('data').set('u4', 0, 7).execute()
assert client.bitfield('data').get('u4', 0).execute() == [7]

client.bitfield('data').incrby('u4', 0, 1).execute()
assert client.bitfield('data').get('u4', 0).execute() == [8]
for i in range(8):
    client.setbit('data', i, 1)
assert client.bitfield('data').get('u8', 0).execute() == [255]

assert client.bitfield('data', 'fail').incrby('u8', 0, 1).execute()==[None]

client.bitfield('data', 'sat').incrby('u8', 0, 1).execute()
assert client.bitfield('data').get('u8', 0).execute() == [255]

client.bitfield('data', 'wrap').incrby('u8', 0, 1).execute()
assert client.bitfield('data').get('u8', 0).execute() == [0]

client.delete('data')
```

## HyperLogLog

当需要统计一个页面的**UV(Unique visitor)**时，需要根据访问用户的ID对页面的访问进行去重，这时有两种解决方案：

- 为每个页面添加一个**set**用于去重，当访问量很大时，会浪费很多空间。
- 利用Redis的HyperLogLog数据结构，提供不精确的统计。

HyperLogLog 提供两个指令：

- `pfadd key element`：添加记录
- `pfcount key`：获得计数。
- `pfmerge  key key`：将多个pf计数值累计。

```python
import redis

client = redis.StrictRedis(host='127.0.0.1', port=6379)
total = 100000
for i in range(total):
    client.pfadd('counter', i)
now = client.pfcount('counter')
print("精确访问量：{}\n 实际访问量：{} \n 误差{}%".format(
    total, now, (total - now) * 100 / total)
)

client.delete('counter')
```

### 实现原理

Redis对HyperLogLog的存储进行了优化，当计数很小时，采用稀疏矩阵存储，空间占用小，只有当计数较大时，才会采用稠密矩阵存储，占用12K的空间。

![HyperLogLog实现原理]()

HyperLogLog是给定的一系列随机整数，通过低位连续零位最大长度K来估算随机数的数量N。N和K之间的关系为：

```python
import math
import random


# 算低位零的个数
def low_zeros(value):
    for i in range(1, 32):
        if value >> i << i != value:
            break
    return i - 1


# 通过随机数记录最大的低位零的个数
class BitKeeper(object):
    def __init__(self):
        self.maxbits = 0

    def random(self):
        value = random.randint(0, 2 ** 32 - 1)
        bits = low_zeros(value)
        if bits > self.maxbits:
            self.maxbits = bits


class Experiment(object):
    def __init__(self, n):
        self.n = n
        self.keeper = BitKeeper()

    def do(self):
        for i in range(self.n):
            self.keeper.random()

    def debug(self):
        print(
            f"总数N为：{self.n} log2N为：{math.log(self.n, 2):0.2f}, 低位连续零最大长度为：{self.keeper.maxbits}")


for i in range(100000, 1000000, 100000):
    exp = Experiment(i)
    exp.do()
    exp.debug()
    
"""
总数N为：100000 log2N为：16.61, 低位连续零最大长度为：17
总数N为：200000 log2N为：17.61, 低位连续零最大长度为：18
总数N为：300000 log2N为：18.19, 低位连续零最大长度为：19
总数N为：400000 log2N为：18.61, 低位连续零最大长度为：19
总数N为：500000 log2N为：18.93, 低位连续零最大长度为：21
总数N为：600000 log2N为：19.19, 低位连续零最大长度为：18
总数N为：700000 log2N为：19.42, 低位连续零最大长度为：17
总数N为：800000 log2N为：19.61, 低位连续零最大长度为：18
总数N为：900000 log2N为：19.78, 低位连续零最大长度为：23
"""
```

通过测试，可以看到K与N之间近似满足：$K=log_2(N)$。

- 统计

```python
import math
import random


def low_zeros(value):
    for i in range(1, 32):
        # 先右移再左移，左移时补充的是0，所以有1时，移动后值会变化
        if (value >> i) << i != value:
            break
    return i - 1

class BitKeeper(object):
    def __init__(self):
        self.maxbits = 0

    def random(self, value):
        bits = low_zeros(value)
        if bits > self.maxbits:
            self.maxbits = bits

class Experiment(object):
    def __init__(self, n, k=1024):
        self.n = n
        self.k = k
        self.keepers = [BitKeeper() for _ in range(k)]

    def do(self):
        for _ in range(self.n):
            value = random.randint(1, 1 << 32 - 1)
            # 取高16位，采用1024个桶
            keeper = self.keepers[
                ((value & 0xfff0000) >> 16) % len(self.keepers)]
            keeper.random(value)

    def estimate(self):
        sumbits_inverse = 0  # 零位数倒数
        #  计算调和平均(倒数的平均=总数/倒数之和
        # 调和平均可以有效平滑离群值的影响
        for keeper in self.keepers:
            if keeper.maxbits == 0:
                sumbits_inverse += keeper.maxbits
            else:
                sumbits_inverse += 1.0 / float(keeper.maxbits)

        avgbits = float(self.k) / sumbits_inverse  # 调和平均零位数

        return (2 ** avgbits) * self.k  # 根据桶的数量对估计值进行放大

for i in range(100000, 1000000, 100000):
    exp = Experiment(i)
    exp.do()
    est = exp.estimate()
    print(f"实际值:{i},预测值:{est:.2f},误差:{(abs(est - i)*100 / i):.5f}%")
"""
实际值:100000,预测值:92411.78,误差:7.58822%
实际值:200000,预测值:188961.64,误差:5.51918%
实际值:300000,预测值:295064.79,误差:1.64507%
实际值:400000,预测值:391421.11,误差:2.14472%
实际值:500000,预测值:492969.06,误差:1.40619%
实际值:600000,预测值:627868.13,误差:4.64469%
实际值:700000,预测值:693719.51,误差:0.89721%
实际值:800000,预测值:794618.48,误差:0.67269%
实际值:900000,预测值:939156.95,误差:4.35077%
"""
```

Redis中采用了`2^14=16384`个桶，每个桶的最大maxbits占6bit，最大可表示`maxbits=63`，因此总占用内存`2^14 * 6 / 8 = 12k `。

## 布隆过滤器

布隆过滤器通常用于解决去重问题，如：垃圾邮件过滤、防止缓存穿透(访问不存在的数据时，每次都会去访问数据库，而不会访问缓存)。布隆过滤器只能精确的判断值不存在，但是对值存在可能会出现误判。

### 安装

```bash
# 拉取镜像
➜  Desktop docker pull redislabs/rebloom
# 创建容器
➜  Desktop docker run -d -p 6379:6379 --name bloomfilter redislabs/rebloom
# 启动交互平台
➜  Desktop docker exec -it bloomfilter redis-cli
```

### 常用指令

- 显示创建：`bf.reserve key error_rate initial_size`
  - `error_rate`：错误率越低，需要的空间越大，默认值`0.01`。
  - `initial_size`：预计放入元素数量，当实际数量超过时，误判率会上升，默认值`100`。
- 添加元素：`bf.add|bf.madd  key value`
- 判断元素是否存在：`bf.exists|bf.mexists key value`

### Python使用布隆过滤器

```python
import redis

client = redis.StrictRedis(host='localhost', port='6379')
# 添加用户
user_number = 10000
not_include = 0

for i in range(user_number):
    client.execute_command('bf.add', 'users', f'user_{i}')
    ret = client.execute_command('bf.exists', 'users', f'user_{i + 1}')
    if ret == 1:
        not_include += 1

print(
    f"共计：{user_number}，实际误判：{not_include}，误判率：{not_include * 100 / user_number}%")

client.delete('users')
```

### 原理

布隆过滤器的数据结构时一个位数组，其原理是采用计算元素的hash值，然后将位数组对应的位置设置为1，因此可以通过位数组来判断元素是否已经存在。计算哈希时会出现hash冲突，因此可以通过设置多个位+多个hash函数来降低hash冲突的概率，同一个元素的对应的多个位有一位不为`1`，则元素不存在。

![](Raw/应用/布隆过滤器.png)

使用时不要让实际元素数量远大于初始化大小(错误率会上升)，应该重新分配一个更大的过滤器。

布隆过滤器的空间占用估计公式：

- $k=0.7*(l/n)$：$k$为hash函数数量，$l$为位数组长度，$n$为预计元素数量。
- $f=0.6185^{(l/n)}$：$f$为误判率。

实际元素数量超出时，误判率变化公式：

- $f=(1-0.5^t)^k$：$t$为实际元素和预计元素倍数。

![](Raw/应用/误判率变化曲线.png)
$k$值分别为错误率为$10.0\%、1\%、0.1\%$时。

## 限流
限流通常用于控制流量(系统处理能力有限时，限制访问流量)和控制用户行为，避免垃圾请求(限制用户的某种行为在规定时间内的次数)。

### 简单限流

简单限流一般用于限定用户的某个行为在指定时间内最多只能发生N次(不能太大)。在Redis中，可以通过`zset`实现一个滑动时间窗口：`score`用于记录行为发生的时间，通过`zremrangebyscore `指令可以删除时间窗口之外的数据，通过`zcard`可以获得窗口之内的行为数量。这里有一点需要：要防止冷用户(规定时间范围内没有发生该动作)的`zset`占用内存，因此可以更新一下该`zset`的过期时间，时间设置为窗口长度`+1s`。

```python
import time
import redis
import uuid

client = redis.StrictRedis(host='localhost', port='6379')

def is_action_allowed(user_id, action_key, period, max_count):
    key = 'hist:%s:%s' % (user_id, action_key)
    now_ts = int(time.time() * 1000)  # 毫秒时间戳
    with client.pipeline() as pipe:  # client 是 StrictRedis 实例
        # 记录行为
        pipe.zadd(key, {str(uuid.uuid4()): now_ts})  # value 和 score 都使用毫秒时间戳
        # 移除时间窗口之前的行为记录，剩下的都是时间窗口内的
        pipe.zremrangebyscore(key, 0, now_ts - period * 1000)
        # 获取窗口内的行为数量
        pipe.zcard(key)
        # 设置 zset 过期时间，避免冷用户持续占用内存
        # 过期时间应该等于时间窗口的长度，再多宽限 1s
        pipe.expire(key, period + 1)
        # 批量执行
        a, b, current_count, _ = pipe.execute()
        # 比较数量是否超标
        return current_count <= max_count

for i in range(20):
    print(is_action_allowed("laoqian", "reply", 60, 5))
```

简单限流策略不适用于行为发生次数很大时的应用，因为会消耗大量存储空间。

### 漏斗限流

漏斗限流的灵感来自于漏斗。

![](Raw/应用/漏斗算法灵感.png)

漏斗的容量是固定的，其代表当前行为的可持续进行的最大量，漏嘴的流水率代表当前行为的最大频率。因此，单机漏斗算法：

```python
import time

class Funnel(object):
    def __init__(self, capacity, leaking_rate):
        self._capacity = capacity
        self._leaking_rate = leaking_rate
        # the remaining space
        self._left_quota = capacity
        # the last leaking time
        self._leaking_ts = time.time()

    def make_space(self):
        """trigger space transformation"""
        now_ts = time.time()
        delta_ts = now_ts - self._leaking_ts
        delta_quota = delta_ts * self._leaking_rate
        if delta_quota < 1:
            return
        self._left_quota += delta_quota
        self._leaking_ts = now_ts
        if self._left_quota > self._capacity:
            self._left_quota = self._capacity

    def watering(self, quota):
        self.make_space()
        if self._left_quota > quota:
            self._left_quota -= quota
            return True
        return False

funnels = {}

def is_action_allowed(user_id, action_key, capacity, leaking_rate):
    key = f'{user_id}:{action_key}'
    funnel = funnels.get(key)
    if not key:
        funnel = Funnel(capacity, leaking_rate)
    return funnel.watering(1)
```

在分布式的漏斗算法实现时，可以将`Funnel`的字段存储到一个`hash`结构中，灌水时将字段读出后，回填新值。在这个过程中，无法保证原子性，因此必须对取值、计算和回填这三个过程加锁，这意味着加锁失败后需要重试或放弃，导致性能下降或影响用户体验。可以采用`Redis-Cell`模块，其支持的指令为`cl.throttle key 容量 数量 时间 本次申请数量`，漏斗的漏水速度为`数量/时间`。

```bash
# 15 容量 30/60(s) 漏水数率
> cl.throttle laoqian:reply 15 30 60
1) (integer) 0 # 0 表示允许， 1 表示拒绝
2) (integer) 15 # 漏斗容量 capacity
3) (integer) 14 # 漏斗剩余空间 left_quota
4) (integer) -1 # 如果拒绝了，需要多长时间后再试(漏斗有空间了，单位秒)
5) (integer) 2 # 多长时间后，漏斗完全空出来(left_quota==capacity，单位秒)
```

## GeoHash

在地图中，位置数据时通过经纬度来表示，如果要查找坐标(x,y)附近的人，则需要查找$(x\pm r,y\pm r)$范围内的数据，因此可以通过SQL指令`SELECT * from poitions where x0-r<x<x0+r and y0-r<y<y0+r`，但是这对服务器压力很大，在高并发场景下，数据库将成为瓶颈。

另一种方案是采用距离位置排序算法GeoHash，GeoHash算法将二维的经纬度数据映射为一维的整数，二维上相邻的坐标在一维上也很接近。GeoHash将地球看做一个二维平面，如围棋棋盘，为每一个格子进行整数编码，越靠近的方格编码越接近，当获得编码后还能反推出对应的经纬度，因此方格越小，精度越高。

Redis中编码为52位整数值，其内部结构为zset，将编码值作为`score`，通过`score`排序即可获得附近的其他元素。其支持的命令有：

- 添加：`geoadd key 经度 纬度 地点名`，如`geoadd company 116.48105 39.996794 juejin `
- 计算距离：`geodist key 地点 地点 单位`，如`geodist company juejin ireader km `，支持的距离单位有`m(米)`、`km(千米)`、`ml(英里)`、`ft(尺)`。
- 获取经纬度：`geopos key 地点`，如`geopos company juejin`。
- 获取元素的经纬度编码：`geohash key 地点`，返回值是base32编码，可以通过`http://geohash.org /编码`查看定位是否正确。
- 根据地点查询附近地点：`georadiusbymember key 地点 距离 单位 [可选项] count 数量 排序方式`，如`georadiusbymember company ireader 20 km count 3 asc `，获得ireader附近20公里内正序排序后的前3个地点。其支持的显示可选项有：
  - `withcoord`：现在坐标。
  - `withdist`：显示距离。
  - `withhash`：显示编码值。
- 根据坐标查询附近地点：`georadius key 经度 纬度 距离 单位 [可选项] count 数量 排序方式`。

集群环境下单个key的数据量不易超过1M(迁移时很麻烦)，因此Geo最好使用单独Redis实例部署，不要使用集群环境，如果数据量过大，可以通过拆分数据降低单个zset集合的大小，如按省、市、区划分。

```python
import redis

client = redis.StrictRedis(host='127.0.0.1', port='6379')
client.geoadd('company', 16.48105, 39.996794, 'juejin')
client.geoadd('company', 16.514203, 39.905409, 'ireader')
client.geoadd('company', 16.489033, 40.007669, 'meituan')
client.geoadd('company', 16.562108, 39.787602, 'jd')
client.geoadd('company', 16.334255, 40.027400, 'xiaomi')
print(f"distance between juejin and ireader:",
      f"{ client.geodist('company', 'juejin', 'ireader', 'km')} km")

print(f"the position of juejin:", client.geopos('company', 'juejin'))
print(f"the geohash of juejin:", client.geohash('company', 'juejin'))
print(f"the companies nearby juejin 20km:",
      client.georadiusbymember('company', 'juejin', 20, 'km', count=3)
      )
client.delete('company')
```

## Scan
