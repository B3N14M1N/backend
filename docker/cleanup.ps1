<#
scripts/cleanup.ps1
Clean up Docker containers, images, and volumes for the backend project.
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

# Stop and remove containers
Write-Host "Stopping and removing containers..." -ForegroundColor Yellow
try {
    Invoke-Expression "$dockerComposeCmd down -v --remove-orphans"
    Write-Host "Containers stopped and removed." -ForegroundColor Green
} catch {
    Write-Host "Failed to stop containers: $_" -ForegroundColor Red
}

Write-Host ""

# Ask about removing images
$removeImages = Read-Host "Do you want to remove the Docker images? (y/N)"
if ($removeImages -eq 'y' -or $removeImages -eq 'Y') {
    Write-Host "Removing project images..." -ForegroundColor Yellow
    try {
        Invoke-Expression "$dockerComposeCmd down --rmi all"
        Write-Host "Project images removed." -ForegroundColor Green
    } catch {
        Write-Host "Failed to remove project images: $_" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "Removing unused images..." -ForegroundColor Yellow
    try {
        docker image prune -f
        Write-Host "Unused images removed." -ForegroundColor Green
    } catch {
        Write-Host "Failed to prune images: $_" -ForegroundColor Red
    }
} else {
    Write-Host "Skipping image removal." -ForegroundColor Blue
}

Write-Host ""
Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host "Resources freed up." -ForegroundColor Cyan
