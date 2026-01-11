@echo off

REM ZeroDB 启动脚本

setlocal enabledelayedexpansion

REM 检查Python是否安装
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误: 未安装Python。请先安装Python 3.6或更高版本。
    pause
    exit /b 1
)

REM 检查是否需要安装依赖
pip list | findstr "psutil" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 正在安装必要依赖...
    pip install psutil
    if %ERRORLEVEL% neq 0 (
        echo 错误: 无法安装依赖。
        pause
        exit /b 1
    )
)

REM 启动ZeroDB服务器
echo 正在启动ZeroDB服务器...
python server.py

pause
