# WSGI学习

## WSGI是什么？

WSGI(Web Server Gateway Interface)是一种Python Web框架和Web服务器通信的接口。WSGI将Web服务器和Web框架分离，因此一套Web服务器可以使用任意遵守WSGI协议的Web应用。

WSGI接口中，分为两部分：

- Server/Gateway：负责从客户端接受请求，并将请求转发给相应的application，然后将application返回的response返回给客户端。

- Application/Framework：接收Server转发的请求，处理后，将结果返回给Server。application是一个可调用对象，必须能接收两个参数`environ`，`start_response`，其返回一个可迭代的对象，用于表示response的body。`environ`是一个字典，包含请求的相关信息。`start_response`也是一个可调用对象，必须接收两个参数`status`(状态码)和`response_headers`(响应的头部信息)。

  ```python
  def simple_app(environ, start_response):
      """Simplest possible application object"""
      status = '200 OK'
      response_headers = [('Content-type', 'text/plain')]
      start_response(status, response_headers)
      return [HELLO_WORLD]
  ```

在WSGI框架下，一个HTTP请求的流程如下：

![WSGI HTTP流程图]()

采用Nginx作为中间者有两大好处：

- 提供负载均衡能力：Nginx根据负载均衡算法，将请求交由相应的wsgi服务器处理。
- 提高性能：Nginx能更好的处理静态资源请求。

## werkzeug是什么？

werkzeug 提供了 python web WSGI 开发相关的功能：

- 路由处理：如何根据请求 URL 找到对应的视图函数
- request 和 response 封装：提供更好的方式处理request和生成response对象
- 自带的 WSGI server： 测试环境运行WSGI应用

```python
from werkzeug.wrappers import Request, Response


class Shortly(object):
    """
    Shortly 是一个实际的 WSGI 应用，通过 __call__ 方法直接调 用 wsgi_app，
    """

    def __init__(self):
        pass

    def dispatch_request(self, request):
        return Response('Hello World!')

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


if __name__ == '__main__':
    from werkzeug.serving import run_simple

    app = Shortly()
    run_simple('127.0.0.1', 5000, app)
```

总结：

`application`提供一个可调用对象`Shortly`，然后通过传参的形式告知WSGI Server，当由对应的请求时，Server将请求转发给application进行处理。

run_simple-->inner(内部函数)-->make_server(创建服务器)-->创建`BaseWSGIServer`对象(该对象中有一个WSGIRequestHandler处理器，一个http服务器)-->调用`server.serve_forever()`-->`HTTPServer.serve_forever`启动服务器(HTTPServer是一个socketserver.TCPServer的子类。)。

```python
class BaseWSGIServer(HTTPServer, object):

    """Simple single-threaded, single-process WSGI server."""

    multithread = False
    multiprocess = False
    request_queue_size = LISTEN_QUEUE

    def __init__(self,host,port,app,handler=None,passthrough_errors=False,...):
        if handler is None:
            handler = WSGIRequestHandler
		# 确定监听地址类型
        # socket.AF_UNIX socket.AF_INET6 socket.AF_INET
        self.address_family = select_address_family(host, port)

		# 获取服务器地址
        server_address = get_sockaddr(host, int(port), self.address_family)

        # 启动http服务
        HTTPServer.__init__(self, server_address, handler)

        self.app = app
        self.passthrough_errors = passthrough_errors
        self.shutdown_signal = False
        self.host = host
        self.port = self.socket.getsockname()[1]

    def serve_forever(self):
        self.shutdown_signal = False
        try:
            HTTPServer.serve_forever(self)
        except KeyboardInterrupt:
            pass
        finally:
            self.server_close()

    def handle_error(self, request, client_address):
        if self.passthrough_errors:
            raise
        # Python 2 still causes a socket.error after the earlier
        # handling, so silence it here.
        if isinstance(sys.exc_info()[1], _ConnectionError):
            return
        return HTTPServer.handle_error(self, request, client_address)

    def get_request(self):
        con, info = self.socket.accept()
        return con, info
```

## HTTP请求如何到达应用程序？

![结构]()



## 如何自行开发一个web服务？

## 参考

- PEP 3333：https://www.python.org/dev/peps/pep-3333

- 标准wsgi实现：wsgiref
