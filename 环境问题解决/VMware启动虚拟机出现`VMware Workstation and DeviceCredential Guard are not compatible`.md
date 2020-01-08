# VMware启动虚拟机出现`VMware Workstation and Device/Credential Guard are not compatible`

## 问题

启动虚拟机出现

![image-20200107111037279](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20200107111037279.png)

## 问题分析

Vmware与`Hyper-V`不兼容，并且在Windows平台中，要求关闭`Device Guard`，参考资料

- `Device Guard`的讨论：https://communities.vmware.com/message/2753727#2753727
- `Hyper-V`的讨论：https://blogs.vmware.com/workstation/2019/08/workstation-hyper-v-harmony.html

## 解决方案

解决方案参考资料为：https://www.youtube.com/watch?v=VIBdY-5zr58，具体流程如下

- 修改组策略：`edit group policy`

  ![image-20200107111246768](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20200107111246768.png)

- 通过`cmd`更新组策略：`gpupdate /force`

  ![image-20200107111327518](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20200107111327518.png)

- 编辑注册表：`Registry Editor`，添加`EnableVirtualizationBasedSecurity`

  ![image-20200107112843392](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20200107112843392.png)

- 编辑注册表：`Registry Editor`，添加`LsaCfgFlags`

  ![image-20200107113117960](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20200107113117960.png)

  

- 关闭`Hyper-V`：`Turn Windows features on or off`

  ![image-20200107113323290](C:\Users\admin\AppData\Roaming\Typora\typora-user-images\image-20200107113323290.png)

- 通过`cmd`执行：

  ```bash
  PS C:\Windows\system32> bcdedit /create  /d "DebugTool" /application osloader
  The entry {3e7ed050-fd22-11e9-8e79-8491a9131e14} was successfully created.
  PS C:\Windows\system32> bcdedit /set path "\EFI\Microsoft\Boot\SecConfig.efi"
  The operation completed successfully.
  PS C:\Windows\system32> bcdedit /set hypervisorlaunchtype off
  The operation completed successfully.
  PS C:\Windows\system32> bcdedit /set  loadoptions DISABLE-LSA-ISO,DISABLE-VBS
  The operation completed successfully.
  ```
  
- 重启解决。