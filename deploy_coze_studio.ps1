# Coze Studio 自动部署脚本
# 请在项目根目录下运行此脚本

Write-Host "========================================="
Write-Host "Coze Studio Deployment Script"
Write-Host "========================================="

# Get current directory
$currentDir = Get-Location

# Check Docker availability
Write-Host "Checking Docker availability..."
docker version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker is not running! Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check Docker Compose
Write-Host "Checking Docker Compose..."
docker-compose version
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Compose is not installed or configured correctly!" -ForegroundColor Red
    exit 1
}

# Define docker directory path
$dockerDir = Join-Path -Path $currentDir -ChildPath "coze-studio-0.2.0\docker"
Write-Host "Docker directory: $dockerDir"

# Check if docker directory exists
if (-not (Test-Path -Path $dockerDir)) {
    Write-Host "Docker directory not found! Please run this script from the project root directory." -ForegroundColor Red
    exit 1
}

# Enter docker directory
Write-Host "Entering docker directory..."
Set-Location -Path $dockerDir

# Ensure .env file exists
$envFile = Join-Path -Path $dockerDir -ChildPath ".env"
$envExampleFile = Join-Path -Path $dockerDir -ChildPath ".env.example"
if (-not (Test-Path -Path $envFile)) {
    Write-Host ".env file not found, creating from .env.example..."
    if (Test-Path -Path $envExampleFile) {
        Copy-Item -Path $envExampleFile -Destination $envFile -Force
    } else {
        Write-Host ".env.example file not found! Please check your project structure." -ForegroundColor Red
        exit 1
    }
}

# Start middleware services
Write-Host "========================================="
Write-Host "Starting middleware services..."
Write-Host "========================================="
docker-compose --profile middleware up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start middleware services!" -ForegroundColor Red
    exit 1
}

# Wait for services to start
Write-Host "Waiting for services to start... (15 seconds)"
Start-Sleep -Seconds 15

# Check middleware services status
Write-Host "========================================="
Write-Host "Checking middleware services status..."
Write-Host "========================================="
docker-compose --profile middleware ps

# Start mysql-setup services
Write-Host "========================================="
Write-Host "Starting mysql-setup services..."
Write-Host "========================================="
docker-compose --profile mysql-setup up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start mysql-setup services!" -ForegroundColor Red
    exit 1
}

# Wait for mysql-setup to complete
Write-Host "Waiting for mysql-setup to complete... (30 seconds)"
Start-Sleep -Seconds 30

# Check mysql-setup services status
Write-Host "========================================="
Write-Host "Checking mysql-setup services status..."
Write-Host "========================================="
docker-compose --profile mysql-setup ps

# Start run-server services
Write-Host "========================================="
Write-Host "Starting run-server services..."
Write-Host "========================================="
docker-compose --profile run-server up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start run-server services!" -ForegroundColor Red
    exit 1
}

# Wait for run-server to start
Write-Host "Waiting for run-server to start... (20 seconds)"
Start-Sleep -Seconds 20

# Check all services status
Write-Host "========================================="
Write-Host "Checking all services status..."
Write-Host "========================================="
docker-compose ps

Write-Host "========================================="
Write-Host "Coze Studio deployment completed!" -ForegroundColor Green
Write-Host "========================================="
Write-Host "Service access address: http://localhost:8888"
Write-Host "View logs command: docker-compose logs -f"
Write-Host "Stop services command: docker-compose down"
Write-Host "========================================="