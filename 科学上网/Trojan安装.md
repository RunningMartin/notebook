# Trojan安装

## 安装Trojan

环境要求：Centos 7，开放80和443端口

```bash
# 切换到root用户
sudo -i
# 安装Trojan
curl -O https://raw.githubusercontent.com/atrandys/trojan/master/trojan_mult.sh && chmod +x trojan_mult.sh && ./trojan_mult.sh
```

安装好后下载连接中提供的包。

## 安装bbr plus

```bash
# 切换到root用户
sudo -i
# 安装bbr plus
cd /usr/src && wget -N --no-check-certificate "https://raw.githubusercontent.com/chiakge/Linux-NetSpeed/master/tcp.sh" && chmod +x tcp.sh && ./tcp.sh
```

## 使用docker 安装客户端

```bash
➜  / sudo mkdir /etc/trojan
➜  / cd /etc/trojan
# 将下载的包中的配置文件和cer证书放在该目录
➜  trojan ls
config.json  CONTRIBUTORS.md  examples  fullchain.cer  LICENSE  README.md
# 编辑config.json，将local_addr改为0.0.0.0
➜  trojan docker pull trojangfw/trojan
# 启动
➜  trojan docker run -dt --name trojan -v /etc/trojan/:/config -p 11080:1080 trojangfw/trojan
# 通过SwitchyOmega使用0.0.0.0 11080，查看状态
# 可以查看日志
➜  trojan docker logs -f trojan
```

## 参考

- https://www.atrandys.com/2019/1963.html
- https://hub.docker.com/r/trojangfw/trojan