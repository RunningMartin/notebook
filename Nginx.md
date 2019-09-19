# Nginx

## 初识Nginx

### 使用场景

Nginx通常运行在网络的边界

- 静态资源服务：通过本地文件系统提供服务
- 反向代理服务：缓存、负载均衡
- API服务：OpenResty

### Nginx组成

- Nginx二进制可执行文件
- Nginx.conf配置文件：控制nginx的行为
- access.log访问日志：记录每一条http请求
- error.log错误日志：用于定位问题

### 编译Nginx

- 下载：https://nginx.org/en/download.html

  ```bash
  ➜  Nginx_source wget https://nginx.org/download/nginx-1.17.3.tar.gz
  ➜  Nginx_source tar -zxvf nginx-1.17.3.tar.gz
  ```

- 文件夹

  ```bash
  ➜  nginx-1.17.3 tree -L 1            
  .
  ├── auto	# 供configure命令调用，获取相关信息
  ├── CHANGES	# 修改日志
  ├── CHANGES.ru 	# 俄文修改日志
  ├── conf		# 配置文件模板
  ├── configure	# 生成编译前的配置文件
  ├── contrib		# 提供扩展工具，如vim支持nginx语法
  ├── html		# 提供500错误和欢迎界面
  ├── LICENSE		
  ├── man		# 提供nginx的帮助文档 man ./man/nginx.8
  ├── README
  └── src		# 源码
  # 添加vim扩展包
  ➜  nginx-1.17.3 cp -r contrib/vim/* ~/.vim/
  ```

- configure支持的参数

  ```bash
  ➜  nginx-1.17.3 ./configure --help
  # nginx辅助功能文件
  # 安装目录
  --prefix=PATH          	set installation prefix
  --sbin-path=PATH       	set nginx binary pathname
  ....
  --builddir=DIR         	set build directory
  
  # 模块选择 with开头 默认不开启 with-out 默认开启
  --with-select_module    enable select module
  --without-select_module disable select module
  ....
  # 编译的特殊参数
  --with-cc=PATH     		set C compiler pathname
  ...
  ```

- 生成配置文件

  ```bash
  ➜  nginx-1.17.3 ./configure --prefix=/home/fangjie/Nginx 
  checking for OS
   + Linux 4.15.0-30deepin-generic x86_64
  checking for C compiler ... found
   + using GNU C compiler
   + gcc version: 6.3.0 20170516 (Debian 6.3.0-18+deb9u1) 
  checking for gcc -pipe switch ... found
  ...
  Configuration summary
    + using system PCRE library
    + OpenSSL library is not used
    + using system zlib library
  # 相关目录信息
  nginx path prefix: "/home/fangjie/Nginx"
  nginx binary file: "/home/fangjie/Nginx/sbin/nginx"
  nginx modules path: "/home/fangjie/Nginx/modules"
  ...
  nginx http scgi temporary files: "scgi_temp"
  # 生成的中间文件
  ➜  nginx-1.17.3 tree objs -L 1
  objs
  ├── autoconf.err
  ├── Makefile
  ├── ngx_auto_config.h
  ├── ngx_auto_headers.h
  ├── ngx_modules.c	# 编译时开启的模块
  └── src
  ```

- 编译

  ```bash
  ➜  nginx-1.17.3 make 
  # 生成了大量中间文件与nginx二进制文件
  # 便于升级时，直接拷贝nginx二进制文件到目录中
  ➜  nginx-1.17.3 tree objs -L 1
  objs
  ├── autoconf.err
  ├── Makefile
  ├── nginx			# 二进制文件
  ├── nginx.8			# man文件
  ├── ngx_auto_config.h
  ├── ngx_auto_headers.h
  ├── ngx_modules.c
  ├── ngx_modules.o
  └── src				# 编译时生成的中间文件
  ```

- 安装

  ```bash
  # 安装
  ➜  nginx-1.17.3 make install
  # 查看安装目录
  ➜  nginx-1.17.3 cd /home/fangjie/Nginx
  ➜  Nginx tree -L 1
  .
  ├── conf	# 配置文件目标
  ├── html	
  ├── logs	# 日志目录
  └── sbin	# 二进制文件目录
  ```

### 配置文件

- 配置文件由指令与指令块构成
- 每条指令以`；`结尾，指令与参数间以空格符号分隔
- 指令块通过`{}`将多条指令组织在一起
- `include`语句允许组合多个配置文件，提高可维护性。
- 使用#符号添加注释，提高可读性
- 通过$符号使用变量
- 部分指令的参数支持正则表达式