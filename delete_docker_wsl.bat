@echo off
setlocal

echo ===============================================
echo Docker WSL 磁盘文件删除工具
echo ===============================================
echo.

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 错误：请以管理员身份运行此脚本！
    echo 右键点击脚本，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo 1. 正在关闭 Docker Desktop...
:: 尝试关闭 Docker Desktop
 taskkill /F /IM "Docker Desktop.exe" /T >nul 2>&1
 taskkill /F /IM "docker.exe" /T >nul 2>&1
 taskkill /F /IM "dockerd.exe" /T >nul 2>&1

echo 2. 正在停止所有 WSL 实例...
wsl --shutdown >nul 2>&1

echo 3. 正在验证 Docker 进程...
tasklist | findstr Docker >nul
if %errorLevel% equ 0 (
    echo 警告：仍有 Docker 进程在运行！
    echo 请手动关闭 Docker Desktop 后重试
    pause
    exit /b 1
)

echo 4. 正在删除 Docker WSL 磁盘文件...
set DOCKER_WSL_PATH="C:\Users\Administrator\AppData\Local\Docker\wsl\disk"

:: 检查目录是否存在
if not exist %DOCKER_WSL_PATH% (
    echo 目录不存在：%DOCKER_WSL_PATH%
    echo 可能已经删除或路径不正确
    pause
    exit /b 1
)

:: 执行删除操作
del /F /S /Q %DOCKER_WSL_PATH%\*.* >nul 2>&1
rmdir /S /Q %DOCKER_WSL_PATH% >nul 2>&1

::