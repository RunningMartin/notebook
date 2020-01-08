# Ubuntu搭建树莓派环境

## qemu简介

qemu是一款开源虚拟中，可以为user-level的进程执行CPU仿真，因此能让不同架构上编译的程序运行在其他架构上。qemu支持在`x86`中模拟`arm`设备。

## 安装qemu

```bash
fangjie@ubuntu:~$ sudo apt-get install qemu-system
```

## 搭建树莓派环境

```bash
# 下载qemu-rpi-kernel
fangjie@ubuntu:~$ mkdir /home/fangjie/qemu_vms/
fangjie@ubuntu:~$ cd /home/fangjie/qemu_vms/
fangjie@ubuntu:~/qemu_vms$ git clone https://github.com/dhruvvyas90/qemu-rpi-kernel
# 拷贝镜像到该目录下
fangjie@ubuntu:~/qemu_vms$ ls
image.img  qemu-rpi-kernel-master  qemu-rpi-kernel-master.zip

# 查看镜像信息
fangjie@ubuntu:~/qemu_vms$ fdisk -l image.img 
Disk image.img: 12 GiB, 12894339072 bytes, 25184256 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x7ca8eb2c

Device     Boot  Start      End  Sectors  Size Id Type
image.img1        8192   532480   524289  256M  c W95 FAT32 (LBA)
image.img2      534528 29837311 29302784   14G 83 Linux

# 挂载镜像，offset为img2的start*512bytes(每个sector的大小为512bytes)
fangjie@ubuntu:~/qemu_vms$ sudo mkdir /mnt/raspbian
fangjie@ubuntu:~/qemu_vms$ sudo mount -v -o offset=273678336 -t ext4 /home/fangjie/qemu_vms/image.img /mnt/raspbian/
mount: /dev/loop8 mounted on /mnt/raspbian.

# 注释镜像中的ld.so.preload文件
fangjie@ubuntu:~/qemu_vms$ sudo echo "#/usr/lib/arm-linux-gnueabihf/libarmmem-${PLATFORM}.so" > /mnt/raspbian/etc/ld.so.preload
fangjie@ubuntu:~/qemu_vms$ sudo cat /mnt/raspbian/etc/ld.so.preload
#/usr/lib/arm-linux-gnueabihf/libarmmem-${PLATFORM}.so

# 解除映射
fangjie@ubuntu:~/qemu_vms$ sudo umount /mnt/raspbian 

# 模拟树莓派
fangjie@ubuntu:~/qemu_vms$ qemu-system-arm -kernel /home/fangjie/qemu_vms/qemu-rpi-kernel-master/kernel-qemu-4.4.34-jessie -M versatilepb -cpu arm1176 -m 256 -M versatilepb -serial stdio -append "root=/dev/sda2 rootfstype=ext4 rw" -hda /home/fangjie/qemu_vms/image.img -redir tcp:5022::22 -no-reboot
```

## 参考资料

- https://azeria-labs.com/emulate-raspberry-pi-with-qemu/
- https://www.jianshu.com/p/da00aea5d666