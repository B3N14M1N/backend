<#
scripts/rebuild.ps1
Stop and remove running containers, remove images, rebuild, and run via Docker Compose.
Based on template from previous project.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Function to check if Docker is running
function Test-DockerRunning {
    Write-Host "Checking if Docker is running..." -ForegroundColor Blue
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        docker info > $null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Docker is running." -ForegroundColor Green
            return $true
        } else {
            Write-Host "Docker info failed with exit code $LASTEXITCODE" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "Error checking Docker: $_" -ForegroundColor Red
        return $false
    } finally {
        $ErrorActionPreference = $oldPreference
    }
}

# Function to get docker compose command
function Get-DockerComposeCommand {
    Write-Host "Detecting Docker Compose command..." -ForegroundColor Blue
    # Try docker compose (v2)
    try {
        Write-Host "Trying 'docker compose version'..." -ForegroundColor Gray
        $null = docker compose version 2>$null
        Write-Host "Found 'docker compose' (v2)" -ForegroundColor Green
        return "docker compose"
    } catch {
        Write-Host "'docker compose' not found: $_" -ForegroundColor Yellow
        # Try docker-compose (v1)
        try {
            Write-Host "Trying 'docker-compose --version'..." -ForegroundColor Gray
            $null = docker-compose --version 2>$null
            Write-Host "Found 'docker-compose' (v1)" -ForegroundColor Green
            return "docker-compose"
        } catch {
            Write-Host "'docker-compose' not found: $_" -ForegroundColor Red
            return $null
        }
    }
}

if (-not (Test-DockerRunning)) {
    Write-Error "Docker daemon is not accessible. Please ensure Docker (Desktop or Rancher Desktop) is running and the docker command is available in PATH, then try again."
    exit 1
}

$dockerComposeCmd = Get-DockerComposeCommand
if (-not $dockerComposeCmd) {
    Write-Error "Docker Compose is not available. Please install Docker Compose or ensure it's included with your Docker setup."
    exit 1
}

Write-Host "Using Docker Compose command: $dockerComposeCmd" -ForegroundColor Blue

Write-Host ""
Write-Host "Cleaning up existing containers..." -ForegroundColor Yellow

# Stop and remove all running containers for this project
try {
    Invoke-Expression "$dockerComposeCmd down -v --remove-orphans"
    Write-Host "Stopped and removed existing containers" -ForegroundColor Green
} catch {
    Write-Host "No existing containers to clean up or failed to stop: $_" -ForegroundColor Blue
}

Write-Host ""
Write-Host "Removing images..." -ForegroundColor Yellow
try {
    Invoke-Expression "$dockerComposeCmd rm --force"
    Write-Host "Removed images" -ForegroundColor Green
} catch {
    Write-Host "Failed to remove images: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Building Docker images..." -ForegroundColor Yellow
try {
    Invoke-Expression "$dockerComposeCmd build --no-cache"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Docker images built successfully" -ForegroundColor Green
    } else {
        Write-Host "Failed to build Docker images" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error building images: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting containers..." -ForegroundColor Yellow
try {
    Invoke-Expression "$dockerComposeCmd up -d"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Containers started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Your backend is running at: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
    } else {
        Write-Host "Failed to start containers" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error starting containers: $_" -ForegroundColor Red
    exit 1
}
