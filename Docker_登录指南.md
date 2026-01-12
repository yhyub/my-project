# Docker Hub 正确登录指南

本指南将详细介绍如何在中文界面下正确登录 Docker Hub，包括 GUI 和命令行两种方法。

## 一、Docker Desktop 中文界面登录

### 步骤 1：打开 Docker Desktop

1. 双击桌面或开始菜单中的 Docker Desktop 图标
2. 等待 Docker Desktop 完全启动，进入中文界面

### 步骤 2：登录 Docker Hub

1. 在 Docker Desktop 界面中，点击左侧导航栏的 **设置**（齿轮图标）
2. 在设置页面中，点击左侧的 **Docker Hub** 选项
3. 在右侧区域点击 **登录** 按钮
4. 在弹出的登录窗口中：
   - **用户名**：输入您的 Docker Hub 用户名
   - **密码**：输入您的 Docker Hub 密码
   - （可选）勾选 **记住我** 以便下次自动登录
5. 点击 **登录** 按钮

### 步骤 3：验证登录状态

登录成功后，您将在 Docker Hub 设置页面看到：
- 显示您的用户名
- 显示 **已登录** 状态
- 提供 **退出登录** 选项

## 二、命令行登录方法

如果您偏好使用命令行，可以通过以下步骤登录：

### 步骤 1：打开命令提示符或 PowerShell

1. 按下 `Win + R` 打开运行窗口
2. 输入 `cmd` 或 `powershell`，然后按 Enter 键

### 步骤 2：执行登录命令

```bash
docker login
```

### 步骤 3：输入凭证

命令执行后，系统会提示您输入：
- `Username:`：您的 Docker Hub 用户名
- `Password:`：您的 Docker Hub 密码（输入时不会显示字符）

### 步骤 4：验证登录成功

登录成功后，您将看到类似以下提示：
```
Login Succeeded
```

## 三、验证登录状态

无论使用哪种登录方法，都可以通过以下命令验证登录状态：

```bash
docker info | findstr "Username"
```

如果已登录，将显示您的 Docker Hub 用户名。

## 四、安全提示

1. **不要在命令行中直接暴露密码**：避免使用 `docker login -u username -p password` 这种格式，因为密码会保存在命令历史中
2. **使用访问令牌**：对于生产环境，建议使用 Docker Hub 访问令牌代替密码登录
3. **定期更换密码**：定期更新您的 Docker Hub 密码以提高安全性
4. **启用双因素认证**：在 Docker Hub 账户设置中启用双因素认证

## 五、常见问题及解决方案

### 问题 1：登录时提示 "incorrect username or password"

解决方案：
- 检查用户名和密码是否正确
- 注意区分大小写
- 确保 Caps Lock 键未开启

### 问题 2：网络连接失败

解决方案：
- 检查网络连接是否正常
- 确保防火墙或代理设置允许 Docker 访问网络
- 尝试切换网络环境

### 问题 3：登录后无法拉取镜像

解决方案：
- 检查镜像名称是否正确
- 确保您有权限访问该镜像
- 尝试重新登录

## 六、退出登录

### Docker Desktop 界面退出

1. 进入 Docker Desktop 设置页面
2. 点击 **Docker Hub** 选项
3. 点击 **退出登录** 按钮

### 命令行退出

```bash
docker logout
```

登录成功后，您就可以自由地拉取、推送和管理 Docker 镜像了！