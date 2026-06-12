# Install Python packages on D: drive only — keeps C: free
# Usage: .\scripts\setup_venv.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# Redirect pip cache, temp, and user site-packages away from C:
$env:PIP_CACHE_DIR = "D:\pip-cache"
$env:TEMP = "D:\temp"
$env:TMP = "D:\temp"
$env:TMPDIR = "D:\temp"
$env:PYTHONUSERBASE = "D:\python-user"
$env:TORCH_HOME = "D:\torch-cache"
$env:HF_HOME = "D:\hf-cache"

New-Item -ItemType Directory -Force -Path $env:PIP_CACHE_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
New-Item -ItemType Directory -Force -Path $env:PYTHONUSERBASE | Out-Null

Set-Location $ProjectRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment at $ProjectRoot\.venv ..."
    python -m venv .venv
}

Write-Host "Installing dependencies into project .venv (D: drive) ..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip
# CPU-only PyTorch — smaller and faster on laptops without NVIDIA GPU
.\.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host "Done. Activate with: .\.venv\Scripts\Activate.ps1"
