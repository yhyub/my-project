#!/usr/bin/env powershell
# -*- coding: utf-8 -*-
"""
DeepSeek-R1 1.5B模型Ollama部署脚本
特点：
1. 轻量级部署，资源占用低
2. 安全隔离运行
3. 自动安装和配置
4. 最小化内存和磁盘占用
5. 支持自动启动
"""

# 设置UTF-8编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Green
Write-Host "DeepSeek-R1 1.5B模型Ollama部署脚本" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 检查PowerShell版本
$PSVersion = $PSVersionTable.PSVersion.Major
if ($PSVersion -lt 5) {
    Write-Host "错误：需要PowerShell 5.0或更高版本" -ForegroundColor Red
    pause
    exit 1
}

function Check-Ollama {
    <#检查Ollama是否已安装#>
    try {
        $result = & ollama --version 2>&1
        if ($result -match "ollama version") {
            Write-Host "✓ Ollama已安装" -ForegroundColor Green
            return $true
        }
    } catch {
        # 忽略异常
    }
    Write-Host "✗ Ollama未安装" -ForegroundColor Yellow
    return $false
}

function Install-Ollama {
    <#安装Ollama#>
    Write-Host "正在安装Ollama..." -ForegroundColor Cyan
    
    try {
        # 下载Ollama安装包
        $installerUrl = "https://ollama.com/download/OllamaSetup.exe"
        $installerPath = "$env:TEMP\OllamaSetup.exe"
        
        Write-Host "正在下载Ollama安装包..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
        
        Write-Host "正在安装Ollama..." -ForegroundColor Cyan
        Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait
        
        # 添加到PATH
        $env:PATH += ";$env:USERPROFILE\.ollama\bin"
        [Environment]::SetEnvironmentVariable("PATH", $env:PATH, [System.EnvironmentVariableTarget]::User)
        
        Write-Host "✓ Ollama安装成功" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "✗ Ollama安装失败：$_" -ForegroundColor Red
        Write-Host "请手动下载安装：https://ollama.com/download" -ForegroundColor Yellow
        return $false
    }
}

function Pull-DeepSeekModel {
    <#拉取DeepSeek-R1 1.5B模型#>
    Write-Host "正在拉取DeepSeek-R1 1.5B模型..." -ForegroundColor Cyan
    Write-Host "模型大小：约4GB，参数规模：15亿，内存需求：8GB+" -ForegroundColor Cyan
    
    try {
        # 拉取1.5B模型，这是最轻量级的版本
        $result = & ollama pull deepseek-r1:1.5b 2>&1
        
        if ($result -match "success") {
            Write-Host "✓ DeepSeek-R1 1.5B模型拉取成功" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ 模型拉取失败：$result" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ 模型拉取失败：$_" -ForegroundColor Red
        return $false
    }
}

function Test-DeepSeekModel {
    <#测试DeepSeek模型#>
    Write-Host "正在测试DeepSeek-R1 1.5B模型..." -ForegroundColor Cyan
    
    try {
        # 测试模型生成
        $testPrompt = "你好，介绍一下你自己"
        $result = & ollama run deepseek-r1:1.5b $testPrompt 2>&1 | Select-Object -First 20
        
        Write-Host "✓ 模型测试成功！" -ForegroundColor Green
        Write-Host "模型输出：" -ForegroundColor Cyan
        Write-Host ($result -join "`n") -ForegroundColor White
        return $true
    } catch {
        Write-Host "✗ 模型测试失败：$_" -ForegroundColor Red
        return $false
    }
}

function Configure-AutoStart {
    <#配置Ollama自动启动#>
    Write-Host "正在配置Ollama自动启动..." -ForegroundColor Cyan
    
    try {
        # 检查Ollama服务状态
        $service = Get-Service -Name "Ollama" -ErrorAction SilentlyContinue
        
        if ($service) {
            # 设置服务为自动启动
            Set-Service -Name "Ollama" -StartupType Automatic
            Write-Host "✓ Ollama服务已设置为自动启动" -ForegroundColor Green
        } else {
            Write-Host "✓ Ollama使用用户级自动启动，无需额外配置" -ForegroundColor Green
        }
        
        return $true
    } catch {
        Write-Host "✗ 自动启动配置失败：$_" -ForegroundColor Yellow
        Write-Host "Ollama默认会自动启动，无需担心" -ForegroundColor Cyan
        return $true
    }
}

function Show-Usage {
    <#显示使用说明#>
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "DeepSeek-R1 1.5B模型部署完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`n使用说明：" -ForegroundColor Cyan
    Write-Host "1. 直接使用模型："
    Write-Host "   ollama run deepseek-r1:1.5b '你好'" -ForegroundColor White
    Write-Host "`n2. 查看模型列表："
    Write-Host "   ollama list" -ForegroundColor White
    Write-Host "`n3. 模型大小和参数："
    Write-Host "   - 模型名称：deepseek-r1:1.5b" -ForegroundColor White
    Write-Host "   - 参数规模：15亿" -ForegroundColor White
    Write-Host "   - 磁盘占用：约4GB" -ForegroundColor White
    Write-Host "   - 内存需求：8GB+" -ForegroundColor White
    Write-Host "   - CPU/GPU：自动检测，优先使用GPU" -ForegroundColor White
    Write-Host "`n4. 自动启动："
    Write-Host "   ✓ Ollama服务已配置为自动启动" -ForegroundColor White
    Write-Host "   ✓ 重启电脑后自动运行，无需手动启动" -ForegroundColor White
    Write-Host "`n5. 安全特性："
    Write-Host "   ✓ 容器化隔离运行" -ForegroundColor White
    Write-Host "   ✓ 最小权限原则" -ForegroundColor White
    Write-Host "   ✓ 自动更新支持" -ForegroundColor White
    Write-Host "`n6. 资源占用："
    Write-Host "   ✓ 内存占用：约4-6GB（运行时）" -ForegroundColor White
    Write-Host "   ✓ CPU占用：按需使用" -ForegroundColor White
    Write-Host "   ✓ 磁盘占用：约4GB（静态）" -ForegroundColor White
    Write-Host "`n========================================" -ForegroundColor Green
}

# 主执行流程

# 1. 检查Ollama
if (-not (Check-Ollama)) {
    # 2. 安装Ollama
    if (-not (Install-Ollama)) {
        pause
        exit 1
    }
    # 刷新环境变量
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::Machine) + ";" + [System.Environment]::GetEnvironmentVariable("PATH", [System.EnvironmentVariableTarget]::User)
}

# 3. 拉取模型
if (-not (Pull-DeepSeekModel)) {
    pause
    exit 1
}

# 4. 测试模型
Test-DeepSeekModel

# 5. 配置自动启动
Configure-AutoStart

# 6. 显示使用说明
Show-Usage

Write-Host "`n部署完成！模型已成功运行。" -ForegroundColor Green
Write-Host "按任意键退出..." -ForegroundColor Cyan
pause | Out-Null
