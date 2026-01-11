@echo off
REM Set encoding to UTF-8
chcp 65001 >nul

REM =================================================================
REM DeepSeek Complete Integration MCP Safe Startup Script
REM Security Features:
REM - No system registry modification
REM - No administrator privileges required
REM - No modification of original software files
REM - Full user control
REM - Transparent operation
REM - Error handling
REM =================================================================

REM Check if DeepSeek Complete Integration MCP server is already running
echo Checking DeepSeek MCP server status...

REM Check if python.exe process is running our server
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq DeepSeek-Complete-MCP-Server" 2>NUL | find /I /N "python.exe">NUL
if %ERRORLEVEL% == 0 (
    echo Server already running
    goto start_trae
)

REM Start DeepSeek Complete Integration MCP server (background)
echo Starting DeepSeek MCP server...
set "SCRIPT_DIR=%~dp0"
pythonw "%SCRIPT_DIR%deepseek_complete_integrated_mcp.py" --start > "%SCRIPT_DIR%mcp_server.log" 2>&1
if %ERRORLEVEL% == 0 (
    echo Server started successfully
) else (
    echo Server failed to start
    pause
    exit /b 1
)

:start_trae
REM Start Trae CN software
echo Starting Trae CN software...
start "Trae CN" "C:\Program Files\Trae CN\Trae CN.exe" 2>NUL
if %ERRORLEVEL% neq 0 (
    start "Trae CN" "C:\Program Files (x86)\Trae CN\Trae CN.exe" 2>NUL
    if %ERRORLEVEL% neq 0 (
        echo Trae CN installation path not found, please start manually
    ) else (
        echo Trae CN started successfully
    )
) else (
    echo Trae CN started successfully
)

REM Display startup completion information
echo.
echo DeepSeek MCP Service Started!
echo MCP Server URL: http://localhost:8000
echo Default Model: deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
echo Supported Models: 11
echo.
echo Usage:
echo 1. Configure MCP tool in Trae CN
echo 2. Use supported commands to call AI models
echo 3. View logs: %SCRIPT_DIR%mcp_server.log
echo.
echo Press any key to exit...
pause >nul
