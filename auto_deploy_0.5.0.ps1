# Coze Studio 0.5.0 终极全自动部署脚本
# 安全优先 | 无需人工干预 | 自动重试 | 完整日志

# 强制以管理员权限运行
function Test-Admin {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Host "需要管理员权限，正在重新启动..." -ForegroundColor Yellow
    Start-Sleep 2
    
    $scriptPath = $MyInvocation.MyCommand.Path
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "powershell.exe"
    $psi.Arguments = "-ExecutionPolicy Bypass -File `"$scriptPath`""
    $psi.Verb = "runas"
    
    try {
        [System.Diagnostics.Process]::Start($psi) | Out-Null
    } catch {
        Write-Host "无法以管理员身份运行，请手动以管理员身份运行此脚本" -ForegroundColor Red
    }
    exit
}

# 配置环境
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# 常量定义
$PROJECT_DIR = "C:\Users\Administrator\Desktop\项目"
$COZE_DIR = "$PROJECT_DIR\coze-studio-0.5.0"
$DOCKER_DIR = "$COZE_DIR\docker"
$LOG_FILE = "$PROJECT_DIR\coze_deploy_log_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
$DAEMON_JSON = "$env:ProgramData\docker\config\daemon.json"

# 颜色定义
$COLORS = @{
    INFO = "Cyan"
    SUCCESS = "Green"
    WARN = "Yellow"
    ERROR = "Red"
    DEBUG = "Gray"
    WHITE = "White"
}

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp [$Level] $Message"
    
    # 写入日志文件
    Add-Content -Path $LOG_FILE -Value $logEntry -Force
    
    # 控制台输出带颜色
    $color = $COLORS[$Level] -or $COLORS["WHITE"]
    Write-Host $logEntry -ForegroundColor $color
}

# 重试函数
function Retry {
    param(
        [scriptblock]$ScriptBlock,
        [int]$MaxRetries = 3,
        [int]$DelaySeconds = 5,
        [string]$OperationName = "操作"
    )
    
    $retryCount = 0
    while ($true) {
        try {
            Write-Log "开始 $OperationName..." "INFO"
            return & $ScriptBlock
        } catch {
            $retryCount++
            if ($retryCount -ge $MaxRetries) {
                Write-Log "$OperationName 失败，已重试 $MaxRetries 次：$($_.Exception.Message)" "ERROR"
                return $false
            }
            Write-Log "$OperationName 失败，$DelaySeconds 秒后重试 ($retryCount/$MaxRetries)：$($_.Exception.Message)" "WARN"
            Start-Sleep -Seconds $DelaySeconds
        }
    }
}

# 检查Docker服务
function Check-Docker {
    Write-Log "检查Docker服务状态..." "INFO"
    
    try {
        $dockerVersion = docker version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Docker未运行或未安装：$dockerVersion" "ERROR"
            return $false
        }
        Write-Log "✓ Docker已安装并运行" "SUCCESS"
        Write-Log "Docker版本信息：$dockerVersion" "DEBUG"
        return $true
    } catch {
        Write-Log "检查Docker时出错：$($_.Exception.Message)" "ERROR"
        return $false
    }
}

# 检查Docker Compose
function Check-DockerCompose {
    Write-Log "检查Docker Compose可用性..." "INFO"
    
    try {
        $composeVersion = docker compose version 2>&1
        if ($LASTEXITCODE -ne 0) {
            # 尝试使用旧版docker-compose
            $composeVersion = docker-compose version 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Log "Docker Compose未安装：$composeVersion" "ERROR"
                return $false
            }
            Write-Log "✓ 使用旧版docker-compose" "SUCCESS"
            return "docker-compose"
        }
        Write-Log "✓ 使用新版docker compose" "SUCCESS"
        return "docker compose"
    } catch {
        Write-Log "检查Docker Compose时出错：$($_.Exception.Message)" "ERROR"
        return $false
    }
}

# 配置Docker国内镜像源
function Configure-DockerMirror {
    Write-Log "配置Docker国内镜像源加速..." "INFO"
    
    # 检查是否已配置
    if (Test-Path $DAEMON_JSON) {
        try {
            $currentConfig = Get-Content $DAEMON_JSON -Raw | ConvertFrom-Json
            if ($currentConfig."registry-mirrors" -and $currentConfig."registry-mirrors".Count -gt 0) {
                Write-Log "✓ Docker镜像源已配置，跳过" "SUCCESS"
                Write-Log "当前镜像源：$($currentConfig."registry-mirrors" -join ', ')" "DEBUG"
                return $true
            }
        } catch {
            Write-Log "解析现有配置文件失败，将创建新配置" "WARN"
        }
    }
    
    # 准备新的配置
    $newConfig = @{
        "registry-mirrors" = @(
            "https://docker.mirrors.ustc.edu.cn",
            "https://hub-mirror.c.163.com",
            "https://mirror.baidubce.com",
            "https://registry.docker-cn.com"
        )
        "insecure-registries" = @()
        "debug" = $true
        "experimental" = $false
    }
    
    # 确保目录存在
    $configDir = Split-Path $DAEMON_JSON -Parent
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    
    # 写入配置文件
    try {
        $newConfig | ConvertTo-Json -Depth 10 | Set-Content $DAEMON_JSON -Encoding UTF8 -Force
        Write-Log "✓ Docker镜像源配置已保存" "SUCCESS"
    } catch {
        Write-Log "写入配置文件失败：$($_.Exception.Message)" "ERROR"
        return $false
    }
    
    # 重启Docker服务
    Write-Log "重启Docker服务以应用配置..." "INFO"
    try {
        Restart-Service -Name "docker" -Force -ErrorAction Stop
        Start-Sleep -Seconds 10
        
        # 验证Docker是否重启成功
        $retryCount = 0
        $maxRetries = 5
        while ($retryCount -lt $maxRetries) {
            if (Check-Docker) {
                Write-Log "✓ Docker服务重启成功" "SUCCESS"
                return $true
            }
            $retryCount++
            Start-Sleep -Seconds 2
        }
        
        Write-Log "Docker服务重启后验证失败，可能需要手动重启Docker Desktop" "WARN"
        return $true
    } catch {
        Write-Log "重启Docker服务失败：$($_.Exception.Message)，请手动重启Docker Desktop" "WARN"
        return $true
    }
}

# 检查目标目录
function Check-CozeDirectory {
    Write-Log "检查目标目录结构..." "INFO"
    
    if (-not (Test-Path $COZE_DIR)) {
        Write-Log "错误：目录不存在：$COZE_DIR" "ERROR"
        return $false
    }
    
    Write-Log "✓ 目标目录存在：$COZE_DIR" "SUCCESS"
    
    # 检查docker目录
    if (-not (Test-Path $DOCKER_DIR)) {
        Write-Log "错误：Docker目录不存在：$DOCKER_DIR" "ERROR"
        return $false
    }
    
    Write-Log "✓ Docker目录存在：$DOCKER_DIR" "SUCCESS"
    
    # 检查docker-compose文件
    $composeFiles = @("docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml")
    $foundFile = $null
    
    foreach ($file in $composeFiles) {
        $filePath = "$DOCKER_DIR\$file"
        if (Test-Path $filePath) {
            $foundFile = $file
            Write-Log "✓ 找到docker-compose文件：$file" "SUCCESS"
            break
        }
    }
    
    if (-not $foundFile) {
        Write-Log "警告：未找到标准docker-compose文件，将尝试使用其他配置" "WARN"
        
        # 查找所有yaml文件
        $yamlFiles = Get-ChildItem -Path $DOCKER_DIR -Filter "*.yml" -File
        if ($yamlFiles.Count -gt 0) {
            Write-Log "找到以下YAML文件：" "INFO"
            foreach ($file in $yamlFiles) {
                Write-Log "  - $($file.Name)" "DEBUG"
            }
        }
    }
    
    return $true
}

# 构建和启动容器
function Build-And-Start {
    Write-Log "开始构建和启动Coze Studio容器..." "INFO"
    
    # 切换到Docker目录
    Push-Location $DOCKER_DIR
    
    try {
        # 确定使用的compose命令
        $composeCmd = Check-DockerCompose
        if (-not $composeCmd) {
            return $false
        }
        
        Write-Log "使用命令：$composeCmd" "INFO"
        
        # 执行构建和启动
        $cmd = "$composeCmd --profile `"*`" up -d"
        Write-Log "执行：$cmd" "INFO"
        
        # 使用Start-Process执行，避免命令超时
        $process = Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -Command $cmd" -Wait -NoNewWindow -WorkingDirectory $DOCKER_DIR -PassThru
        
        if ($process.ExitCode -eq 0) {
            Write-Log "✓ 容器构建和启动成功！" "SUCCESS"
            return $true
        } else {
            Write-Log "容器构建或启动失败，退出码：$($process.ExitCode)" "ERROR"
            return $false
        }
    } catch {
        Write-Log "构建和启动过程中出错：$($_.Exception.Message)" "ERROR"
        return $false
    } finally {
        Pop-Location
    }
}

# 验证部署结果
function Validate-Deployment {
    Write-Log "验证部署结果..." "INFO"
    
    try {
        # 检查运行的容器
        $cmd = "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
        $process = Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -Command $cmd" -Wait -NoNewWindow -PassThru -RedirectStandardOutput "$PROJECT_DIR\running_containers.txt"
        
        if (Test-Path "$PROJECT_DIR\running_containers.txt") {
            $runningContainers = Get-Content "$PROJECT_DIR\running_containers.txt"
            Write-Log "运行中的容器：" "INFO"
            foreach ($line in $runningContainers) {
                Write-Log "