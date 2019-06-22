# SQL

SQL语言是声明性的语言，只需通过SQL描述想要的数据，数据库管理系统会为我们提供相应的数据。ER图为实体-关系图，具备三要素：实体、属性、关系。

SQL保留字、函数名、绑定变量名大写，自己定义的小写

SQL语言按功能可以分为：

- DDL(Data Definition Language)：数据定义语言，用于定义数据库对象，如数据库、表、列。
- DML(Data Manipulation Language)：数据操作语言，用于操作与数据库相关的记录，如增加、删除、修改表中的记录。
- DCL(Data Control Language)：数据控制语言，用于定义访问权限和安全级别。
- DQL(Data Query Language)：数据查询语言，定于查询数据。

## 常用数据库

- 关系型数据库：建立在关系模型基础上的数据库。
  - MySQL
  - MariaDB：大部分与MySQL兼容。
- 键值型数据库：通过Key-Value键值的方式存储数据，查找速度快，但是不能自由的条件过滤，常用于内容缓存。
  - Redis
- 文档型数据库：以文档为单位存储信息，一个文档为一条记录。
  - MongoDB
- 搜素引擎：用于全文搜素，Elasticsearch，核心原理倒排索引。
- 图像数据库：用于存图结构。

## SQL执行原理

- Oracle：SQL语句会经过如下流程

  - 语法检查：语句拼写是否正确。
  - 语义检查：访问的对象是否存在，如表名，列名。
  - 权限检查：检查是否有访问该数据库的权限。
  - 共享池检查：获取SQL语句hash值，通过hash值检查库缓存(Library Cache)中查找，如果存在，则直接使用其缓存的执行计划，然后交由执行器(软解析)；不存在，则进入优化器。
  - 优化器：优化器根据SQL语句创建解析树、生成执行计划（硬解析）。
  - 执行器：根据解析树与执行计划执行SQL语句。
  - 共享池为Oracle的专属名称，包含库缓存、数据字典缓存区等
    - 库缓存决定SQL语句是否需要硬解析，应该避免硬解析(消耗资源)，为了避免硬解析，可以使用绑定变量，即在SQL语句中使用变量，提高软解析可能性，但是可能会导致生成的执行计划不够优化(每个表中使用绑定列表的列数据分布不均)。
    - 数据字典缓存区存储对象的定义，如表、视图、索引的等对象，在解析SQL语句时，可以直接从中获取目标对象的相关信息。

- MySQL：MySQL是经典的CS架构。

  - MySQL的服务端由`mysqld`提供，主要分为3层
    - 连接层：负责服务器端与客户端建立连接。
    - SQL层：对SQL语句进行查询处理。
    - 存储引擎层：与数据库文件交互，负责数据的存储和读取。
  - SQL层：
    - 缓存查询：Server查询缓存，如果存在这条语句则立即返回结果，MySQL8.0后取消该功能，当数据表被更新，则会清空所有缓存，因此只有当表为静态表，使用缓存查询才有意义。
    - 解析器：对SQL语句进行语法、语义分析。
    - 优化器：确定SQL的执行路径，如全表检索、索引检索。
    - 执行器：判断权限，执行SQL并返回结果(MySQL8.0以下会对查询结果进行缓存)。
  - 存储引擎层：MySQL中存储引擎是以插件的形式存在的，不同的引擎有不同的特点。
    - InnoDB：MySQL5.5.8以后默认存储引擎，支持事务、行级锁定、外键约束。
    - MyISAM：MySQL5.5.8之前的默认存储引擎，不支持事务与外键，优点是速度快、占用资源小。
    - Memory：采用内存作为存储介质，相应速度快，但当Server进程崩溃时，将丢失数据。适用于临时数据。
    - Archive：良好的压缩机制，适合文件归档。
  - 分析方法

  ```sql
  '查询分析是否打开'
  select @@profiling;
  '打开分析'
  set profiling=1;
  '执行查询语句'
  '查看产生的profiles'
  show profiles;
  '查看最近的'
  show profile;
  '根据id查看'
  show profile for query {id};
  ```

## DDL使用

DDL是DBMS的核心组件，也是SQL的重要组成部分，DDL的正确性和稳定性是整个SQL运行的重要基础。

### DDL语法：

DDL的语法主要是对数据库和数据表进行增、删、改操作。

数据库操作

- 增：`CREATE DATABASE 数据库名;`
- 删：`DROP DATABASE 数据库名;`

数据表操作(管理平台：Navicat)

- 创建：`CREATE TABLE 表名(列信息[列名 类型 列约束],补充信息[主键、索引])数据表约束[存储引擎、字符集]`

```sql
CREATE TABLE `player`(
    // 字段player_id 类型为int 长度为11位 非空 列值自增
	`player_id` int(11) NOT NULL AUTO_INCREMENT,
    // 字段team_id 类型为int 长度为11位 非空
    `team_id` int(11) NOT NULL,
    // 字段player_name 类型为varchar 长度为255位 字符集为utf8 排序规则为utf_general_ci 非空 
    `player_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
    // 字段height 类型为float 默认值为0.00
    `height` float(2,3) NULL DEFAULT 0.00,
    // player表的主键为player_id 索引方式为BTREE
    PRIMARY KEY(`player_id`) USING BTREE,
    // 为player_name字段设置索引 索引方式为BTREE
    UNIQUE INDEX `player_name` (`player_name`) USING BTREE,
)ENGINE = InnoDB CHARACTER SET=utf8 COLLATE=utf8_general_ci ROW_FORMAT=Dynamic;
// 数据表采用InnoDB引擎存储，字符集为utf8(MySQL中真utf8为utf8mb4，utf8是采用3字节)
// 排序规则为utf8_general_ci 行格式为Dynamic
```

- 删除表：`DROP TABLE 条件[IF EXISTS] 表名;`

- 修改：
  - 添加字段：`ALTER TABLE player ADD(age int(11));`
  - 修改字段名：`ALTER TABLE player RENAME COLUMN age TO player_age;`
  - 修改字段数据类型：`ALTER TABLE player MODIFY(player_age float(3,1));`
  - 删除字段：`ALTER TABLE player DROP COLUMN player_age;`

索引类型

- `UNIQUE INDEX`：唯一索引，索引值唯一。
- `NORMAL INDEX`：普通索引。

索引方式：

- `BTREE`
- `HASH`

### 数据表约束

列约束

- `PRIMARY KEY`：主键，不允许为NULL。
- `FOREIGN KEY`：外键
- `NOT NULL`：列值不能为空。
- `AUTO_INCREMENT`：主键自增。
- `UNIQUE`：列值唯一。
- `DEFAULT`：设置默认值。
- `CHECK(条件)`：条件约束。

### 设计数据表原则

- 数据表个数越少越好：RDBMS的核心为ER图，表代表实体，表越少，则实体与关系越清晰。
- 表中字段越少越好：字段最好相互独立，字段越少，数据冗余的可能性越小。
- 联合主键越少越好，索引空间小。
- 使用主键和外键越多越好：关系越多，实体间冗余度越小，数据利用度越高
- 核心简单可复用

主键用于区分数据的唯一性。外键确保表与表之间的引用关系；索引用于提高检索速度，主键是索引的一种。

为什么设计数据库不使用外键？

外键的优点：

- 阻止执行：
  - 修改、添加从表数据时，当数据在主表中不存在，则阻止操作。
  - 删除、修改主表主键时，必须清理从表相关行。
- 级联操作(触发器)：
  - 主表删除、修改主键值会同时修改从表，因此杜绝了一致性问题

- 保证数据一致性、完整性、关联性，数据冗余。

外键的缺点：

- 主表进行修改或变更时，涉及从表过多，导致业务暂时不可用。
- 对从表进行操作时，会检查外键约束，性能有下降。
- 通过触发器解决级联操作，不利于维护。

所以考虑是否用主键，要从性能和安全性上考虑，如果不是有外键，则需要用程序实现数据一致性和完整性。

互联网行业，因为加了外键后，会导致级联操作、一致性检查的压力都给了数据库服务器，所以数据库服务器性能成为了瓶颈，将约束通过中间层控制。
