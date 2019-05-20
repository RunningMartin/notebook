## 修改密码，清理本地缓存的密码信息
git config --system --unset credential.helper
git config --global credential.helper store
