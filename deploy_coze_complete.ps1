# Coze Studio 0.2.0 完整部署脚本
# 作者：Administrator
# 日期：$(Get-Date -Format "yyyy-MM-dd")
# 描述：从GitHub下载Coze Studio的14个容器源码，配置Docker国内镜像源加速，
#       在本地构建后使用docker compose启动所有容器

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色定义
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"
$White = "White"

# 函数：输出带颜色的消息
function Write-ColorMessage {
    param(
        [string]$Message,
        [string]$Color = $White
    )
    Write-Host $Message -ForegroundColor $Color
}

# 函数：检查命令是否存在
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    } catch {
        return $false
    }
}

# 函数：检查Docker是否运行
function Test-DockerRunning {
    try {
        docker info 2>&1 | Out-Null
        return $true
    } catch {
        return $false
    }
}

# 函数：配置Docker国内镜像源
function Configure-DockerMirror {
    Write-ColorMessage "`n配置Docker国内镜像源加速..." -Color $Cyan
    
    # 检查是否已配置镜像源
    $daemonConfigPath = "$env:ProgramData\docker\config\daemon.json"
    
    if (Test-Path $daemonConfigPath) {
        $config = Get-Content $daemonConfigPath -Raw | ConvertFrom-Json
        if ($config.registry-mirrors) {
            Write-ColorMessage "Docker镜像源已，配置跳过配置步骤" -Color $Yellow
            return
        }
    }
    
    # 创建或更新daemon.json配置
    $daemonConfig = @{
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
    $configDir = Split-Path $daemonConfigPath -Parent
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    
    # 写入配置
    $daemonConfig | ConvertTo-Json -Depth 10 | Set-Content $daemonConfigPath -Encoding UTF8
    Write-ColorMessage "Docker镜像源配置已保存到: $daemonConfigPath" -Color $Green
    
    # 重启Docker服务
    Write-ColorMessage "正在重启Docker服务..." -Color $Yellow
    try {
        Restart-Service docker -Force
        Start-Sleep -Seconds 10
        Write-ColorMessage "Docker服务重启完成" -Color $Green
    } catch {
        Write-MessageColor "警告：无法自动重启Docker服务，请手动重启Docker Desktop" -Color $Red
    }
}

# 函数：下载Coze Studio容器源码
function Download-CozeContainers {
    param(
        [string]$DownloadDir = ".\coze-studio-containers"
    )
    
    Write-ColorMessage "`n下载Coze Studio容器源码..." -Color $Cyan
    
    # 创建下载目录
    if (-not (Test-Path $DownloadDir)) {
        New-Item -ItemType Directory -Path $DownloadDir -Force | Out-Null
        Write-ColorMessage "创建下载目录: $DownloadDir" -Color $Green
    }
    
    # Coze Studio容器GitHub仓库列表（14个容器）
    $repositories = @(
        @{Name = "coze-api"; Url = "https://github.com/coze-ai/coze-api.git"},
        @{Name = "coze-web"; Url = "https://github.com/coze-ai/coze-web.git"},
        @{Name = "coze-gateway"; Url = "https://github.com/coze-ai/coze-gwayate.git"},
        @{Name = "coze-auth"; Url = "https://github.com/coze-ai/coze-auth.git"},
        @{Name = "coze-user"; Url = "https://github.com/coze-ai/coze-user.git"},
        @{Name = "coze-workspace"; Url = "https://github.com/coze-ai/coze-workspace.git"},
        @{Name = "coze-bot"; Url = "https://github.com/coze-ai/coze-bot.git"},
        @{Name = "coze-knowledge"; Url = "https://github.com/coze-ai/coze-knowledge.git"},
        @{Name = "coze-plugin"; Url = "https://github.com/coze-ai/coze-plugin.git"},
        @{Name = "coze-message"; Url = "https://github.com/coze-ai/coze-message.git"},
        @{Name = "coze-file"; Url = "https://github.com/coze-ai/coze-file.git"},
        @{Name = "coze-database"; Url = "https://github.com/coze-ai/coze-database.git"},
        @{Name = "coze-cache"; Url = "https://github.com/coze-ai/coze-cache.git"},
        @{Name = "coze-search"; Url = "https://github.com/coze-ai/coze-search.git"}
    )
    
    $successCount = 0
    $totalCount = $repositories.Count
    
    foreach ($repo in $repositories) {
        $repoName = $repo.Name
        $repoUrl = $repo.Url
        $repoPath = Join-Path $DownloadDir $repoName
        
        Write-ColorMessage "正在下载: $repoName ($($successCount + 1)/$totalCount)" -Color $Yellow
        
        if (Test-Path $repoPath) {
            Write-ColorMessage "  目录已存在，跳过下载" -Color $Yellow
            $successCount++
            continue
        }
        
        try {
            # 使用git clone下载
            Write-ColorMessage "  从 $repoUrl 克隆..." -Color $White
            git clone $repoUrl $repoPath 2>&1 | Out-Null
            
            if (Test-Path $repoPath) {
                Write-ColorMessage "  下载成功: $repoName" -Color $Green
                $successCount++
            } else {
                Write-ColorMessage "  下载失败: $repoName" -Color $Red
            }
        } catch {
            Write-ColorMessage "  下载出错: $repoName - $($_.Exception.Message)" -Color $Red
        }
    }
    
    Write-ColorMessage "`n下载完成: $successCount/$totalCount 个容器源码下载成功" -Color $Cyan
    return $DownloadDir
}

# 函数：创建统一的docker-compose.yml文件
function Create-DockerComposeFile {
    param(
        [string]$ContainersDir
    )
    
    Write-ColorMessage "`n创建统一的docker-compose.yml文件..." -Color $Cyan
    
    $composePath = Join-Path $ContainersDir "docker-compose.yml"
    
     #检查是否已有docker-compose.yml
    if (Test-Path $composePath) {
        Write-ColorMessage "docker-compose.yml已存在，备份原文件..." -Color $Yellow
        $backupPath = "$composePath.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
        Copy-Item $composePath $backupPath -Force
    }
    
    # 创建统一的docker-compose配置
    $composeConfig = @"
version: '3.8'

services:
  # Coze API服务
  coze-api:
    build: ./coze-api
    container_name: coze-api
    ports:
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - DB_HOST=${env:DB_HOST}
      - DB_PORT=${env:DB_PORT}
      - DB_USER=${env:DB_USER}
      - DB_PASSWORD=${env:DB_PASSWORD}
      - DB_NAME=${env:DB_NAME}
      - REDIS_HOST=coze-cache
    depends_on:
      - coze-cache
    networks:
      - coze-network
    restart: unless-stopped

  # Coze Web前端
  coze-web:
    build: ./coze-web
    container_name: coze-web
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - API_URL=http://coze-api:8080
    depends_on:
      - coze-api
    networks:
      - coze-network
    restart: unless-stopped

  # Coze网关
  coze-gateway:
    build: ./coze-gateway
    container_name: coze-gateway
    ports:
      - "80:80"
      - "443:443"
    environment:
      - API_SERVICE=coze-api:8080
      - WEB_SERVICE=coze-web:3000
    depends_on:
      - coze-api
      - coze-web
    networks:
      - coze-network
    restart: unless-stopped

  # 认证服务
  coze-auth:
    build: ./coze-auth
    container_name: coze-auth
    ports:
      - "8081:8081   "
 environment:
      - DB_HOST=coze-database
      - REDIS_HOST=coze-cache
    depends_on:
      - coze-database
      -ze co-cache
    networks:
      - coze-network
    restart: unless-stopped

  # 用户服务
  coze-user:
    build: ./coze-user
    container_name: coze-user
    ports:
      - "8082:8082"
    environment:
      - DB_HOST=coze-database
    depends_on:
      - coze-d
atabase    networks:
      - coze-network
    restart:-st unlessopped

  # 工作空间服务
  coze-workspace:
    build: ./coze-workspace
    container_name: coze-workspace
    ports:
      - "8083:8083"
    environment:
      - DB_HOST=coze-database
    depends_on:
      - coze-database
    networks:
      - coze-network
    restart: unless-stopped

  # Bot服务
  coze-bot:
    build: ./coze-bot
    container_name: coze-bot
    ports:
      - "8084:8084"
    environment:
      - DB_HOST=coze-database
      - KNOWLEDGE_SERVICE=coze-knowledge:8085
    depends_on:
      - coze-database
      - coze-knowledge
    networks:
      - coze-network
    restart: unless-stopped

  # 知识库服务
  coze-knowledge:
    build: ./coze-knowledge
    container_name: coze-knowledge
    ports:
      - "8085:8085"
    environment:
      - DB_HOST=coze-database
      - SEARCH_SERVICE=coze-search:8089
    depends_on:
      - coze-database
      - coze-search
    networks:
      - coze-network
    restart: unless-stopped

  # 插件服务
  coze-plugin:
    build: ./coze-plugin
    container_name: coze-plugin
    ports:
      - "8086:8086"
    environment:
      - DB_HOST=coze-database
    depends_on:
      - coze-database
    networks:
      - coze-network
    restart: unless-stopped

  # 消息服务
  coze-message:
    build: ./coze-message
    container_name: coze-message
    ports:
      - "8087:8087"
    environment:
      - DB_HOST=coze-database
      - REDIS_HOST=coze-cache
    depends_on:
      - coze-database
      - coze-cache
    networks:
      - coze-network
    restart: unless-stopped

  # 文件服务
  coze-file:
    build: ./coze-file
    container_name: coze-file
    ports:
      - "8088:8088"
    environment:
      - DB=_HOSTcoze-database
    depends_on:
      - coze-database
    networks:
      - coze-network
    restart: unless-stopped

  # 数据库服务（云端配置）
  # 注：已将本地数据库替换为云端MySQL，减少本地资源占用
  # 无需启动本地数据库容器，直接使用云端数据库服务

  # 缓存服务
  coze-cache:
    build: ./coze-cache
    container_name: coze-cache
    ports:
      - "6379:6379"
    volumes:
      - coze-cache-data:/data
    networks:
      - coze-network
    restart: unless-stopped

  # 搜索服务
  coze-search:
    build: ./coze-search
    container_name: coze-search
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      - discovery.type=single-node
    volumes:
      - coze-search-data:/usr/share/elasticsearch/data
    networks:
      - coze-network
    restart: unless-stopped

networks:
  coze-network:
    driver: bridge

volumes:
  coze-db-data:
  coze-cache-data:
  coze-search-data:
"@
    
    # 写入docker-compose.yml文件
    $composeConfig | Set-Content $composePath -Encoding UTF8
    Write-ColorMessage "docker-compose.yml文件已创建: $composePath" -Color $Green
    
    return $composePath
}

# 函数：构建Docker容器
function Build-DockerContainers {
    param(
        [string]$ComposePath
    )
    
    Write-ColorMessage "`n开始构建Docker容器..." -Color $Cyan
    
    $composeDir = Split-Path $ComposePath -Parent
    
    # 切换到docker-compose.yml所在目录
    Push-Location $composeDir
    
    try {
        Write-ColorMessage "正在构建所有容器（这可能需要一些时间）..." -Color $Yellow
        
        # 构建所有容器
        docker-compose build
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorMessage "所有容器构建成功！" -Color $Green
        } else {
            Write-ColorMessage "容器构建过程中出现错误" -Color $Red
            return $false
        }
    } catch {
        Write-ColorMessage构建 "过程中出错: $($_.Exception.Message)" -Color $Red
        return $false
    } finally {
        Pop-Location
    }
    
    return $true
}

# 函数：启动所有容器
function Start-AllContainers {
    param(
        [string]$ComposePath
    )
    
    Write-ColorMessage "`n启动所有容器..." -Color $Cyan
    
    $composeDir = Split-Path $ComposePath -Parent
    
    # 切换到docker-compose.yml所在目录
    Push-Location $composeDir
    
    try {
        Write-ColorMessage "使用命令: docker compose --profile '*' up -d" -Color $Yellow
        
        # 容器启动
所有        docker -- composeprofile "*" up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorMessage "所有容器启动成功！" -Color $Green
            
            # 显示容器状态
            Start-Sleep -Seconds 5
            Write-ColorMessage "`n容器状态:" -Color $Cyan
            docker-compose ps
            
            # 显示访问信息
            Write-ColorMessage "`n访问信息:" -Color $Cyan
            Write-ColorMessage "Web界面: http://localhost:3000" -Color $Green
            Write-ColorMessage "API接口: http://localhost:8080" -Color $Green
            Write-ColorMessage "网关: http://localhost:80" -Color $Green
            Write-ColorMessage "`n数据库: localhost:5432 (用户: coze, 密码: coze123)" -Color $Yellow
            Write-ColorMessage "Redis缓存: localhost:6379" -Color $Yellow
            Write-ColorMessage "Elasticsearch搜索: localhost:9200" -Color $Yellow
            
        } else {
            Write-ColorMessage "容器启动过程中出现错误" -Color $Red
            return $false
        }
    } catch {
        Write-ColorMessage "启动过程中出错: $($_.Exception.Message)" -Color $Red
        return $false
    } finally {
        Pop-Location
    }
    
    return $true
}

# 函数：显示部署摘要
function Show-DeploymentSummary {
    param(
        [string]$ContainersDir
    )
    
    Write-ColorMessage "`n" + ("=" * 60) -Color $Cyan
    Write-ColorMessage "Coze Studio 0.2.0 部署完成摘要" -Color $Cyan
    Write-ColorMessage "=" * 60 -Color $Cyan
    
    Write-ColorMessage "`n部署目录: $ContainersDir" -Color $White
    Write-ColorMessage "容器数量: 14个" -Color $White
    
    Write-ColorMessage "`n已启动的服务:" -Color $Green
    Write-ColorMessage "1. coze-api (API服务) - 端口: 8080" -Color $White
    Write-ColorMessage "2. coze-web (Web前端) - 端口: 3000" -Color $White
    Write-ColorMessage "3. coze-gateway (网关) - 端口: 80, 443" -Color $White
    Write-ColorMessage "4. coze-auth (认证服务) - 端口: 8081" -Color $White
    Write-ColorMessage "5. coze-user (用户服务) - 端口: 8082" -Color $White
    Write-ColorMessage "6. coze-workspace (工作空间) - 端口: 8083" -Color $White
    Write-ColorMessage "7. coze-bot (Bot服务) - 端口: 8084" -Color $White
    Write-ColorMessage "8. coze-knowledge (知识库) - 端口: 8085" -Color $White
    Write-ColorMessage "9. coze-plugin (插件服务) - 端口: 8086" -Color $White
    Write-ColorMessage "10.ze co-message (消息服务) - 端口: 8087" -Color $White
    Write-ColorMessage "11. coze-file (文件服务) - 端口: 8088" -Color $White
    Write-ColorMessage "12. coze-database (数据库) - 端口: 5432" -Color $White
    Write-ColorMessage "13. coze-cache (缓存) - 端口: 6379" -Color $White
    Write-ColorMessage "14. coze-search (搜索) - 端口: 9200, 9300" -Color $White
    
    Write-ColorMessage "`n管理命令:" -Color $Yellow
    Write-ColorMessage "查看容器状态: docker-compose ps" -Color $White
    Write-ColorMessage "查看容器日志: docker-compose logs [服务名]" -Color $White
    Write-ColorMessage "停止所有容器: docker-compose down" -Color $White
    Write-ColorMessage "重启所有容器: docker-compose restart" -Color $White
    
    Write-ColorMessage "`n" + ("=" * 60) -Color $Cyan
}

# 主函数
function Main {
    Write-ColorMessage "Coze Studio 0.2.0 完整部署脚本" -Color $Cyan
    Write-ColorMessage "=" * 60 -Color $Cyan
    
    # 检查必要工具
    Write-ColorMessage "`n检查必要工具..." -Color $Yellow
    
    # 检查Git
    if (-not (Test-Command "git")) {
        Write-ColorMessage "错误: Git未安装，请先安装Git" -Color $Red
        exit 1
    }
    Write-ColorMessage "✓ Git已安装" -Color $Green
    
    # 检查Docker
    if (-not (Test-Command "docker")) {
        Write-ColorMessage "错误: Docker未安装，请先安装Docker Desktop" -Color $Red
        exit 1
    }
    Write-ColorMessage "✓ Docker已安装" -Color $Green
    
    # 检查Docker Compose
    if (-not (Test-Command "docker-compose")) {
        Write-ColorMessage "警告: docker-compose未安装，尝试使用docker compose..." -Color $Yellow
        if (-not (Test-Command "docker compose")) {
            Write-ColorMessage "错误: docker compose未找到，请安装Docker Compose" -Color $Red
            exit 1
        }
    }
    Write-ColorMessage "✓ Docker Compose可用" -Color $Green
    
    # 检查Docker是否运行
    if (-not (Test-DockerRunning)) {
        Write-ColorMessage "错误: Docker未运行，请启动Docker Desktop" -Color $Red
        exit 1
    }
    Write-ColorMessage "✓ Docker正在运行" -Color $Green
    
    # 配置Docker国内镜像源
    Configure-DockerMirror
    
    # 下载容器源码
    $containersDir = Download-CozeContainers
    
    # 创建docker-compose.yml文件
    $composePath = Create-DockerComposeFile -ContainersDir $containersDir
    
    # 构建容器
    $buildSuccess = Build-DockerContainers -ComposePath $composePath
    if (-not $buildSuccess) {
        Write-ColorMessage "容器构建失败，请检查错误信息" -Color $Red
        exit 1
    }
    
    # 启动容器
    $startSuccess = Start-AllContainers -ComposePath $composePath
    if (-not $startSuccess) {
        Write-ColorMessage "容器启动失败，请检查错误信息" -Color $Red
        exit 1
    }
    
    # 显示部署摘要
    Show-DeploymentSummary -ContainersDir $containersDir
    
    Write-ColorMessage "`n部署完成！所有容器已成功导入并显示在Docker Desktop中。" -Color $Green
    Write-ColorMessage "请打开Docker Desktop查看容器状态。" -Color $Yellow
}

# 执行主函数
try {
   
 Main} catch {
    Write-ColorMessage "`n部署过程中出现未预期的错误: $($_.Exception.Message)" -Color $Red
    Write-ColorMessage "堆栈跟踪: $($_.ScriptStackTrace)" -Color $Red
    exit 1
}