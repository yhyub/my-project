# Docker 安装指南 - Windows 10 x64

## 系统要求
- Windows 10 专业版、企业版或教育版（64位）
- 内部版本号：1903或更高版本，Build 18362或更高版本
- 启用WSL 2（Windows Subsystem for Linux）
- 至少4GB内存

## 安装步骤

### 1. 启用WSL 2

#### 步骤1：启用WSL功能
以管理员身份运行PowerShell，执行以下命令：
```powershell
wsl --install
```

此命令将：
- 启用适用于Linux的Windows子系统
- 启用虚拟机平台
- 将WSL 2设置为默认版本
- 安装Ubuntu Linux发行版

#### 步骤2：设置WSL默认版本
```powershell
wsl --set-default-version 2
```

### 2. 下载Docker Desktop

访问[Docker官方下载页面](https://www.docker.com/get-started/)，点击"Download for Windows"按钮，下载Docker Desktop安装程序。

### 3. 安装Docker Desktop

1. 运行下载的安装程序（Docker Desktop Installer.exe）
2. 在安装向导中，确保勾选以下选项：
   - "Install required Windows components for WSL 2"
   - "Use WSL 2 instead of Hyper-V"
3. 点击"OK"开始安装
4. 安装完成后，点击"Close and restart"

### 4. 启动Docker Desktop

1. 重启电脑后，启动Docker Desktop
2. 接受Docker条款
3. 登录Docker Hub账号（可选）

### 5. 验证安装

打开PowerShell，执行以下命令验证Docker是否安装成功：

```powershell
# 检查Docker版本
docker --version

# 检查Docker Compose版本
docker compose version

# 运行Hello World容器验证Docker运行状态
docker run hello-world
```

## 常用Docker命令

### 容器操作
- `docker run <image>`: 运行容器
- `docker ps`: 查看正在运行的容器
- `docker ps -a`: 查看所有容器
- `docker stop <container>`: 停止容器
- `docker rm <container>`: 删除容器

### 镜像操作
- `docker pull <image>`: 拉取镜像
- `docker images`: 查看本地镜像
- `docker rmi <image>`: 删除镜像

### 其他常用命令
- `docker info`: 查看Docker系统信息
- `docker logs <container>`: 查看容器日志
- `docker exec -it <container> bash`: 进入容器终端

## 注意事项

1. **性能优化**：
   - 为WSL 2分配足够的内存（建议至少2GB）
   - 在Docker Desktop设置中调整资源分配

2. **防火墙设置**：
   - 确保Windows防火墙允许Docker相关服务通过

3. **更新Docker**：
   - 定期更新Docker Desktop以获取最新功能和安全补丁

4. **WSL 2与Hyper-V**：
   - Docker Desktop在Windows 10上默认使用WSL 2
   - 如果需要使用Hyper-V，可以在设置中切换

## 故障排除

### 常见问题

1. **Docker无法启动**
   - 检查WSL 2是否正确安装
   - 重启WSL服务：`wsl --shutdown`
   - 重启Docker Desktop

2. **容器运行缓慢**
   - 确保WSL 2已启用
   - 为WSL 2分配更多资源

3. **权限问题**
   - 以管理员身份运行PowerShell或命令提示符
   - 将用户添加到docker用户组（仅适用于Linux子系统）

## 参考资源

- [Docker官方文档](https://docs.docker.com/desktop/windows/install/)
- [Windows Subsystem for Linux文档](https://docs.microsoft.com/en-us/windows/wsl/)
- [Docker Hub](https://hub.docker.com/): 查找和分享Docker镜像

## 下一步

安装完成后，您可以：
1. 尝试运行第一个Docker容器
2. 学习Docker Compose来管理多容器应用
3. 探索Docker Hub上的各种镜像
4. 开始构建自己的Docker镜像

祝您使用Docker愉快！