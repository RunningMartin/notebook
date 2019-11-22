# Flask学习

## 前言

`werkzeug`是一个`WSGI Web`应用程序库，通过`werkzeug`可以很快速的编写出Web框架或应用。下面是一个简单的例子

```python
from werkzeug.wrappers import Request, Response

def application(environ, start_response):
    request = Request(environ)
    response = Response("Hello %s!" % request.args.get('name', 'World!'))
    return response(environ, start_response)

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application)
```

`werkzeug`提供了一个简单的`WSGI`服务器，通过`run_simple`即可启用。当请求到达时，`werkzeug`将`WSGI`服务器提供的`environ`封装为一个`Request`实例，处理完逻辑后，生成一个`response`对象，然后调用`response(environ, start_response)`，将相应返回给WSGI服务器。

## 实例化应用

`Flask`中，使用`app = Flask(__name__)`即可实例化一个Flask应用。实例化应用是需要注意以下几点：

- 针对请求和响应的处理，`Flask`使用`werkzeug`的`Request`类和`Response`类。

- 针对`URL`的处理，`Flask`使用`werkzeug`的`Rule`类和`Map`类。一个`URL`对应一个`Rule`实例，`Map`实例负责将多个`Rule`实例组建为一个地图，用于匹配请求。

- 添加路由推荐使用`route`函数。

  ```python
  # 会自动生成一个Rule实例，然后添加到Map中
  @app.route('/')
  def index():
      return 'hello'
  ```

- 实例化时，会创建一个`Jinja`环境。

- 实例化后的Flask应用可通过`__call__(environ, start_response)`调用。

  ```python
  def __call__(self, environ, start_response):
      """Shortcut for :attr:`wsgi_app`"""
      return self.wsgi_app(environ, start_response)
  ```

  `__call__`会调用`wsgi_app(environ, start_response)`方法，这样做的原因是，可以通过中间件改变`Flask`应用的特性。

  ```python
  import os
  from flask import Flask
  from werkzeug.middleware.dispatcher import DispatcherMiddleware
  from werkzeug.middleware.shared_data import SharedDataMiddleware
  
  app1 = Flask(__name__)
  app = Flask(__name__)
  
  @app1.route('/')
  def index():
      return "This is app1!"
  
  @app.route('/')
  def index():
      return "This is app!"
  
  # DispatcherMiddleware可以将多个应用合并为一个应用
  app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
      '/app1': app1,
  })
  # SharedDataMiddleware 可以添加一个静态资源共享url
  app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/shared': os.path.join(os.path.dirname(__file__), 'shared')
  })
  
  if __name__ == '__main__':
      app.run()
  ```

## 请求处理流程

```python
def full_dispatch_request(self):
    self.try_trigger_before_first_request_functions()
    try:
        request_started.send(self)
        # 对请求进行预处理，如建立数据库连接
        rv = self.preprocess_request()
        if rv is None:
            # 根据url，将请求交给相应的视图函数处理
            rv = self.dispatch_request()
    except Exception as e:
        rv = self.handle_user_exception(e)
    # finalize_request将视图函数的返回值转换为response对象
    return self.finalize_request(rv)

def wsgi_app(self, environ, start_response):
    # 获取请求上下文RequestContext
    # app：当前flask应用
    # url_adapter：Map实例创建的MapAdapter实例，用于将匹配请求中的URL和Map实例中的URL规则进行匹配
    # request：请求的相关信息
    # session：会话相关信息
    # g：全局变量，基于应用上下文栈_app_ctx_stack
    # _request_ctx_stack：请求上下文栈，werkzeug的LocalStack
    ctx = self.request_context(environ)
    error = None
    try:
        try:
            # 将请求上下文入栈
            ctx.push()
            # 正在处理请求
            response = self.full_dispatch_request()
        except Exception as e:
            error = e
            response = self.handle_exception(e)
        except:  # noqa: B001
            error = sys.exc_info()[1]
            raise
        # 将响应返回给wsgi服务器
        return response(environ, start_response)
    finally:
        if self.should_ignore_error(error):
            error = None
        # 清理请求上下文
        ctx.auto_pop(error)

def __call__(self, environ, start_response):
    return self.wsgi_app(environ, start_response)
```

## URL处理

`Flask`应用实例化时，会添加`url_map`属性。该属性是一个`werkzeug.routing.Map`实例，其主要功能是为应用添加`URL`与视图函数的映射关系。`Flask`中提供了两种方式添加`URL`：

- `add_url_rule`方法(我只保留了主要代码)。

```python
def add_url_rule(self,
rule,
endpoint=None,
view_func=None,
provide_automatic_options=None,
**options
):
if endpoint is None:
endpoint = _endpoint_from_view_func(view_func)
options["endpoint"] = endpoint
methods = options.pop("methods", None)

if methods is None:
methods = getattr(view_func, "methods", None) or ("GET",)

methods = set(item.upper() for item in methods)
# 生成url规则
rule = self.url_rule_class(rule, methods=methods, **options)
# 添加rule对象到map中
self.url_map.add(rule)
# 添加视图函数，视图函数和url通过endpoint进行关联
if view_func is not None:
self.view_functions[endpoint] = view_func
```

- `route`装饰器，推荐使用装饰器。

```python
def route(self, rule, **options):
	def decorator(f):
		endpoint = options.pop("endpoint", None)
		self.add_url_rule(rule, endpoint, f, **options)
		return f
  
	return decorator
```

现在通过一个简单的例子，看看`Flask`如何处理添加`URL`路由操作：

```python
In [1]: from flask import Flask
In [2]: app=Flask(__name__)
In [3]: @app.route('/')
   ...: def index():
   ...:     return "hello world"
   ...:
# 查看url_map中存储的url规则
In [4]: app.url_map
Out[4]:
Map([<Rule '/' (OPTIONS, HEAD, GET) -> index>,
 <Rule '/static/<filename>' (OPTIONS, HEAD, GET) -> static>])
In [5]: rule
Out[5]: <Rule '/static/<filename>' (OPTIONS, HEAD, GET) -> static>
# 可以通过_regex查看rule的正则表达式
In [6]: rule._regex
Out[6]: re.compile(r'^\|/static/(?P<filename>[^/].*?)$', re.UNICODE)
# 查看url_map中end_point与rule的映射关系，默认将视图函数名作为end_point
In [6]: app.url_map._rules_by_endpoint
Out[6]:
{'static': [<Rule '/static/<filename>' (OPTIONS, HEAD, GET) -> static>],
 'index': [<Rule '/' (OPTIONS, HEAD, GET) -> index>]}
# 查看end_point和视图函数之间的映射关系
In [7]: app.view_functions
Out[7]:
{'static': <bound method _PackageBoundObject.send_static_file of <Flask '__main__'>>,
 'index': <function __main__.index()>}
```

我们再来看看`Flask`具体是如何处理请求的。

```python
def dispatch_request(self):
    req = _request_ctx_stack.top.request
    if req.routing_exception is not None:
        self.raise_routing_exception(req)
	# 获取请求的Rule实例，rule.endpoint存储视图函数名 rule.map中存储了所有的rule和视图映射关系
    rule = req.url_rule
    if (
        getattr(rule, "provide_automatic_options", False)
        and req.method == "OPTIONS"
    ):
        return self.make_default_options_response()
    # 调用视图函数，处理请求
    return self.view_functions[rule.endpoint](**req.view_args)
```

综上所述，我们可以整理出`Flask`框架处理`URL`的整体逻辑流程。

![Flask URL处理]()

## 蓝图

对于大型应用而言，随着功能的增加，应用规模也会扩大，为了降低代码复杂度，提高可维护性，需要将应用按一定的规则拆分为不同模块。`Flask`提供了蓝图的概念，来实现应用的拆分。

> Flask uses a concept of blueprints for making application components and supporting common patterns within an application or across applications. Blueprints can greatly simplify how large applications work and provide a central means for Flask extensions to register operations on applications. A Blueprint object works similarly to a Flask application object, but it is not actually an application. Rather it is a blueprint of how to construct or extend an application.

根据官方文档的描述，蓝图功能和应用类似，只是它必须注册到应用中。通过使用蓝图，我们可以实现将应用的逻辑功能拆分到不同的蓝图中。我们先来看下蓝图是如何使用的。

```python
In [1]: from flask import Blueprint
# 创建蓝图，前两个参数必须
In [2]: blog = Blueprint('blog', __name__,static_folder='static',template_folder='templates')
# 注册路由规则
In [3]: @blog.route('/')
   ...: def index():
   ...:     return "This is blog home page."
   ...:
# 定义请求处理前的操作，如建立数据库连接
In [4]: @blog.before_request
   ...: def before_request():
   ...:     return "This is before_request function."
   ...:
# 定义请求处理完成后的操作，如关闭数据库连接
In [5]: @blog.after_request
   ...: def after_request():
   ...:     return "This is after_request function."
   ...:
# deferred_functions和应用的view_functions相同，存放蓝图装饰的视图函数
In [6]: blog.deferred_functions
Out[6]:
[<function flask.blueprints.Blueprint.add_url_rule.<locals>.<lambda>(s)>,
 <function flask.blueprints.Blueprint.before_request.<locals>.<lambda>(s)>,
 <function flask.blueprints.Blueprint.after_request.<locals>.<lambda>(s)>]

In [7]: from flask import Flask
In [8]: app = Flask(__name__)
In [9]: app.url_map
Out[9]: Map([<Rule '/static/<filename>' (HEAD, GET, OPTIONS) -> static>])
# 应用中的蓝图
In [10]: app.blueprints
Out[10]: {}
# 请求执行前做的操作
In [11]: app.before_request_funcs
Out[11]: {}
# 请求处理完后执行的操作
In [12]: app.after_request_funcs
Out[12]: {}
# 将蓝图注册到应用中
In [13]: app.register_blueprint(blog, url_prefix='/blog')
# 检查应用的相关信息，可以看到，注册时，将蓝图中的很多属性都存入了应用中
In [14]: app.url_map
Out[14]:
Map([<Rule '/blog/' (HEAD, GET, OPTIONS) -> blog.index>,
 <Rule '/blog/static/<filename>' (HEAD, GET, OPTIONS) -> blog.static>,
 <Rule '/static/<filename>' (HEAD, GET, OPTIONS) -> static>])
In [15]: app.blueprints
Out[15]: {'blog': <flask.blueprints.Blueprint at 0x8f7a7b8>}
In [16]: app.before_request_funcs
Out[16]: {'blog': [<function __main__.before_request()>]}
In [17]: app.after_request_funcs
Out[17]: {'blog': [<function __main__.after_request()>]}
```

通过查看`Blueprint`关于`before_request`的源码。

```python
# buleprints.BulePrint
def record(self, func):
    self.deferred_functions.append(func)

def record_once(self, func):
    def wrapper(state):
        if state.first_registration:
            func(state)

	return self.record(update_wrapper(wrapper, func))

def before_request(self, f):
    self.record_once(lambda s: s.app.before_request_funcs
        .setdefault(self.name, []).append(f))
    return f
```

我们可以发现，使用蓝图的装饰器时，会在`deferred_functions`中添加一个匿名函数。然后我们再看看蓝图注册到应用时，会执行哪些操作。

```python
# app.Flask
def register_blueprint(self, blueprint, **options):
    # 调用蓝图的注册方法
    blueprint.register(self, options, first_registration)

# buleprints.Buleprint.register
def register(self, app, options, first_registration=False):
    self._got_registered_once = True
    # 创建BlueprintSetupState对象，将应用和蓝图进行关联
    state = self.make_setup_state(app, options, first_registration)
	# 添加url
    if self.has_static_folder:
        state.add_url_rule(
            self.static_url_path + "/<path:filename>",
            view_func=self.send_static_file,
            endpoint="static",
        )
    # 执行deferred_functions中所有匿名函数
    # 将蓝图中的操作映射到应用中。
	for deferred in self.deferred_functions:
        deferred(state)
```

综上所述，我们可以将蓝图视作为一个小应用，通过调用`register_blueprint`，可以将蓝图上的相关操作注册到`Flask`应用中，从而实现模块化拆分。

## LoaclStack

`Flask`中采用`werkzeug.local`模块提供的数据结构`LocalStack`存储上下文。`LocalStack`是一个字典结构，采用线程/协程标识符作为键。

```python
In [1]: from werkzeug.local import LocalStack
In [2]: local_stack=LocalStack()
# 查看栈中存储的元素
In [3]: local_stack._local.__storage__
Out[3]: {}
In [4]: def worker(i):
    ...:     local_stack.push(i)
    ...:
In [4]: import threading
In [5]: for i in range(3):
    ...:     t = threading.Thread(target=worker, args=(i,))
    ...:     t.start()
    ...:
In [6]:  local_stack._local.__storage__
Out[6]: {3544: {'stack': [0]}, 16556: {'stack': [1]}, 16984: {'stack': [2]}}
```

`LocalStack`将根据线程/协程标识符，存取相应的数据。`LocalStack`的`top`方法永远指向当前线程/协程最后推入栈中的元素。

```python
In [1]: from werkzeug.local import LocalStack
In [2]: import sys
In [3]: from time import sleep
In [4]: import threading  
In [5]: local_stack=LocalStack()
In [6]: def worker(i):
   ...:     ident=threading.currentThread().ident
   ...:     info="{} {}:{} \n".format(ident,'push',i)
   ...:     sys.stdout.write(info)
   ...:     local_stack.push(i)
   ...:     sleep(5)
   ...:     info="{} {}:{}\n".format(ident,'pop',local_stack.pop())
   ...:     sys.stdout.write(info)
   ...:

In [7]: for i in range(3):
   ...:     t = threading.Thread(target=worker, args=(i,))
   ...:     t.start()
   ...:
Out[7]: 
14504 push:0
16596 push:1
15652 push:2

15652 pop:2
14504 pop:0
16596 pop:1
```

## 请求上下文

`Flask`中所有的请求处理都在请求上下文中进行。请求上下文中包含了很多余请求相关的信息：

- app：当前flask应用。
- url_adapter：Map实例创建的MapAdapter实例，用于将匹配请求中的URL和Map实例中的URL规则进行匹配。
- request：请求的相关信息。
- session：会话相关信息。
- g：全局变量，基于应用上下文栈_app_ctx_stack。
- _request_ctx_stack：全局请求上下文栈。

`Flask`收到一个请求后每，会先生成请求上下文，然后保存到全局请求上下文栈中`_request_ctx_stack`(`LocalStack`的实例)，再调用视图函数处理请求，然后请求处理后，将请求上下文从`_request_ctx_stack`中移除。

```python
# app.Flask.wsgi_app
def wsgi_app(self, environ, start_response):
    # 获取请求上下文RequestContext
    ctx = self.request_context(environ)
    error = None
    try:
        try:
            # 将请求上下文入栈
            ctx.push()
            # 正在处理请求
            response = self.full_dispatch_request()
        except Exception as e:
            error = e
            response = self.handle_exception(e)
        except:  # noqa: B001
            error = sys.exc_info()[1]
            raise
        # 将响应返回给wsgi服务器
        return response(environ, start_response)
    finally:
        if self.should_ignore_error(error):
            error = None
        # 清理请求上下文
        ctx.auto_pop(error)
# ctx.RequestContext.push
```

我们先看看上下文`push`的源码（进行了无关内容删减，用文字代替描述）：

```python
def push(self):
    top = _request_ctx_stack.top
    if top is not None and top.preserved:
        top.pop(top._preserved_exc)

	# 检查应用上下文
    # 如果应用上下文不存在或栈顶的应用上下文对象不是当前应用
    # 则会自动生成应用上下文对象
    ....
	# 将请求上下文入栈
    _request_ctx_stack.push(self)

	#生成会话信息
	....
    # 进行url匹配
    if self.url_adapter is not None:
        self.match_request()
```

然后再看看`pop`的源码：

```python
def pop(self, exc=_sentinel):
    # 进行一些应用上下文的处理
    ....
    # 请求上下文销毁
	rv = _request_ctx_stack.pop()
	
    # 哦按点是否需要销毁应用上下文
    if clear_request:
        rv.request.environ["werkzeug.request"] = None

    if app_ctx is not None:
        app_ctx.pop(exc)
```

综上，我们可以总结出：请求到达时，会先生成请求上下文(按需生成应用上下文)，再将请求上下文会存储在一个全局栈中，然后再使用视图函数处理请求；处理完毕后，销毁请求上下文(按需销毁应用上下文)。

我们来看一个简单例子：

```python
In [1]: from flask import Flask, _request_ctx_stack, _app_ctx_stack
In [2]: app = Flask(__name__)
# 查找全局请求上下文栈和应用上下文栈
In [3]: _request_ctx_stack._local.__storage__
Out[3]: {}
In [4]:  _app_ctx_stack._local.__storage__
Out[4]: {}
# 生成一个请求上下文
In [5]: request_context = app.test_request_context()
# 请求上下文入栈，可以看到生成了一个应用上下文
In [6]: request_context.push()
In [7]: _request_ctx_stack._local.__storage__
Out[7]: {16020: {'stack': [<RequestContext 'http://localhost/' [GET] of __main__>]}}
In [8]: _app_ctx_stack._local.__storage__
Out[8]: {16020: {'stack': [<flask.ctx.AppContext at 0x8e5c128>]}}
# 销毁请求上下文，可以看到应用上下文也销毁了
In [9]: request_context.pop()
In [10]: _request_ctx_stack._local.__storage__
Out[10]: {}
In [11]: _app_ctx_stack._local.__storage__
Out[11]: {}
```

## 应用上下文

应用上下文和请求上下文类似，只是应用上下文是用于确定请求所在的应用。它主要为了解决在多应用场景下，如果一个应用嵌套另一个应用的相关操作时，无法通过请求上下文的`app`属性或`current_app`找到另一个应用。

```python
In [1]:  from flask import Flask, _request_ctx_stack, _app_ctx_stack,current_app
In [2]: app1=Flask('app1')
In [3]: app2=Flask('app2')
# 构造app1的上下文中，处理app2的操作
In [4]: with app1.test_request_context():
   ...:     print("Enter app's Request Context:")
   ...:     print(_request_ctx_stack._local.__storage__)
   ...:     print(_app_ctx_stack._local.__storage__)
   ...:     print("current_app",current_app)
   ...:     with app2.app_context():
   ...:         print("Enter app2's App Context:")
   ...:         print("current_app",current_app)
   ...:         print(_request_ctx_stack._local.__storage__)
   ...:         print(_app_ctx_stack._local.__storage__)
   ...:     print("Exit app2's App Context:")
   ...:     print(_request_ctx_stack._local.__storage__)
   ...:     print(_app_ctx_stack._local.__storage__)
   ...:
Enter app's Request Context:
{7920: {'stack': [<RequestContext 'http://localhost/' [GET] of app1>]}}
{7920: {'stack': [<flask.ctx.AppContext object at 0x000000000A61F940>]}}
current_app <Flask 'app1'>
Enter app2's App Context:
current_app <Flask 'app2'>
{7920: {'stack': [<RequestContext 'http://localhost/' [GET] of app1>]}}
{7920: {'stack': [<flask.ctx.AppContext object at 0x000000000A61F940>, <flask.ctx.AppContext object at 0x000000000A5CB710>]}}
Exit app2's App Context:
{7920: {'stack': [<RequestContext 'http://localhost/' [GET] of app1>]}}
{7920: {'stack': [<flask.ctx.AppContext object at 0x000000000A61F940>]}}
```

## 上下文相关的全局变量

`Flask`中有很多与上下文相关的全局变量：

```python
# globals.py
def _lookup_req_object(name):
    top = _request_ctx_stack.top
    if top is None:
        raise RuntimeError(_request_ctx_err_msg)
    return getattr(top, name)


def _lookup_app_object(name):
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError(_app_ctx_err_msg)
    return getattr(top, name)


def _find_app():
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError(_app_ctx_err_msg)
    return top.app


# context locals
_request_ctx_stack = LocalStack()
_app_ctx_stack = LocalStack()
# 指向_app_ctx_stack的栈顶元素
current_app = LocalProxy(_find_app)
# request指向当前请求上下文的request
request = LocalProxy(partial(_lookup_req_object, "request"))
# session指向当前请求上下文的session
session = LocalProxy(partial(_lookup_req_object, "session"))
# g指向当前应用上下文的g
g = LocalProxy(partial(_lookup_app_object, "g"))
```

全局变量中使用了很多次`werkzeug.local.LocalProxy`，这是因为初始化时，两个上下文栈为空，因此获取栈顶元素的相应变量时将报错，而`LocalProxy`类提供了动态引用栈顶元素的能力。
