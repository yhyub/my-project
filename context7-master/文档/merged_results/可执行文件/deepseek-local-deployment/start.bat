@echo off
chcp 65001 >nul
echo =========================================
echo DeepSeek本地部署工具
echo =========================================
echo.
echo 当前目录: %cd%
echo.
echo 1. 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: Python未安装或未添加到PATH
    echo 请访问 https://www.python.org/downloads/ 下载并安装Python
    pause
    exit /b 1
)
echo.
echo 2. 安装依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo 警告: 依赖安装可能失败，尝试使用 --user 参数...
    pip install -r requirements.txt --user
)
echo.
echo 3. 启动部署脚本...
echo.
python main.py
echo.
echo =========================================
echo 部署完成！
echo =========================================
pause
