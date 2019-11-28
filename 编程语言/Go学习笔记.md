# Go学习笔记

## 安装

- 官网下载安装文件后，确保`bin`目录在`PATH`环境变量中。

- 配置环境变量，`go get`指令需要使用。

```bash
➜  Desktop echo "export GO111MODULE=on" >> ~/.zshrc    
➜  Desktop echo "export GOSUMDB=off" >> ~/.zshrc
➜  Desktop echo "export GOPROXY=https://goproxy.cn" >> ~/.zshrc
➜  Desktop echo "export GOPATH=/usr/local/apps/go" >> ~/.zshrc
➜  Desktop source ~/.zshrc 
➜  Desktop go get golang.org/x/tour
# 设置软连接
➜  Desktop sudo ln -s /usr/local/apps/go/bin/godoc /usr/bin/godoc
➜  Desktop sudo ln -s /usr/local/apps/go/bin/go /usr/bin/go
➜  Desktop sudo ln -s /usr/local/apps/go/bin/gofmt /usr/bin/gofmt
```

## 常用指令

- `go run 文件.go`：运行简单文件。
- `go build|go install`：编译为可执行文件。
- `go fmt`：格式化Go代码。
- `go get`：拉取远程代码库，搭配`GOPATH`，默认位置为`~/go`目录。
- `go test`：运行单元和基准测试用例测试。
- `go doc 包`：查看官方文档。
- `go mod`：管理包依赖。

本地文档

- 获取：`go get golang.org/x/tour `
- 安装`godoc`：`go get golang.org/x/tools/cmd/godoc`
- 启动：`godoc -http=:9999`

## 问题

1、疑问：`go get 包名`出现`timeout`或`410`错误。

- 分析：`go`官网被墙，需要设置代理，推荐使用七牛的代理`https://github.com/goproxy/goproxy.cn`。

```bash
➜  Desktop echo "export GO111MODULE=on" >> ~/.zshrc    
➜  Desktop echo "export GOSUMDB=off" >> ~/.zshrc
➜  Desktop echo "export GOPROXY=https://goproxy.cn" >> ~/.zshrc
➜  Desktop echo "export GOPATH=/usr/local/apps/go" >> ~/.zshrc
➜  Desktop source ~/.zshrc 
➜  Desktop go get golang.org/x/tour
```

