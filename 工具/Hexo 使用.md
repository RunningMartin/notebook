# Hexo 使用

## 0X01 安装依赖

```bash
[root@fangjie ~]# mkdir nodejs
[root@fangjie ~]# cd nodejs/
# 下载nodejs
[root@fangjie nodejs]# wget https://nodejs.org/dist/v13.0.1/node-v13.0.1-linux-x64.tar.xz
[root@fangjie nodejs]#  tar -xvf node-v13.0.1-linux-x64.tar.xz
[root@fangjie nodejs]#  mv node-v13.0.1-linux-x64 node
root@fangjie nodejs]#  mkdir /usr/local/software/
[root@fangjie nodejs]#  sudo mv node /usr/local/software/

# 创建快捷方式
[root@fangjie nodejs]#  cd /usr/local/software/node
[root@fangjie node]#  ln -s /usr/local/software/node/bin/npm   /usr/local/bin/
[root@fangjie node]#  ln -s /usr/local/software/node/bin/node   /usr/local/bin/
[root@fangjie node]#  npm -v
6.12.0
[root@fangjie node]#  node -v
v13.0.1

# 更换为淘宝源
[root@fangjie node]# sudo npm install -g cnpm --registry=https://registry.npm.taobao.org
[root@fangjie node]#  ln -s /usr/local/software/node/bin/cnpm   /usr/local/bin/
[root@fangjie node]#  cnpm -v
cnpm@6.1.0 (/usr/local/software/node/lib/node_modules/cnpm/lib/parse_argv.js)
npm@6.12.0 (/usr/local/software/node/lib/node_modules/cnpm/node_modules/npm/lib/npm.js)
node@13.0.1 (/usr/local/software/node/bin/node)
npminstall@3.23.0 (/usr/local/software/node/lib/node_modules/cnpm/node_modules/npminstall/lib/index.js)
prefix=/usr/local/software/node 
linux x64 3.10.0-957.21.3.el7.x86_64 
registry=https://r.npm.taobao.org

# 安装git
[root@fangjie node]#  sudo yum -y install git
[root@fangjie node]#  git --version
git version 1.8.3.1

# 安装hexo
[root@fangjie node]#  sudo cnpm install -g hexo-cli
[root@fangjie node]#  ln -s /usr/local/software/node/bin/hexo   /usr/local/bin/
[root@fangjie node]#  hexo -v
hexo-cli: 3.1.0
os: Linux 3.10.0-957.21.3.el7.x86_64 linux x64
node: 13.0.1
v8: 7.8.279.17-node.14
uv: 1.33.1
zlib: 1.2.11
brotli: 1.0.7
ares: 1.15.0
modules: 79
nghttp2: 1.39.2
napi: 5
llhttp: 1.1.4
openssl: 1.1.1d
cldr: 35.1
icu: 64.2
tz: 2019a
unicode: 12.1
```

## 0X02 创建项目

```bash
[root@fangjie node]#  mkdir ~/blog_conf
[root@fangjie node]#  cd ~/blog_conf
[root@fangjie blog_conf]#  hexo init RunningMartin.coding.me
```

## 0X03 配置模块

- 安装`Next`主题

```bash
[root@fangjie blog_conf]#  cd RunningMartin.coding.me
[root@fangjie RunningMartin.coding.me]#  git clone https://github.com/iissnan/hexo-theme-next.git themes/next
[root@fangjie RunningMartin.coding.me]#  tree -L 1
.
├── _config.yml    # Hexo配置文件
├── node_modules
├── package.json
├── package-lock.json
├── scaffolds
├── source
└── themes
[root@fangjie RunningMartin.coding.me]#  tree -L 1 themes/next/
themes/next/
├── bower.json
├── _config.yml		# next主题配置文件
├── gulpfile.coffee
├── languages
├── layout
├── LICENSE
├── package.json
├── README.cn.md
├── README.md
├── scripts
├── source
└── test
```

- 配置Hexo：https://hexo.io/zh-cn/docs/configuration.html
- 配置Next： https://theme-next.iissnan.com/