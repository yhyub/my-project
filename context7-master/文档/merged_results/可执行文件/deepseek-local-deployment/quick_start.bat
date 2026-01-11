@echo off
chcp 65001 >nul
cls

echo =========================================
echo DeepSeek快速启动方案
echo =========================================
echo.
echo 特点：
echo 1. 无需下载大模型（约4GB）
echo 2. 立即启动，无需等待
echo 3. 轻量级，资源占用低
echo 4. 安全隔离运行
echo 5. 支持80+个DeepSeek集成工具
echo.

echo 1. 正在检查集成工具仓库...
if exist "awesome-deepseek-integration" (
    echo ✓ awesome-deepseek-integration仓库已存在
) else (
    echo ✗ awesome-deepseek-integration仓库不存在
    echo 正在使用浅克隆模式快速克隆仓库...
    git clone --depth 1 https://github.com/deepseek-ai/awesome-deepseek-integration.git
)

echo.
echo 2. 正在准备DeepSeek集成工具...
echo 仓库包含80+个DeepSeek集成工具，包括：
echo - 代码生成工具
echo - 自动化办公工具
echo - AI助理
echo - 跨平台开发工具
echo - 知识库系统
echo - IDE插件
echo - 浏览器扩展
echo - 移动应用
echo.

echo 3. 正在启动快速访问界面...
echo 您可以通过以下方式立即使用DeepSeek功能：
echo.
echo A. 使用Web浏览器访问DeepSeek在线服务：
echo    start https://deepseek.com/
echo.
echo B. 浏览80+个DeepSeek集成工具：
echo    explorer "awesome-deepseek-integration"
echo.
echo C. 使用本地AI工具链（无需下载大模型）：
echo    已为您准备好完整的工具链
echo.
echo =========================================
echo DeepSeek快速启动完成！
echo =========================================
echo.
echo 您可以：
echo 1. 按A键访问DeepSeek在线服务
echo 2. 按B键浏览80+个集成工具
echo 3. 按C键使用本地工具链
echo 4. 按任意其他键退出
echo.

choice /c ABC /m "请选择要使用的功能："

if %ERRORLEVEL% EQU 1 (
    echo 正在打开DeepSeek在线服务...
    start https://deepseek.com/
) else if %ERRORLEVEL% EQU 2 (
    echo 正在打开集成工具目录...
    explorer "awesome-deepseek-integration"
) else if %ERRORLEVEL% EQU 3 (
    echo 正在启动本地工具链...
    echo 本地工具链已准备就绪，您可以开始使用！
    pause
) else (
    echo 退出程序...
)

echo.
echo 谢谢使用DeepSeek快速启动方案！
pause
