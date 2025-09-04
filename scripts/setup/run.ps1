<#
scripts/rebuild.ps1
Stop and remove running containers, remove images, rebuild, and run via Docker Compose.
Based on template from previous project.
#>

Param(
    [switch]$Rebuild,
    [switch]$Start
)

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
Write-Host "Preparing Docker Compose actions..." -ForegroundColor Yellow

# Decide action based on switches:
# -Rebuild: remove containers + volumes, build with --no-cache, recreate everything
# -Start: recreate containers only (no build)
# no switch: build (using cache) and recreate containers

try {
    if ($Rebuild) {
        Write-Host "REBUILD requested: stopping and removing containers + volumes" -ForegroundColor Yellow
        Invoke-Expression "$dockerComposeCmd down -v --remove-orphans"
        Write-Host "Removed containers and volumes" -ForegroundColor Green

        Write-Host "Building Docker images (no cache) ..." -ForegroundColor Yellow
        Invoke-Expression "$dockerComposeCmd build --no-cache"
        if ($LASTEXITCODE -ne 0) { throw "docker compose build failed with exit code $LASTEXITCODE" }

        Write-Host "Starting containers..." -ForegroundColor Yellow
        Invoke-Expression "$dockerComposeCmd up -d"
        if ($LASTEXITCODE -ne 0) { throw "docker compose up failed with exit code $LASTEXITCODE" }

        Write-Host "Rebuild complete: images, containers and volumes recreated." -ForegroundColor Green
    } elseif ($Start) {
        Write-Host "START requested: recreating containers only (no build, no volume removal)" -ForegroundColor Yellow
        # Force recreate containers using existing images
        Invoke-Expression "$dockerComposeCmd up -d --force-recreate --remove-orphans"
        if ($LASTEXITCODE -ne 0) { throw "docker compose up failed with exit code $LASTEXITCODE" }

        Write-Host "Containers recreated." -ForegroundColor Green
    } else {
        Write-Host "Default action: rebuild images (using cache) and recreate containers" -ForegroundColor Yellow

        Write-Host "Building Docker images (use cache) ..." -ForegroundColor Yellow
        Invoke-Expression "$dockerComposeCmd build"
        if ($LASTEXITCODE -ne 0) { throw "docker compose build failed with exit code $LASTEXITCODE" }

        Write-Host "Starting containers (force recreate) ..." -ForegroundColor Yellow
        Invoke-Expression "$dockerComposeCmd up -d --force-recreate --remove-orphans"
        if ($LASTEXITCODE -ne 0) { throw "docker compose up failed with exit code $LASTEXITCODE" }

        Write-Host "Images built and containers recreated." -ForegroundColor Green
    }

    Write-Host ""; Write-Host "Your backend is running at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API docs at: http://localhost:8000/docs" -ForegroundColor Cyan

} catch {
    Write-Host "Error during requested action: $_" -ForegroundColor Red
    exit 1
}
