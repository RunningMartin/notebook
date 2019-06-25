# MySQL使用

## 数据库操作

- 查看所有数据库：`SHOW DATABASES;`
- 使用数据库：`USE 数据库名;`

## 数据表操作

- 查看所有数据表：`SHOW TABLES;`

- 查看表列信息：`SELECT COLUMNS FROM 表名;`

- 创建表：

  ```mysql
  CREATE TABLE [IF NOT EXISTS] 表名{
  列名 类型 列约束(主键|非空(NOT NULL)|自增(AUTO_INCREMENT)|字符集(SET 字符集)|排序(COLLATE )),
  数据表描述信息(主键(PRIMARY KEY)|外键(FOREIGN  KEY)|索引(INDEX))
  }数据表约束(数据引擎(ENGINE)|字符集(SET)|排序(COLLATE) ;
  ```

  - 列约束
    - `PRIMARY KEY`：主键，主键必须是惟一的，可以为单一或组合值，不允许为NULL。
    - `FOREIGN KEY`：外键，外键不能夸引擎。
    - `NOT NULL`：列值不能为空。
    - `AUTO_INCREMENT`：主键自增，可以通过`last_insert_id()`查询最后一个值，一个表只能有一个字段为自增，且必须索引。
    - `UNIQUE`：列值唯一。
    - `DEFAULT`：设置默认值。
    - `CHECK(条件)`：条件约束。

- 更新表：最佳是采用`INSERT SELECT`重建新表，把旧表数据导入，然后在重命名新表。

  - 添加字段：`ALTER  TABLE 表名 ADD (字段信息);`
  - 重命名字段：`ALTER TABLE 表名 RENAME COLUMn 旧列名 TO 新列名;`
  - 修改字段信息：`ALTER TABLE 表名 MODIFY COLUMN 字段 类型 DEFAULT 默认值 COMMENT 注释;`
  - 修改字段数据类型：`ALTER TABLE 表名 MODIFY(列名 float(3,1));`
  - 删除字段：`ALTER TABLE 表名 DROP COLUMN 字段;`

- 删除表：`DROP TABLE 表;`

- 重命名：`RENAME TABLE 旧名 TO 新名;`

## 数据操作

### 检索数据

- 语法：`SELECT 显示信息 FROM 表(实体表或虚拟表) WHERE 筛选条件 HAVINT ??? GROUP BY 分组条件 ORDER BY 排序条件 LIMIT 限制结果数量;`

- 行数据去重：显示信息中使用`DISTINCT`关键字，作用于所有列。

- 限制结果数量：`LIMIT [起始行,]最大行数`：起始行序号从`0`开始，可选。替代语法`LIMIT 最大行数 OFFSET 起始行`

- 完全限定表名：`表名.列名`，有利于区别不同表的同名列。

- 排序：`ORDER BY 列名或条件 排序规则`，排序规则支持`ASC`升序，`DESC`降序，其排序策略由字符集指定。支持多列排序与非显示列排序。

- 过滤

  - 比较运算符

    | 操作符            | 含义           |
    | ----------------- | -------------- |
    | `=`               | 等于           |
    | `!=|<>`           | 不等于         |
    | `<|<=`            | 小于，小于等于 |
    | `>|>=`            | 大于，大于等于 |
    | `BETWEEN a AND b` | 在a，b之间     |
    | `IS NULL`         | 空值判断       |

  - 逻辑运算符

    | 操作符       | 含义       |
    | ------------ | ---------- |
    | `AND`        | 且         |
    | `OR`         | 或         |
    | `NOT`        | 非         |
    | `IN （a,b）` | 是否是a或b |

  - 逻辑运算符计算次序：`AND`优先级更高，应该合理运用括号。

  - 通配符过滤：`LIKE '通配符表达式'`，`LIKE`是对整个列进行匹配。通配符速度慢，最好不要将通配符放在开始位置。

    | 通配符 | 含义                                |
    | ------ | ----------------------------------- |
    | `%`    | 任意字符出现`>=0`次，但是不匹配NULL |
    | `_`    | 任意字符出现`1`次                   |

  - 正则过滤：`REGEXP [BINARY] '正则'`，只支持正则的一个子集。正则是对列值进行匹配。正则不区分大小写，可以用`BINARY`关键字修饰。

    | 正则      | 含义                                     |
    | --------- | ---------------------------------------- |
    | `.`       | 任意字符                                 |
    | `?`       | 出现0或1次                               |
    | `*`       | `>=`0次                                  |
    | `+`       | `>=1`次                                  |
    | `{n,[m]}` | 至少出现n次，最多m次                     |
    | `|`       | 或                                       |
    | `[]`      | 提供匹配可能性，如[123]，搭配`^`，表达否 |
    | `-`       | 在`[]`中表达范围，`[0-9]`=`[0123456789]` |
    | `\`       | 转义，用于匹配特殊字符                   |
    | `^`       | 文本开头                                 |
    | `$`       | 文本结尾                                 |
    | `[[:`     | 词开头                                   |
    | `[[:>:]]` | 词结尾                                   |

    正则测试：`SELECT 文本 REGEXP '正则'`

### 计算字段

什么是计算字段？

计算字段是将数据库中存储的原始数据处理为应用所需要的数据格式。可以通过`SELECT 计算字段`进行测试。

- `Concat(串(字段|字符串))`：将串连接起来。
- `RTrim(串)`：去掉串右边所有空格。
- `LTrim(串)`：去掉串左边所有空格。
- `Trim(串)`：去掉两边所有空格。
- `AS 别名`：起别名。
- `+|-|*|/`：算术运算符。

### 函数

`MySQL`提供函数来对数据进行处理，但是函数没有`SQL`可移植性强，使用函数时要写好代码注释。

- 文本串处理函数
  - `Length(字段)`：返回串的长度。
  - `Lower(字段)`：将串转换为小写。
  - `Upper(字段)`：将串转换为大写。
  - `Trim(字段)`：去除串两端的空格。
  - `LTrim(字段)`：去除串右边的空格。
  - `RTrim(字段)`：去除串左边的空格。
  - `Soundex(字段)`：根据读音寻找，`Soundex(name)=Soundex('li ming')`。
- 数值处理函数，
  - `Abs(字段)`：绝对值。
  - `Rand()`：随机数。
- 日期处理函数：日期可以直接跟字符串比较`Date(now())='2018-01-01'`，而且日期最好使用`yyyy-mm-dd`格式，防止误解。
  - `Date(字段)`：提取出日期部分。
  - `Time(字段)`：提出时间部分。
  - `AddDate(字段,INTERVAL 值 类型)`：增加一个日期，`AddDate(birthdate,INTERVAL 10 DAY)`。
  - `AddTIme(字段,INTERVAL 值 类型)`：增加一个时间。
  - `CurDate()`：返回当前日期。
  - `CurTime()`：返回当前时间。
- 系统函数
  - `datebase()`：返回当前数据库名。
  - `version()`：返回当前版本
  - `user()`：返回当前登录用户。
- 自定义函数

### 数据汇总

- 聚集函数：用于汇总数据。
  - `AVG(字段)`：求字段平均值，会忽略值为`NULL`的行。
  - `COUNT(字段|*|1)`：返回行数。
    - `COUNT(字段)`：统计行数，但是会忽略字段值为`NULL`的行。
    - `COUNT(*|1)`：统计检索出来结果的行数，包括列值为`NULL`的行。
  - `MAX(字段)`：返回字段最大值(值或日期)。对文本使用时，返回按该字段排序后的最后一行，会忽略字段为`NULL`的行。
  - `MIN(字段)`：返回字段最小值。对文本使用时，返回按该字段排序后的第一行，会忽略字段为`NULL`的行。
  - `SUM(字段)`：对字段值求和。
- 聚集函数还可以使用`DISTINCT`去修饰字段，只取字段的不同值，但是不能对`Count`使用。

### 数据分组

- 分组：`GROUP BY 字段`，按字段的值进行分组。
  - 可以包含多个字段或表达式(不能有聚集函数)，用于嵌套分组。
  - 嵌套分组时，只会在最后一层分组中进行汇总。
  - 只能依靠检索字段进行检索。
  - `NULL`值将被视作为一组。
- 过滤分组：`HAVING 条件`，同`WHERE(过滤行)`。
- 排序：显示跟上`ORDER BY`，因为`GROUP BY`的排序只依赖于出现的顺序。

### 子查询

子查询是将一个`SELECT`语句视作为整体。`SELECT * FROM user WHERE user.class_id IN (SELECT class_id FROM class)`，其实际执行了两条`SELECT`语句，先内层`SELECT class_id FROM class`，然后在外层。子查询的效率不及联结表。

### 联结表

- 主键：用于唯一区分一条记录。
- 外键：为另一个表的主键，用于建立两个表之间的关系。
- 当数据被拆分到了多个表中，想要检索出数据来，可以使用子查询，也可以使用联结。
- 等值联结：`SELECT * FROM products,vendors WHERE products.vend_id = vendors.vend_id ORDER BY vend_name,prod_name;`
  - 笛卡尔积(cross join)：``SELECT * FROM products,vendors ORDER BY vend_name,prod_name;` 
  - 通过`WHERE products.vend_id = vendors.vend_id`进行过滤数据。
- 内部联结：`SELECT * FROM products INNER JOIN products ON products.vend_id = vendors.vend_id`
- 联结时不要联结过多的表，这样性能会比较糟糕。
- 自联接：自己和自己联结，通过表别名来区分：`SELECT p1.prod_id,p1.prod_name FROM product AS p1,product AS p2 WHERE p1.vend_id=p2.vend_id AND p2.prod_id='DTNTR'`
- 自然联结：进行联结时，会出现重复的列，自然联结就避免的列重复出现。对一个表使用通配符`SELECT 表.*`，对其他表使用明确表达。
- 外部联结：联结只显示有关联的行，外部联结会显示无关联行，`LEFT JOIN ON`，无关联部分为`NULL`。
  - `LEFT`：左联结，以左边的表作为基准。
  - `RIGHT`

### 组合查询

- 组合查询：将多个`SELECT`语句的结果进行结合。
- 创建组合查询：`查询语句1 UNION 查询语句2`。
- `UNION`要求每个查询必须包含相同的字段、表达式、聚酯函数，且列的数据必须兼容。
- `UNION`默认过滤重复行，可以采用`UNION ALL`。
- 排序：最后使用`ORDER BY`即可，是对组合后的数据进行排序。

### 全文本搜索

- 不是所有的所有的存储引擎都支持，`MyISAM`支持，但`InnoDB`不支持。
- `LIKE`和`REGEX`的缺点：
  - 性能差：会匹配所有的行。
  - 不能明确控制什么不匹配，什么匹配。
- 被搜索的列必须被索引。创建表时，添加`FULLTEXT(字段)`，更新索引需要消耗时间(插入删除数据都要更新索引)，因此最佳方式是先导入数据，然后在打开`FULLTEXT`。
- 全文本搜索
  - `WHERE Match(字段和FULLTEXT相同) Against(搜索表达式)`，不区分大小写
- 查询扩展：` Against(搜索表达式 WITH QUERY EXPANSION)`能查询到和没有查询扩展的结果相关的行。
- 布尔文本查询：` Against(搜索表达式 IN BOOLEAN MODE)`，对于非`FULLTEXT`也可以使用，只是效率低。
  - `-`：必须不包含。
  - `+`：必须包含，`+a -b`，包含a但是不包含b。
  - `>`：包含且增加等级(输出的次序)。
  - `<`：包含且降低等级。
  - `()`：定义子表达式。
  - `*`：词尾通配符。
  - `""`：定义短语。
  - `~`：取消排序值。
  - `a b`：包含a或b。
- 若一个词出现在`50%`的行中，视作为非用词，在布尔文本查询不适用。

### 插入数据

- 插入一行：`INSERT INTO 表名 VALUES(值);`。如果字段没有值，可以设置为`NULL`。该插入方法不安全，因为严重依赖于字段顺序。
- 安全插入：`INSERT INTO 表名（字段） VALUES(值);`。
- 插入数据时，因为需要很多操作(如更新索引)，因此耗时较多，可能会降低`SELECT`性能，应为默认写入操作优先于读取操作。如果数据检索最重要，则可以使用`INSERT LOW_PRIORITY INTO`降低优先级。
- 插入多行：`INSERT INTO 表名(字段名) VALUES(值1),(值2);`。比写多条语句快。
- 插入检索数据：`INSERT INTO 表名(字段名) SELECT 字段名 FROM 表名`。将`SELECT`语句查询到的数据插入表中。

### 修改数据

- 更新行数据：`UPDATE 表 SET 字段=值 WHERE 条件;`

### 删除数据

- 删除特定行：`DELETE FROM 表名 WHERE 条件;`
- 删除所有行：
  - `DELETE FROM 表名;`
  - `TRUNCATE TABLE 表名;`：新建一个空表，因此速度更快。

## 视图

## 存储过程

## 游标

## 触发器

## 事务

## 数据库维护

## 性能

