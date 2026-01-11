# Docker Desktop 中文设置 - 手动操作指南

## 已完成的准备工作

✅ Docker Desktop 已确认未在运行
✅ 已将 `app-Windows-x86.asar` 复制并重命名为 `app.asar` 保存在项目目录中

## 手动替换步骤

由于系统权限限制，需要您手动完成以下操作：

### 步骤 1：打开Docker安装目录

1. 打开文件资源管理器
2. 导航到：`C:\Program Files\Docker\Docker\frontend\resources`

### 步骤 2：备份原始文件（可选但推荐）

1. 在该目录中找到 `app.asar` 文件
2. 右键点击该文件，选择「重命名」
3. 将其重命名为 `app.asar.backup`（如果已存在该名称，请使用其他名称如 `app.asar.backup.20251231`）

### 步骤 3：复制新文件到Docker目录

1. 打开项目目录：`C:\Users\Administrator\Desktop\项目`
2. 找到已准备好的 `app.asar` 文件
3. 右键点击该文件，选择「复制」
4. 返回Docker资源目录：`C:\Program Files\Docker\Docker\frontend\resources`
5. 在空白处右键点击，选择「粘贴」

### 步骤 4：启动Docker Desktop

1. 双击桌面上的Docker Desktop图标
2. 等待Docker Desktop启动完成
3. 检查界面是否已变为中文

## 恢复原始设置（如果需要）

如果新的中文设置出现问题，您可以：

1. 关闭Docker Desktop
2. 打开 `C:\Program Files\Docker\Docker\frontend\resources` 目录
3. 删除新的 `app.asar` 文件
4. 将之前备份的 `app.asar.backup` 文件重命名回 `app.asar`
5. 重新启动Docker Desktop

## 注意事项

- 请确保在操作过程中Docker Desktop完全关闭
- 如果遇到权限问题，请以管理员身份运行文件资源管理器
- 原始备份文件 `app (2).asar` 请勿修改，保留作为最后的恢复选项
