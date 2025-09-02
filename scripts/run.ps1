<#
scripts/run.ps1
Activate the project's .venv and start the FastAPI app using uvicorn.
Run from project root:

  .\scripts\run.ps1    # runs in this PowerShell session

If you want the venv to stay active in your session, first dot-source the init script:
  . .\scripts\init_venv.ps1
  # then run this script (it will also activate the venv)
  .\scripts\run.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path -Path (Join-Path $scriptDir '..')
$venvDir = Join-Path $projectRoot '.venv'

if (-not (Test-Path $venvDir)) {
    Write-Error ".venv not found at $venvDir. Run scripts\init_venv.ps1 first."
    exit 1
}

$activateScript = Join-Path $venvDir 'Scripts\Activate.ps1'
if (-not (Test-Path $activateScript)) {
    Write-Error "Activate.ps1 not found in $venvDir."
    exit 1
}

# Activate venv in this session
. $activateScript

$hostAddr = '127.0.0.1'
if ($env:HOST) { $hostAddr = $env:HOST }

$portNum = '8000'
if ($env:PORT) { $portNum = $env:PORT }

$reloadFlag = 'true'
if ($env:RELOAD) { $reloadFlag = $env:RELOAD }

Write-Host "Starting app on $($hostAddr):$($portNum) (reload=$($reloadFlag))"
if ($reloadFlag -eq 'true' -or $reloadFlag -eq '1') {
  & uvicorn app.main:app --host $hostAddr --port $portNum --reload
} else {
  & uvicorn app.main:app --host $hostAddr --port $portNum
}
