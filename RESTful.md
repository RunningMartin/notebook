# RESTful

## RESTful是什么？

RESTful是一种架构方式的约束，简单的说：

- 每个URI都代表一种资源。
- 客户端通过HTTP协议的四大请求方法(GET、POST、PUT、DELETE)表达对服务器上资源的操作。

## RESTful的6大原则？

- `C-S架构`：数据存储在Server上，Client通过接口使用数据。
- `无状态`：Client每次请求都需要携带识别信息，Server通过该信息识别用户后，返回正确的响应。无状态的特征使Server不需要保存Client状态，提高了Server的健壮性和可扩展性。
- `可缓存`：响应可以被缓存，通过合理的缓存管理，可以进一步改善性能和延展性。
- `系统分层`：组件只能看到与其交互的相邻层，架构上被分解为若干等级的层。
- `按需扩展`：Server可以传输代码给Client，用于扩展Client的功能。
- `接口统一`：统一的API和返回的数据格式(XML或JSON)，提高可读性。

## RESTful的7个最佳实践？

- 版本号，如`https://example.com/api/v1/`。

- URI应该为名词复数，用HTTP请求方法表达动作。

- 合理使用查询参数，针对多级分类资源，URI只表示第一级目录，其他级别采用查询字符串表示，如`/articles?published=true`优于`/articles/published`。

- 参数命名规范(推荐下划线命名)，如`/users？today_login=true`。

- Server的响应状态码必须明确。

- API应该返回JSON对象，并统一格式。

  ```json
  {
      "code":200,//响应状态码
      "status":"success",
      "message":"success",//用于显示错误信息
      "data":{//具体的数据
          "username":"test",
          "password":"12345678"
      }
  }
  ```

- 通过URL来提供发现其他URL(HATEOAS)，如`https://api.github.com`.

- 多表多参数查询：通过路由属性来实现，如`/api/orders/{address}/{month}`，查询指定月份、指定地址的订单。
