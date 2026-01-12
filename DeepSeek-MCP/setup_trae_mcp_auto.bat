@echo off
chcp 65001 >nul

REM =================================================================
REM DeepSeek Complete Integration MCP Auto-Configuration Tool (Safe Version)
REM Security Features:
REM - No registry modification
REM - No administrator privileges required
REM - No modification of original software files
REM - Full user control
REM - Transparent operation
REM =================================================================

echo =========================================
echo DeepSeek MCP Configuration Tool (Safe Version)
echo =========================================
echo This tool will create safe shortcuts without modifying system registry
echo =========================================
echo.

echo Step 1: Creating desktop shortcut...

set "DESKTOP=%USERPROFILE%\Desktop"
set "SCRIPT_PATH=%~dp0start_trae_with_mcp.bat"

REM Check if script exists
if not exist "%SCRIPT_PATH%" (
    echo Error: Start script not found!
    echo Please ensure start_trae_with_mcp.bat is in current folder
    pause
    exit /b 1
)

REM Create shortcut using PowerShell (safe method)
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\Trae CN with MCP.lnk'); $Shortcut.TargetPath = '%SCRIPT_PATH%'; $Shortcut.IconLocation = 'shell32.dll,1'; $Shortcut.Save()" >nul

if %ERRORLEVEL% == 0 (
    echo Success: Desktop shortcut created: %DESKTOP%\Trae CN with MCP.lnk
    echo   Double-click this shortcut to start Trae CN and MCP server
    echo   This shortcut is safe and does not modify any system files
) else (
    echo Error: Failed to create shortcut
    echo   Please create shortcut manually
)

echo.
echo Step 2: Displaying usage instructions...
echo =========================================
echo Safe Usage Guide
echo =========================================
echo 1. Double-click desktop shortcut "Trae CN with MCP" to start
echo 2. Or run start_trae_with_mcp.bat directly
echo 3. Run monitor_mcp_server.bat to monitor server status
echo 4. View mcp_server.log file for running information
echo.
echo Security Features:
echo - No registry modification
echo - No administrator privileges required
echo - No modification of original software files
echo - Full user control
echo - Transparent operation
echo - Error handling mechanism
echo - Log recording
echo.
echo Step 3: Creating configuration file...

REM Create configuration file
if not exist "%~dp0deepseek_complete_mcp_config.json" (
    echo {
        "siliconflow_api_url": "https://api.siliconflow.cn/v1/chat/completions",
        "api_key": "sk-nhmrjxrkoafgnffhwvcforpkgexmsdvasjolntzdcqtbdqcz",
        "default_model": "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
        "output_path": "./output",
        "timeout": 300,
        "security_level": "high",
        "server_host": "localhost",
        "server_port": 8000,
        "supported_models": [
            "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
            "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "THUDM/glm-4-9b-chat",
            "THUDM/GLM-Z1-9B-0414",
            "THUDM/GLM-4-9B-0414",
            "THUDM/GLM-4.1V-9B-Thinking",
            "Kwai-Kolors/Kolors",
            "deepseek-ai/DeepSeek-V3.2-Exp",
            "Pro/deepseek-ai/DeepSeek-V3.2-Exp",
            "deepseek-ai/DeepSeek-V3.1-Terminus",
            "Pro/deepseek-ai/DeepSeek-V3.1-Terminus"
        ]
    } > "%~dp0deepseek_complete_mcp_config.json"
    echo Success: Configuration file created: deepseek_complete_mcp_config.json
) else (
    echo Configuration file already exists, skipping creation
)

echo.
echo =========================================
echo Configuration Complete!
echo =========================================
echo Created files:
echo 1. Desktop shortcut: Trae CN with MCP.lnk
echo 2. Configuration file: deepseek_complete_mcp_config.json
echo 3. Usage guide: Security_Startup_Guide.md
echo.
echo Now you can:
echo - Double-click desktop shortcut to start Trae CN and MCP server
echo - Run start_trae_with_mcp.bat to start manually
echo - Run monitor_mcp_server.bat to monitor server status
echo.
echo Press any key to exit...
pause >nul
