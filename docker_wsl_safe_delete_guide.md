# Docker WSL 磁盘文件安全删除指南

## 1. 确认文件位置
Docker Desktop for Windows 使用 WSL 2 时，镜像和容器数据默认存储在以下位置：
```
C:\Users\Administrator\AppData\Local\Docker\wsl\disk\
```

## 2. 安全删除前的准备工作

### 2.1 完全关闭 Docker Desktop
- 右键点击任务栏中的 Docker 图标
- 选择 "Quit Docker Desktop"
- 等待 Docker 完全退出（任务栏图标消失）

### 2.2 停止所有 WSL 实例
打开 PowerShell 以管理员身份运行：
```powershell
# 列出所有 WSL 发行版
wsl --list -v

# 停止所有 WSL 发行版
wsl --shutdown
```

### 2.3 确认 Docker 进程已终止
```powershell
# 检查是否还有 Docker 相关进程在运行
tasklist | findstr Docker
```
如果有进程运行，使用 `taskkill` 命令终止：
```powershell
taskkill /F /IM "Docker Desktop.exe" /T
taskkill /F /IM "docker.exe" /T
taskkill /F /IM "dockerd.exe" /T
```

## 3. 安全删除操作

### 3.1 手动删除 WSL 磁盘文件
1. 打开文件资源管理器，导航到：
   ```
   C:\Users\Administrator\AppData\Local\Docker\wsl\disk\
   ```
2. 您将看到类似以下的文件：
   - `ext4.vhdx` (主要的 Docker 数据磁盘)
   - 可能还有其他 `.vhdx` 文件
3. 选中所有要删除的文件，按 `Shift + Delete` 永久删除（跳过回收站）

### 3.2 清理 WSL 发行版（可选）
如果您想完全清理 Docker 相关的 WSL 发行版：
```powershell
# 查看 Docker 相关的 WSL 发行版
wsl --list -v | findstr docker

# 删除 Docker 发行版（例如）
wsl --unregister docker-desktop
wsl --unregister docker-desktop-data
```

## 4. 验证删除结果
1. 确认磁盘文件已被删除
2. 重新启动 Docker Desktop，它会自动重新创建必要的 WSL 磁盘文件
3. 验证 Docker 功能正常：
   ```powershell
   docker run hello-world
   ```

## 5. 注意事项

### 5.1 数据备份
- 删除这些文件会永久丢失所有本地 Docker 镜像、容器、卷和网络配置
- 在删除前，请确保已备份重要数据：
  ```powershell
  # 导出镜像
  docker save -o my_images.tar image1 image2
  
  # 导出容器
  docker export -o my_container.tar container_name
  
  # 备份卷
  docker run --rm -v my_volume:/source -v $(pwd):/target busybox tar czf /target/volume_backup.tar.gz /source
  ```

### 5.2 权限问题
- 确保您以管理员身份执行所有操作
- 如果遇到权限错误，尝试使用管理员身份打开文件资源管理器

### 5.3 磁盘空间释放
- 删除文件后，Windows 可能需要一些时间来回收磁盘空间
- 您可以运行磁盘清理工具来加速这个过程：
  ```powershell
  cleanmgr /sagerun:1
  ```

## 6. 替代方案：使用 Docker Desktop 清理

如果您不想手动删除文件，也可以使用 Docker Desktop 内置的清理功能：

1. 打开 Docker Desktop
2. 进入 "Settings" > "Resources" > "Advanced"
3. 点击 "Clean/Purge data"
4. 选择要清理的资源类型（镜像、容器、卷等）
5. 点击 "Delete"

这种方式更加安全，但可能不会完全删除 WSL 磁盘文件，只是清理其中的内容。

## 7. 常见问题

### Q: 删除后 Docker 无法启动？
A: 尝试重新安装 Docker Desktop 或重置 WSL：
```powershell
wsl --set-default-version 2
```

### Q: 磁盘空间没有释放？
A: 运行 WSL 压缩命令：
```powershell
# 对于每个 WSL 发行版
wsl --export docker-desktop-data docker-desktop-data.tar
wsl --unregister docker-desktop-data
wsl --import docker-desktop-data "C:\Users\Administrator\