# OpenResty学习笔记—测试工具

## 理念

OpenResty通过自动化测试和持续集成来保证代码质量。

test::nginx是OpenResty测试体系的核心。

## 安装

使用官方CI中的[安装方法](https://github.com/openresty/lua-resty-core/blob/master/.travis.yml)。

- 安装perl包管理器：cpanminus。
- 安装`test::nginx`：`sudo cpanm --notest Test::Nginx IPC::Run > build.log 2>&1 || (cat build.log && exit 1)`
- 克隆最新代码：`git clone https://github.com/openresty/test-nginx.git`
- 加载运行测试案例：`prove -Itest-nginx/lib -j$JOBS -r t`

OpenResty的作者使用perl为Nginx和OpenResty实现了一个DSL。

```perl
use Test::Nginx::Socket;#perl中引用库的方法
run_tests(); # 启动测试，需要使用其他test::nginx中的函数时，请放在该函数前
# 标记下面是数据
__DATA__ 
# TEST 标记一个测试，config是nginx的测试配置，request是发送的请求，body和header指响应中必须存在的信息
=== TEST 1: basic semaphore in uthread
--- http_config eval: $::HttpConfig
--- config
    location /test {
        content_by_lua_block {
            local semaphore = require "ngx.semaphore"
            local sem = semaphore.new()

            local function sem_wait()
                ngx.say("enter waiting")

                local ok, err = sem:wait(1)
                if not ok then
                    ngx.say("err: ", err)
                else
                    ngx.say("wait success")
                end
            end

            local co = ngx.thread.spawn(sem_wait)

            ngx.say("back in main thread")

            sem:post()

            ngx.say("still in main thread")

            ngx.sleep(0.01)

            ngx.say("main thread end")
        }
    }
--- request
GET /test
--- response_body
enter waiting
back in main thread
still in main thread
wait success
main thread end
--- no_error_log
[error]
```

test::nginx还支持很多配置项：

- `stream_config`
- `stream_server_config`
- `no_error_log`

test::nginx的本质是根据测试案例生成配置文件，启动nginx，模拟请求并分析响应信息。

## 常用测试方法

- `--- config`：添加server中的config
- `--- stream_config`：添加stream的配置
- `--- http_config`：添加http模块的配置

### 请求

- `--- request`：发送请求，协议名可以不选。

  ```perl
  # 下面写HTTP协议请求信息
  --- requst
  GET /t
  --- request
  POST /t
  hello world
  # 还能通过eval执行语句
  --- request eval
  "POST /t
  hello\x00\x01\x02
  world\x03\x04\xff"
  ```

- `--- piplined_requests`：批量发起请求。

  ```perl
  --- piplined_request eval
  ["GET /hello","GET /world"]
  ```

- `repeat_each`：重复执行

  ```perl
  # 该文件中所有测试用例重复执行3次
  repeat_each(3)
  run_tests();
  ```

- `--- more_headers`：自定义请求头。

  ```perl
  --- more_headers
  X-Foo:blah
  ```

### 响应

- `--- request_body`：响应体。

  ```perl
  --- request_body
  hello
  # 支持多个请求
  --- request_body eval
  ["hello","world"]
  ```

- `--- request_body_like`、`--- request_body_unlike`支持正则表达式。

- `--- response_headers`：自定义响应头。

- `response_headers_like`、`raw_responese_headers_like`、`raw_response_headers_unlike`。

- `error_code`、`error_code_like`

  ```
  # 支持多个请求的错误码
  --- error_code eval
  [200,200]
  ```

- `error_log`：检查`error.log`中是否存在指定错误标识，默认`[error]`。

- `no_error_log`：默认`[error]`，即不会出现该标识。

## 冷门用法

- `--- ONLY`：指定只运行一个测试案例，正式提交前请取消掉。

  ```perl
  # 只运行这个测试案例
  === TEST 1: get
  --- ONLY
  ```

- `--- SKIP`：忽视该测试案例，用于未实现的功能。

  ```perl
  # 忽视该测试案例
  === TEST 1: get
  --- SKIP
  ```

- `--- LAST`：只执行前面的测试案例。

  ```perl
  # 只执行前面的测试案例
  === TEST 4: get
  --- LAST
  ```

- 测试计划plan：来源于perl模块`Test::Plan`。

  ```perl
  # 假设repeat_each=2 测试案例为10个
  # plan=2*3*10
  
  plan tests => repeat_each() * (3*blocks());
  
  # 3 代表每个测试案例用都显式建立了两次，因为response_code默认隐式检查
  # 推荐直接关闭plan
  use Test::Nginx::Socket 'no_plan';
  # 如果plan不准确时，通过修改plan数字即可
  plan tests => repeat_each() * (3*blocks())+2;
  ```

- 预处理器：通过`add_block_preprocessor`指令可以为同一测试文件中所有的测试案例添加共同配置。

  ```perl
  # 为每个测试案例添加一个config
  add_block_preprocessor(sub {
     my $block=shift;
     if(!defined $block->config){
         $block->set_value("config",<<'_END_')；
         location = /t {
         		echo $arg_a;   
         }
     _END_
     }
  });
  ```

- 自定义函数：在`run_tests`之前可以自定义函数并调用。

  ```perl
  sub read_file{
      my $infile =shift;
      open my $in,$infile;
      	or die "cannot open $infile for reading:$!";
     	my $content = do {local $/;<$in>};
     	close $in;
     	$content;
  }
  
  our $CONTENT = read("t/test.jpg")
  run_tests;
  # 实现post文件
  === TEST 4: sanity
  --- request eval
  "POST /\n$::CONTENT"
  ```

- 乱序：`test::nginx`默认采用乱序，随机执行测试案例，但是某些测试用例需要使用数据库，依赖前面的测试案例执行的结果，因此可以使用如下方法关闭。

  ```perl
  no_shuffle();
  run_tests;
  ```

- reindex：对测试案例进行格式化，`openresty-devel-util`。

## 性能测试

`ab`(Apache Benchmark)工具是一个简单的性能测试工具，但是针对协程和异步I/O的服务器，ab不能利用多核，生成的请求并不够大。`wrk`类似于OpenResty，基于`LuaJIT`和`Redis`，支持Lua，能充分利用系统的多核资源来生成请求。

```bash
# 启动12个线程，保持400个长连接，时间为30S
wrk -t 12 -c 400 -d 30s URI
```

### 测试环境准备

测试时测试环境需要做一些修改。

```bash
# SETP 1： 关闭SELinux，针对Centos/RedHat
# 查看状态
[root@localhost ~]# sestatus
# 临时关闭，永久关闭需要修改文件/etc/selinux/config
[root@localhost ~]# setenforce 0
# SETP 2：打开最大文件数
# 打开最大连接数，第三个数为最大文件数
[root@localhost ~]# cat /proc/sys/fs/file-nr 
11904   0       17976981
# 修改如下参数
[root@localhost ~]# cat /etc/sysctl.conf
fs.file-max
net.ipv4.ip_conntrack_max
net.ipv4.netfilter.ip_conntrack_max
# 重启系统服务
[root@localhost ~]# sudo sysctl -p /etc/sysctl.conf
# SETP 3：检查进程限制
[root@localhost ~]# ulimit -n
65536
# 临时修改，永久修改/etc/security/limits.conf
[root@localhost ~]# ulimit -n 数量
# SETP 4：修改nginx worker连接数
events{
    worker_connections 10240;
}
```

测试环境准备好后，还需要做一次交叉检测，避免犯错。

```bash
# SETP 1：使用自动化工具c1000k，检查环境是否满足100万并发连接的要求
https://github.com/ideawu/c1000k
# 启动服务器，监听端口
./server 7000
# 启动客户端
./client ip 端口
# SETP 2：检测服务端程序是否正常，确保wrk测试的接口正常响应，并在error.log中没有错误信息
```

### 开始测试

```bash
# 默认两个线程和10个长连接
wrk -d 30 URI
```

测试时，需要使用`top`或`htop`工具，看服务器目标程序是否跑满CPU，并且压力测试时间不能太短，以免服务器还未热加载完毕。如果测试过程中CPU满载，并且测试停止后，CPU和内存使用有下降，则压测顺利完成。

火焰图安装：<https://ytlm.github.io/2017/04/%E5%AE%89%E8%A3%85systemtap%E7%94%9F%E6%88%90openresty%E7%9A%84%E7%81%AB%E7%84%B0%E5%9B%BE/>

- CPU不能满载：网络限制或代码中存在阻塞操作，可以通过off CPU火焰图(火焰图工具systemmap)确认。
- CPU一直满载：代码中存在热循环，可能是正则表达式或LuaJIT bug，可以通过on CPU火焰图确认。

性能测试工具可能存在coordinated omission问题(压力测试时，针对响应，只统计发送和接受回复之间的时间是不够的，还需要把测试请求的等待时间也计算在内)，要关注用户的响应时间。

### 测试SSL

`test::nginx`可以测试ssl相关功能，可以参考`https://github.com/iresty/apisix/blob/master/t/admin/ssl.t`
