# Docker Desktop 中文设置指南

## 确认Docker Desktop状态
- ✅ Docker Desktop已安装（版本：29.1.3）
- ✅ Docker Desktop正在运行

## 手动设置步骤

### 1. 打开Docker Desktop设置界面

1. **启动Docker Desktop**
   - 点击Windows开始菜单
   - 找到并点击 `Docker Desktop` 图标
   - 等待Docker Desktop完全启动（任务栏图标变为稳定状态）

2. **进入设置**
   - 在Docker Desktop主界面右上角，点击齿轮图标 ⚙️
   - 在下拉菜单中选择 `Settings`（或 `Preferences`）

   ![Docker Desktop主界面](https://img.example.com/docker_main.png)  
   *Docker Desktop主界面，右上角齿轮图标位置*

### 2. 配置语言选项

1. **进入General选项卡**
   - 在设置窗口左侧导航栏中，点击 `General` 选项

2. **找到语言设置**
   - 在General选项卡中，向下滚动找到 `UI Language` 或 `Language` 下拉菜单
   - 点击下拉菜单，选择 `中文（简体）` 或 `Chinese (Simplified)`

   ![语言设置位置](https://img.example.com/docker_language_setting.png)  
   *General选项卡中的语言设置位置*

### 3. 应用设置

1. **保存并重启**
   - 点击设置窗口右下角的 `Apply & Restart` 按钮
   - Docker Desktop将自动重启以应用新的语言设置

   ![应用设置按钮](https://img.example.com/docker_apply_restart.png)  
   *Apply & Restart按钮位置*

### 4. 验证结果

1. **检查重启后的界面**
   - Docker Desktop重启完成后，观察界面元素
   - 菜单、按钮、提示信息等应显示为中文

2. **验证成功标志**
   - 主界面标题显示为 `Docker Desktop`
   - 菜单选项如 `设置`、`退出` 等显示为中文
   - 左侧导航栏如 `容器`、`镜像`、`Volumes` 等显示为中文

   ![中文界面示例](https://img.example.com/docker_chinese_ui.png)  
   *Docker Desktop中文界面示例*

## 替代方案：通过配置文件修改

如果上述步骤无法完成，您可以尝试直接修改Docker Desktop的配置文件：

1. **打开配置文件**
   - 按下 `Win + R` 组合键，打开运行对话框
   - 输入 `%APPDATA%\Docker\settings.json`，点击确定

2. **修改语言设置**
   - 在打开的JSON文件中，找到 `language` 字段
   - 将其值修改为 `"zh-CN"`
   - 如果没有该字段，在合适位置添加：`"language": "zh-CN"`

3. **保存并重启**
   - 保存文件并关闭编辑器
   - 重启Docker Desktop以应用更改

## 常见问题排查

1. **设置窗口无法打开**
   - 尝试重启Docker Desktop后再试
   - 检查Docker Desktop是否有更新可用

2. **语言选项中没有中文**
   - 确保Docker Desktop版本支持中文（最新版本通常都支持）
   - 尝试更新Docker Desktop到最新版本

3. **设置后界面仍为英文**
   - 检查配置文件中language字段是否正确设置为"zh-CN"
   - 尝试完全退出Docker Desktop后重新启动

## 验证Docker Desktop版本

您可以通过以下命令验证Docker版本（如果PowerShell正常工作）：
```powershell
docker --version
```

## 联系支持

如果遇到无法解决的问题，您可以：
- 访问Docker官方文档：https://docs.docker.com/desktop/
- 查看Docker Desktop内置的帮助文档
- 在Docker社区论坛寻求帮助

---

**完成状态**：✅ Docker Desktop中文设置指南已创建  
**文档位置**：`c:\Users\Administrator\Desktop\项目\Docker_Desktop_中文设置指南.md`  
**生效方式**：按照上述步骤手动操作即可完成中文设置