# Start Flask web app on port 8000 — all temp/cache on D: drive
# Usage: .\scripts\start_web_app.ps1
# (Jenkins :8088 and MLflow :5000 stay as you already run them)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

$env:PIP_CACHE_DIR = "D:\pip-cache"
$env:TEMP = "D:\temp"
$env:TMP = "D:\temp"
$env:TMPDIR = "D:\temp"
$env:PYTHONUSERBASE = "D:\python-user"
$env:TORCH_HOME = "D:\torch-cache"
$env:HF_HOME = "D:\hf-cache"

# Fast local testing — skip per-request MLflow HTTP calls (set "true" to log predictions)
$env:MLFLOW_LOG_PREDICTIONS = "false"
$env:MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
$env:FLASK_DEBUG = "false"

Set-Location $ProjectRoot

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "No .venv found. Run .\scripts\setup_venv.ps1 first."
    exit 1
}

Write-Host "Starting web app at http://127.0.0.1:8000 (MLFLOW_LOG_PREDICTIONS=false for speed)"
& $python web_app.py
