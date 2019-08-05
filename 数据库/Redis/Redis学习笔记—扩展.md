# Redis学习笔记—扩展

## Info指令

Redis提供了`info`指令，可以查看Redis内部各个模块的参数：

- 服务器环境信息：`info server`
- 客户端统计数据：`info clients`
- 服务器内存数据：`info memory`
- 持久化信息：`info persistence`
- 通用信息：`info stats`
- 主从复制信息：`info replication`
- CPU使用状况：`info cpu`
- 集群信息：`info cluster`
- 键值对统计信息：`info keyspace`

### 常用操作

- 查看ops：`info stats|grep ops`，极限值是每秒钟`10W`次指令。
- 查看频繁访问的key：`monitor`
- 查看客户端详细信息：`client list`
- 查看拒绝连接次数：`info stats|grep reject`
- 查看增量同步缓冲区：`info replication |grep backlog `，增量同步缓存区太小容易出现从库断开后，缓冲区被覆盖，导致触发全量同步。
- 查看同步情况：`info stats |grep sync`。

## 过期策略

Redis是单线程的，因此如果同一时间有很多key过期，处理所有的过期key会出现卡顿现象。为了避免这个问题，Redis将设置了过期时间的key放入独立过期字典中，采用两种策略删除到期的key：

- 定时扫描策略：默认每秒进行10次过期扫描，删除满足条件的key。
- 惰性删除：当客户端访问key时，Redis判断是否需要删除key。

### 定时扫描

定时过期扫描不会扫描整个过期字典，每次只随机选择20个key，删除已经过期的key，如果过期率超过`25%`，则重复操作，但是最多只执行`25ms`。

假设实例中所有的key都在同一时间过期，这会导致Redis在响应客户时出现严重得卡顿，排队越后的，卡顿现象越严重(每次访问都会触发删除操作，而且内存管理器需要频繁回收内存页，存在一定的CPU消耗)。因此要避免大量的key集中过期，需要将key的过期时间设置在一个随机范围内。

### 从库的过期策略

从库不会进行过期扫描，因为主库在key到期后，会在AOF中添加del指令。Redis中指令同步是异步进行的，因此会出现主库已删除的数据在从库中存在。

## LRU

当Redis的内存使用超过了物理内存限制时，内存的数据会开始和磁盘进行频繁的交换，从而导致Redis性能下降。可以通过`redis.conf`的`maxmemory`限制最大内存使用。Redis提供如下策略`maxmemory-policy`可供选择：

- noeviction：默认策略，将不能提供写服务，只能进行读或删除服务。
- volatile-lru：对设置了过期时间的key采用LRU淘汰策略(LRU：最近最少使用策略，按使用时间排序)，可以保证需要持久化的数据不会突然丢失。
- allkeys-lru：对所有的key采用LRU淘汰策略。
- volatile-lfu：对设置了过期时间的key采用LFU淘汰策略(LFU：最不常使用策略，按使用次数排序)。
- allkeys-lfu：对所有的key采用LFU淘汰策略。
- volatile-random：对设置了过期时间的key采用随机淘汰策略。
- allkeys-random：对所有的key采用随机淘汰策略。
- volatile-ttl：对设置了过期时间的key，淘汰ttl最小的key。

### LRU算法

### 近似LRU算法

Redis中采用的是近似LRU算法，避免了消耗大量的额外内存。近视LRU算法会采用随机采样法来淘汰元素，Redis为每个key添加一个额外24bit的字段，用于记录最后一次被访问的时间戳。当Redis执行写操作时，如果内存使用超过`maxmemory`，执行LRU淘汰算法，随机取出5个key(`maxmemory-samples`设置)，淘汰最旧的key，直到内存使用低于`maxmemory`。Redis中添加了淘汰池(淘汰池的大小为maxmemory，每次淘汰循环，将随机选出的key加入淘汰池，然后淘汰最旧的key)，提升近似LRU算法的效果。

## 懒惰删除

## Redis安全保护