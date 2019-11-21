# WSGI
## WSGI

`WSGI(Python Web Server Gateway Interface)`是一种用于Web服务器和Web应用程序之间进行交互的接口。`WSGI`的主要目的是将请求和响应的处理从应用程序中剥离，交由`Web`服务器处理，应用程序只需关注自身的业务逻辑。因此，通过`WSGI`接口能提高不同服务器和应用程序之间的可移植性。该标准的官方说明可以查看[PEP333](http://www.python.org/dev/peps/pep-0333)。

![WSGI架构]()

WSGI规范要求：

- 服务器和应用程序必须符合`WSGI`规范。
- 应用程序是可调用对象，必须能接收两个参数`environ`，`start_response`，`environ`是一个环境字典，包含请求的相关信息。`start_response`也是一个可调用对象，必须接收两个参数`status`(状态码)和`response_headers`(响应的头部字段)，用于生成响应的头部。应用程序会返回一个可迭代对象，用于生成响应的`body`。

## wsgiref

标准库`wsgiref`提供了一个`WSGI`标准的参考。该库包含五个模块：

- `simple_server`：提供了一个简单的WSGI服务器。
- `headers`：负责处理响应头部。
- `handlers`：处理请求器。
- `validate`：提供验证是否符合WSGI的方法。
- `util`：工具包。

官方文档中，提供了一个简单例子：

```python
from wsgiref.simple_server import make_server

def hello_world_app(environ, start_response):
    status = '200 OK'  # HTTP Status
    headers = [('Content-type', 'text/plain; charset=utf-8')]  # HTTP Headers
    # 返回响应头部
    start_response(status, headers)
    # 返回响应body
    return [b"Hello World"]

with make_server('', 8000, hello_world_app) as httpd:
    print("Serving on port 8000...")
    # 启动服务
    httpd.serve_forever()
```

这里简单分析下整体的运行流程：

![]()

## 参考

- PEP 3333：https://www.python.org/dev/peps/pep-3333

- 标准wsgi实现：wsgiref
