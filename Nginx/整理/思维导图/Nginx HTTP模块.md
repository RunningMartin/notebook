# Nginx HTTP模块

## 11个处理阶段

- POST_READ
  - realip模块
    - 模块：ngx_http_realip_module
    - 默认不编译
    - 作用：获取用户真实IP，默认从TCP四元组中获取。
    - 变量：
      - realip_remote_addr：TCP连接源IP
      - realip_remote_port：TCP连接源端口
    - 指令：
      - set_real_ip_from
        - 设置可信地址
        - 可信地址发起的连接才会替换remote_addr
      - real_ip_header 
        - 指定remote_addr的来源
        - 采用X-Forwarded-For时，取末尾IP
      - real_ip_recursive
        - 默认关闭
        - 打开时，依据X-Forwarded-For，从右到左，选第一个不等于set_real_ip_from指定的IP
- SERVER_REWRITE
  - rewrite模块
- `FIND_CONFIG`
  - Nginx框架负责
- `REWRITE`
  - rewrite模块
- `POST_REWRITE`
- `PREACCESS`
  - limit_req模块
  - limit_conn模块
- `ACCESS`
  - access模块
  - auth_basic模块
  - auth_request模块
- `POST_ACCESS`
- `PRECONTENT`
  - try_files模块
  - mirrors模块
- `CONTENT`
  - concat模块
  - random_index模块
  - index模块
  - auto_index模块
  - static模块
- `LOG`
  - log
