<#
scripts/setup/run.ps1
Docker Compose management script for the backend application.

Commands:
  run.ps1                 - Build images (using cache) and recreate containers
  run.ps1 -Rebuild        - Stop containers, remove volumes, rebuild images, start fresh
  run.ps1 -Start          - Recreate containers only (no build, use existing images)
  run.ps1 -Build          - Rebuild only the api image and recreate api container (for code changes)
  -NoCache                - Disable build cache (force rebuild from scratch)

Examples:
  .\run.ps1               # Quick restart with cached build
  .\run.ps1 -Rebuild      # Full clean rebuild (with cache)
  .\run.ps1 -Start        # Quick container restart (no build)
  .\run.ps1 -Build        # Rebuild api only (with cache)
  .\run.ps1 -Rebuild -NoCache  # Full rebuild without cache (when dependencies change)

Based on template from previous project.
#>

Param(
    [switch]$Rebuild,
    [switch]$Start,
    [switch]$Build,
    [switch]$NoCache
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
# -Rebuild: remove containers + volumes, build, recreate everything
# -Start: recreate containers only (no build)
# -Build: rebuild only the api image and recreate api container
# -NoCache: disable build cache
# no switch: build (using cache) and recreate containers

try {
    if ($Rebuild) {
        Write-Host "REBUILD requested: stopping and removing containers + volumes" -ForegroundColor Yellow
        Invoke-Expression "$dockerComposeCmd down -v --remove-orphans"
        Write-Host "Removed containers and volumes" -ForegroundColor Green

        # Remove existing alembic versions to avoid conflicts during rebuild
        Write-Host "Removing existing alembic versions..." -ForegroundColor Yellow
        if (Test-Path "alembic/versions") {
            Remove-Item -Recurse -Force "alembic/versions"
            Write-Host "Alembic versions removed." -ForegroundColor Green
        } else {
            Write-Host "No alembic versions directory found." -ForegroundColor Gray
        }

        Write-Host "Building Docker images..." -ForegroundColor Yellow
        $buildCmd = "$dockerComposeCmd build"
        if ($NoCache) { $buildCmd += " --no-cache" }
        $buildCmd += " api"
        Invoke-Expression $buildCmd
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
    } elseif ($Build) {
        Write-Host "BUILD requested: rebuilding api image and recreating api container only" -ForegroundColor Yellow
        
        # Stop only the api container
        Invoke-Expression "$dockerComposeCmd stop api"
        if ($LASTEXITCODE -ne 0) { throw "docker compose stop api failed with exit code $LASTEXITCODE" }

        # Rebuild only the api service
        Write-Host "Building api image..." -ForegroundColor Yellow
        $buildCmd = "$dockerComposeCmd build"
        if ($NoCache) { $buildCmd += " --no-cache" }
        $buildCmd += " api"
        Invoke-Expression $buildCmd
        if ($LASTEXITCODE -ne 0) { throw "docker compose build api failed with exit code $LASTEXITCODE" }

        # Start the api container (this will recreate it with the new image)
        Write-Host "Starting api container..." -ForegroundColor Yellow
        Invoke-Expression "$dockerComposeCmd up -d api"
        if ($LASTEXITCODE -ne 0) { throw "docker compose up api failed with exit code $LASTEXITCODE" }

        Write-Host "API image rebuilt and container recreated." -ForegroundColor Green
    } else {
        Write-Host "Default action: rebuild images (using cache) and recreate containers" -ForegroundColor Yellow

        Write-Host "Building Docker images..." -ForegroundColor Yellow
        $buildCmd = "$dockerComposeCmd build"
        if ($NoCache) { $buildCmd += " --no-cache" }
        $buildCmd += " api"
        Invoke-Expression $buildCmd
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