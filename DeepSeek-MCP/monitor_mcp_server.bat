@echo off
chcp 65001 >nul

REM =================================================================
REM DeepSeek MCP Server Monitor (Safe Version)
REM Security Features:
REM - No registry modification
REM - No administrator privileges required
REM - No modification of original software files
REM - Full user control
REM - Transparent operation
REM =================================================================

echo ========================================
echo DeepSeek MCP Server Monitor (Safe Version)
echo ========================================
echo Monitoring DeepSeek MCP server status...
echo Press Ctrl+C to stop monitoring
echo ========================================
echo.

:check
REM Get current time
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "datetime=%%a"
set "time=!datetime:~8,2!:!datetime:~10,2!:!datetime:~12,2!"

REM Check if DeepSeek MCP server is running
set "SCRIPT_DIR=%~dp0"
set "SERVER_SCRIPT=%SCRIPT_DIR%deepseek_complete_integrated_mcp.py"

REM Check if server script exists
if not exist "%SERVER_SCRIPT%" (
    echo Error: Server script not found!
    echo Please ensure %SERVER_SCRIPT% is in current folder
    pause
    exit /b 1
)

REM Check if python.exe process is running our server
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq DeepSeek-Complete-MCP-Server" 2>NUL | find /I /N "python.exe">NUL
if %ERRORLEVEL%==1 (
    echo %time% - Server not running
    echo %time% - Restarting server...
    pythonw "%SERVER_SCRIPT%" --start > "%SCRIPT_DIR%mcp_server.log" 2>&1
    if %ERRORLEVEL%==0 (
        echo %time% - Server restarted successfully
    ) else (
        echo %time% - Failed to restart server
    )
) else (
    echo %time% - Server is running normally
)

REM Wait 30 seconds before checking again
echo %time% - Waiting 30 seconds for next check...
timeout /t 30 /nobreak >nul
echo.
goto check
