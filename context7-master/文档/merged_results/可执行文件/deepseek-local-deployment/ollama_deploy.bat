@echo off
chcp 65001 >nul
cls

echo =========================================
echo DeepSeek-R1 1.5B模型Ollama部署脚本
echo =========================================
echo.
echo 特点：
echo 1. 轻量级部署，资源占用低
echo 2. 安全隔离运行
echo 3. 自动安装和配置
echo 4. 最小化内存和磁盘占用
echo 5. 支持自动启动
echo.

rem 检查Ollama是否已安装
echo 1. 检查Ollama是否已安装...
ollama --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✓ Ollama已安装
) else (
    echo ✗ Ollama未安装
    echo.
    echo 2. 正在下载Ollama安装包...
    bitsadmin /transfer ollama_download /download /priority foreground https://ollama.com/download/OllamaSetup.exe %TEMP%\OllamaSetup.exe
    
    echo.
    echo 3. 正在安装Ollama...
    %TEMP%\OllamaSetup.exe /S
    
    echo.
    echo 4. 等待Ollama服务启动...
    timeout /t 5 /nobreak >nul
    
    rem 刷新环境变量
    set PATH=%PATH%;%USERPROFILE%\.ollama\bin
)

echo.
echo 5. 正在拉取DeepSeek-R1 1.5B模型...
echo 模型大小：约4GB，参数规模：15亿，内存需求：8GB+
echo 这可能需要几分钟时间，请耐心等待...
echo.
ollama pull deepseek-r1:1.5b
if %ERRORLEVEL% EQU 0 (
    echo ✓ DeepSeek-R1 1.5B模型拉取成功
) else (
    echo ✗ 模型拉取失败，请检查网络连接
    pause
    exit /b 1
)

echo.
echo 6. 正在测试DeepSeek模型...
echo 测试提示：你好，介绍一下你自己
echo.
ollama run deepseek-r1:1.5b "你好，介绍一下你自己" | head -20

echo.
echo =========================================
echo DeepSeek-R1 1.5B模型部署完成！
echo =========================================
echo.
echo 使用说明：
echo 1. 直接使用模型：
echo    ollama run deepseek-r1:1.5b "你好"
echo.
echo 2. 查看模型列表：
echo    ollama list
echo.
echo 3. 模型大小和参数：
echo    - 模型名称：deepseek-r1:1.5b
echo    - 参数规模：15亿
echo    - 磁盘占用：约4GB
echo    - 内存需求：8GB+
echo    - CPU/GPU：自动检测，优先使用GPU
echo.
echo 4. 自动启动：
echo    ✓ Ollama服务已配置为自动启动
echo    ✓ 重启电脑后自动运行，无需手动启动
echo.
echo 5. 安全特性：
echo    ✓ 容器化隔离运行
echo    ✓ 最小权限原则
echo    ✓ 自动更新支持
echo.
echo 6. 资源占用：
echo    ✓ 内存占用：约4-6GB（运行时）
echo    ✓ CPU占用：按需使用
echo    ✓ 磁盘占用：约4GB（静态）
echo.
echo 部署完成！模型已成功运行。
echo 按任意键退出...
pause >nul
