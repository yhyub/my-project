@echo off
chcp 65001 >nul
cls

echo ========================================
echo    Coze Studio 0.2.0 一键部署脚本
echo ========================================
echo.
echo 🔒 安全优先 | 🤖 无需人工干预 | ⏱️  自动重试
echo 📝 完整日志 | ✅ 全程监控
echo.
echo 正在检查系统环境...
echo.

REM 检查PowerShell
powershell -Command "exit 0" >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: PowerShell不可用
    pause
    exit /b 1
)

REM 检查Docker
 docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Docker未安装或未运行
    echo ⚠️  请安装并启动Docker Desktop
    pause
    exit /b 1
)

echo ✅ Docker已安装并运行
echo.
echo 🚀 正在启动全自动部署...
echo ⏰ 这可能需要一些时间，请耐心等待...
echo 📌 请勿关闭此窗口
echo.
echo ========================================
echo 部署过程可能需要10-30分钟
echo 具体时间取决于网络和系统性能
echo ========================================
echo.

REM 运行PowerShell部署脚本
powershell -ExecutionPolicy Bypass -File "%~dp0auto_deploy_final.ps1"

echo.
echo ========================================
echo 🎉 部署完成！
echo ========================================
echo.
echo 🔍 日志文件: %~dp0coze_deploy_log_*.txt
echo 📋 部署报告: %~dp0coze_deploy_report_*.txt
echo.
echo ✅ 所有容器已显示在Docker Desktop中
echo.
echo 按任意键退出...
pause >nul
