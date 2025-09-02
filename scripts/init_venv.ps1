<#
scripts/init_venv.ps1
Create a virtual environment (.venv) and install requirements.txt using PowerShell.
Run this script from the project root (or dot-source it to keep the venv activated in your session):

  # from project root
  .\scripts\init_venv.ps1

  # to keep .venv activated in the current session
  . .\scripts\init_venv.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path -Path (Join-Path $scriptDir '..')
$venvDir = Join-Path $projectRoot '.venv'

# Find python executable
$pythonCmd = $null
$cmd = Get-Command python -ErrorAction SilentlyContinue
if ($cmd -ne $null) {
    # CommandInfo.Source contains the path to the module/file that provided the command.
    # For executables the Path property is more reliable.
    if ($cmd.Path) { $pythonCmd = $cmd.Path } elseif ($cmd.Source) { $pythonCmd = $cmd.Source }
}
if (-not $pythonCmd) {
    $cmd = Get-Command python3 -ErrorAction SilentlyContinue
    if ($cmd -ne $null) {
        if ($cmd.Path) { $pythonCmd = $cmd.Path } elseif ($cmd.Source) { $pythonCmd = $cmd.Source }
    }
}
if (-not $pythonCmd) {
    Write-Error "Python not found. Install Python 3.8+ and ensure 'python' or 'python3' is on PATH."
    exit 1
}

if (-not (Test-Path $venvDir)) {
    Write-Host "Creating virtual environment at $venvDir using $pythonCmd"
    & $pythonCmd -m venv $venvDir
} else {
    Write-Host "Virtual environment already exists at $venvDir"
}

$activateScript = Join-Path $venvDir 'Scripts\Activate.ps1'
if (-not (Test-Path $activateScript)) {
    Write-Error "Could not find Activate.ps1 in $venvDir (venv may not have been created)."
    exit 1
}

# Dot-source activation to affect current session when this file is dot-sourced.
. $activateScript

Write-Host "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip

$reqFile = Join-Path $projectRoot 'requirements.txt'
if (-not (Test-Path $reqFile)) {
    Write-Error "requirements.txt not found in project root: $projectRoot"
    exit 1
}

pip install -r $reqFile
Write-Host "Virtual environment ready. To activate in a new session: . $venvDir\Scripts\Activate.ps1"
