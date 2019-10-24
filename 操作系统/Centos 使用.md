# Centos 使用

## 防火墙

```bash
# 查看已经开放的端口
[root@localhost network-scripts]# firewall-cmd --list-all
public (active)
  target: default
  icmp-block-inversion: no
  interfaces: enp0s3
  sources: 
  services: cockpit dhcpv6-client ssh
  ports: 
  protocols: 
  masquerade: no
  forward-ports: 
  source-ports: 
  icmp-blocks: 
  rich rules: 
# 添加端口
[root@localhost network-scripts]# firewall-cmd --zone=public --permanent --add-port 8080/tcp
Warning: ALREADY_ENABLED: 8080:tcp
success
[root@localhost network-scripts]# firewall-cmd --zone=public --permanent --add-port 80/tcp
success
# 重新加载防火墙规则
[root@localhost network-scripts]# firewall-cmd --reload 
success
[root@localhost network-scripts]# firewall-cmd --list-all
public (active)
  target: default
  icmp-block-inversion: no
  interfaces: enp0s3
  sources: 
  services: cockpit dhcpv6-client ssh
  ports: 8080/tcp 80/tcp
  protocols: 
  masquerade: no
  forward-ports: 
  source-ports: 
  icmp-blocks: 
  rich rules:
```

