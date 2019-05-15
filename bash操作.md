# bash

## 常用命令

- 命令历史：`history`
- 补全功能：`tab键`
- 别名设置：
  - 创建别名：`alias 别名='命令串'`，`alias myll='ls -al'`
  - 取消别名：`unalias 别名`
- 查看是否为内建命令：`type 命令`

## 登录信息定制

- `/etc/issue`：本地打开`bash`时欢迎信息

| 符号 | 含义         |
| ---- | ------------ |
| `\d` | 日期         |
| `\t` | 时间         |
| `\l` | 终端号       |
| `\m` | cpu类型      |
| `\n` | 主机网络名称 |
| `\O` | domain name  |
| `\r` | 操作系统版本 |
| `\S` | 操作系统名称 |

- `/etc/issue.net`：定制`ssh`远程登录信息，具体调用那个文件需要查看`/etc/ssh/sshd_config`的Banner字段。

## 环境配置

- `login shell`：新建bash需要输入账号与密码。会读取以下几个配置文件：
  - `/etc/profile`：系统设置
    - `PATH`：根据UID确定`PATH`变量的具体内容。
    - `umask`：默认权限。
    - `/etc/profile.d/*.sh`：执行里面的文件，加载配置。
    - `/etc/locale.conf`：编码，由`lang.sh`加载。
    - `/usr/share/bash-completion/completions/*`：`tab`补全，由`bash_completion.sh`加载。
  - `~/.bash_profile或~/.bash_login或~/.profile`：用户自定义配置，根据次序，只读取一个。
- `non-login shell`： 新建bash不需要重新登录。
  - `~/.bashrc`：只读取这个配置文件。
- `source`：重新加载配置文件。

## 编码

- 查看支持的编码：`locale -a`
- 查看当前编码：`local`
- 编码文件位置：`/usr/bin/locale`
- 修改编码：`/etc/locale.conf`
- 主要参数
  - `LANG`：系统默认语言，显示乱码的话可以设置为`en_US.UTF-8`或为空。
  - `LC_ALL`：国际化设置，用于设置时间格式、排序规则等。
