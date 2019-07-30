# 图解HTTP

## 访问流程

通过浏览器访问一个网页的过程中，会存在两个角色：客户端与服务器端。客户端与服务器端交互数据时采用HTTP协议传输。整个访问流程是：客户端向服务器端发生指令(请求)，服务器端返回指令结果(响应)。

![访问流程]()

- URI和URL的区别

  URL是URI的一部分，URL(Uniform Resource Location)强调的是定位，必须告知该资源的位置，URI(Uniform Resource Identify)强调的是区分，只要能区分该资源即可，如同身份证号，通过身份证号可以唯一区分一个人，但是却不知道去哪里找，但URL是带地址的，因此可以通过URL直接定位到该资源。

## 请求

### 报文结构

![请求报文结构]()

### 请求行

请求行包含三部分：请求方法、请求URI和HTTP版本。

![请求行]()

### 请求方法

请求中的请求方法用于表明客户端的意图。常用的请求方法有：

- GET：获取URI标识的资源。
- HEAD：只获取报文的首部。
- POST：通过主体向服务器传输数据。
- PUT：传输文件，将文件保存在URI指定的位置。
- DELETE：删除URI标识的资源。

## 响应

### 报文结构

![响应报文结构]()

### 状态行

状态行包含三部分：响应状态码、状态码解释和HTTP版本。

![状态行]()

### 常用状态码

HTTP状态码负责表达服务器对请求的处理状态。状态码被分为五类：1XX、2XX、3XX、4XX、5XX。

- 1XX：信息性状态码（请求正在被处理，通常只在服务器内部使用）
- 2XX：成功状态码（请求正常处理）
  - 200：OK，请求被正常处理。
  - 204：No Content，请求正常处理，但响应报文主体为空。
  - 206：Partial Content，响应了客户端范围请求。
- 3XX：重定向状态码（需要客户端额外操作才能完成处理）
  - 301：Moved Permanently，永久重定向，资源已经分配新URI，客户端请求新的URI。
  - 302：Found，临时重定向。
  - 303：See Other，请用GET方法访问资源新URI。
  - 304：Not Modified，资源未改变，可使用缓存。
- 4XX：客户端错误状态码（请求有错误，服务器无法处理）
  - 400：Bad Request，请求报文语法错误。
  - 401：Unauthorized，请进行信息认证（搭配WWW-Authenticate）。
  - 403：Forbidden，禁止访问该资源。
  - 404：Not Found，访问资源不存在。
- 5XX：服务器错误状态码（服务器处理异常）
  - 500：Interval Server Error，服务器内部错误。
  - 503：Server Unavailable，服务不可用（超负载或停机维护)。

## 首部字段

HTTP的首部字段用于在客户端和服务器端传递额外信息，如：报文主体大小、认证信息等。HTTP的首部字段由`字段名:字段值`组成，如`Content-Type:text/html`。首部字段根据实际用途被划分为：

- 通用首部字段：请求和响应都需要使用的首部。
- 请求报文首部字段：描述客户端发送的请求信息。
- 响应报文首部字段：描述服务器端发送的响应信息。
- 实体首部字段：用于描述报文实体的信息。

### 通用首部

- `Cache-Control`：控制缓存机制，多个指令通过`;`隔开。
  - 请求常用缓存指令
    - `max-age=[秒]`：必需，如果缓存的时间未超过最大值，则返回该缓存。
    - `min-fresh=[秒]`：必需，期待返回指定时间内有效的资源
    - `no-cache`：不使用缓存，请从源服务器发送资源。
    - `no-store`：不缓存任何内容。
    - `only-if-cached`：从缓存处获取资源。
    - `max-stale=[秒]`：可以接受指定时间内过期的的资源。
  - 响应常用缓存指令
    - `max-age=[秒]`：缓存的最长时间，在此时间内不必向服务器确认有效性。
    - `s-maxage=[秒]`：必需，公共缓存服务器响应的最大时间。
    - `public|private`：该缓存的所有者。
    - `no-cache`：该资源不能被缓存。
    - `no-store`：不要缓存资源。
    - `no-transform`：缓存服务器不能修改实体的媒体类型，防止缓存或代理压缩图片等操作。
  - 难点
    - `no-cache`和`no-store`
- `Connection`：`Connection`有两个功能
  - 控制代理不再转发首部字段：`Connection:不再转发的字段`。
  - 管理持久连接
    - 断开：`Connection:close`
    - 维持持续连接：`Connection:Keep-Alive`。HTTP初始版本中，每一次HTTP通信都需要断开一个TCP连接，维持持续连接可以节约频繁建立和断开TCP的开销。而且持续连接能实现管道化(不再是发生请求、等待响应后再发下一个，可以一次性发多个请求或接受响应，加快通信速度。)
- `Date`：创建HTTP报文的时间与日期，格式为RFC1123，如`Date:Sun, 06 Nov 1994 08:49:37 GMT`
- `Transfer-Encoding`：报文主体传输时采用的编码方式。

### 请求首部

- `Accept`：描述客户端能处理的媒体类型及相对优先级。
  - 类型，多个类型用逗号隔开。
    - 文本：`text/htm`、`text/css`
    - 图片：`image/jpeg`、`image/gif`
    - 视频：`video/mpeg`
    - 二进制文件：`application/zip`
  - 权重：`video/mpeg;q=0.2`，权重值为0.2，默认为1.
- `Accept-Charset`：指定客户端支持的字符集与相对优先级。如`Accept-Charset=utf-8,unicode-1;q=0.2`
- `Accept-Encoding`：客户端支持的编码格式及相对优先级。
  - 编码格式：`gzip`、`compress`、`deflate`、`identity(不压缩)`、`*(任意编码格式)`。
  - 相对优先级：`gzip;q=0.2`。
- `Accept-Language`：客户端支持的自然语言集与相对优先级。
  - 语言集：`zh-cn`、`zh`、`en`、`en-us`
  - 相对优先级：`zh-cn,zh;q=0.2`。
- `Authorization`：用户认证信息。
- `Except`：期待服务器的行为，格式为`状态码-状态注释`，如`100-continue`。
- `From`：
- `Host`：

### 响应首部

- `Accept-Ranges`：告知客户端自己是否能处理范围请求，`Accept-Ranges:none`为不能处理范围请求，`Accept-Ranges:bytes`为能处理范围请求。

### 实体首部

- `Allow`：用于通知客户端URI指向的资源所支持的方法，如`Allow:GET,POST`。
- `Content-Encoding`：实体的编码方式，如`Content-Encoding:gzip`，支持`gzip`、`compress`、`deflate`、`identity(不压缩)`。
- `Content-Language`：实体采用的自然语言，如`Content-Language:zh-CN`。
- `Content-Length`：实体的大小，单位为字节。
- `Content-Location`：报文实体部分对应的URI。
- `Content-Range`：响应请求资源的某个范围，如`Content-Range:5001-10000/10000`，传输第5001字节到第10000字节部分数据，整个实体大小为10000字节。
- `Content-Type`：实体的媒体类型，如`Content-Type:text/html;charset=UTF-8`。
- `Expire`：资源的过期时间，时间格式为RFC1123。
- `Last-Modified`：资源最近一次修改时间，时间格式为RFC1123。
