# 手动应用Docker镜像源配置的脚本
# 请以管理员身份运行此脚本

Write-Host "正在复制daemon.json到Docker配置目录..."
Copy-Item -Path "c:\Users\Administrator\Desktop\项目\daemon.json" -Destination "C:\ProgramData\Docker\config\daemon.json" -Force

Write-Host "正在重启Docker服务..."
Restart-Service -Name Docker -Force

Write-Host "Docker镜像源配置已成功应用！"
Write-Host "请等待Docker服务完全启动后，再继续执行后续操作。"