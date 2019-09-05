# LVM管理

## 基础概念

LVM的核心是可以对文件系统动态调整。LVN将多个分区整合到一起，对外展现为一个磁盘，还能在使用的过程中新增或移除分区到该LVM中。

LVM中有3个重要概念：

- PV：物理卷，对应每个分区。
- VG：卷组，由多个PV组成，对外展现为一个磁盘。
- LV：逻辑卷，对应单盘中的分区概念，可以用于做文件系统。
- PE：VG中的块大小，默认每块4MB。

其整体结构图为：

![1567677977585](C:\Users\fwx788132\AppData\Roaming\Typora\typora-user-images\1567677977585.png)

可以通过命令查看已经存在的pv、vg、lv。

```bash
# 查看所有的pv
[root@localhost ~]# pvs
  PV         VG   Fmt  Attr PSize   PFree 
  /dev/md3   vg00 lvm2 a--  538.08g 393.08G
# 查看所有的vg
[root@localhost ~]# vgs
  VG   #PV #LV #SN Attr   VSize   VFree 
  vg00   1  14   0 wz--n- 538.08g 393.08G
# 查看逻辑卷
[root@localhost ~]# lvs
  LV                  VG   Attr       LSize   
  opt                 vg00 -wi-ao----  60.00g
  swap                vg00 -wi-ao----  20.00g
  tmp                 vg00 -wi-ao----  40.00g
  usr                 vg00 -wi-ao----  20.00g
  var                 vg00 -wi-ao----   5.00g                                       
```

## PV管理

- 查看已有PV：`pvs`或`pvscan`
- 创建PV：`pvcreate /dev/分区`
- 删除PV：`pvremove /dev/分区`
- 查看PV详情：`pvdisplay /dev/分区`

## VG管理

- 查看已有VG：`vgs`或`vgscan`
- 创建VG：`vgcreate vg名称 pv名称`
- 删除VG：`vgremove vg名称`
- 查看VG详情：`vgdisplay vg名称`
- 为VG添加PV：`vgextend vg名称 pv名称`
- 从VG中移除PV：`vgreduce vg名称 pv名称`

## LV管理

- 查看已有LV：`lvs`或`lvscan`
- 创建LV：`lvcreate -L 容量 -n lv名称 vg名称`
- 删除LV：`lvremote lv名称 `
- 查看LV详情：`lvdisplay lv名称`
- 调整LV容量：`lvresize -L 新容量 lv名称 `

## 实战 添加home

```bash
# 查看所有的pv
[root@localhost ~]# pvs
  PV         VG   Fmt  Attr PSize   PFree 
  /dev/md3   vg00 lvm2 a--  538.08g 393.08G
# 查看所有的vg
[root@localhost ~]# vgs
  VG   #PV #LV #SN Attr   VSize   VFree 
  vg00   1  14   0 wz--n- 538.08g 393.08G
# 查看逻辑卷
[root@localhost ~]# lvs
  LV                  VG   Attr       LSize   
  opt                 vg00 -wi-ao----  60.00g
  swap                vg00 -wi-ao----  20.00g
  tmp                 vg00 -wi-ao----  40.00g
  usr                 vg00 -wi-ao----  20.00g
  var                 vg00 -wi-ao----   5.00g   
# 创建逻辑卷
[root@localhost ~]# lvcreate -L 160G -n home vg00
# 格式化逻辑卷
[root@localhost ~]# mkfs.ext4 /dev/vg00/home
# 挂载
[root@localhost ~]# mount /dev/vg00/home /home/
[root@localhost ~]# lvs
  LV                  VG   Attr       LSize  
  home                 vg00 -wi-ao----  160.00g
  opt                 vg00 -wi-ao----  60.00g
  swap                vg00 -wi-ao----  20.00g
  tmp                 vg00 -wi-ao----  40.00g
  usr                 vg00 -wi-ao----  20.00g
  var                 vg00 -wi-ao----   5.00g   
```

