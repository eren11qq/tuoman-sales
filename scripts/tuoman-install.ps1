<#
.SYNOPSIS
  拓漫 TouMan — 一键安装
  用法: iex (irm https://raw.githubusercontent.com/eren11qq/tuoman-sales/main/scripts/tuoman-install.ps1)
#>

param(
    [string]$InstallDir = "$env:LOCALAPPDATA\tuoman"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()

Write-Host ">> 拓漫 TouMan 安装中..." -ForegroundColor Cyan

# Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host ">> 安装 Python 3.11..." -ForegroundColor Yellow
    try { winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null; refreshenv; $python = Get-Command python -ErrorAction SilentlyContinue } catch {}
    if (-not $python) { Write-Host "!! 请安装 Python 3.11" -ForegroundColor Red; exit 1 }
}
Write-Host ">> $(python --version)" -ForegroundColor Green

# Git
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host ">> 安装 Git..." -ForegroundColor Yellow
    try { winget install Git.Git --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null; refreshenv; $git = Get-Command git -ErrorAction SilentlyContinue } catch {}
    if (-not $git) { Write-Host "!! 请安装 Git" -ForegroundColor Red; exit 1 }
}

# Clone
if (Test-Path $InstallDir) { Push-Location $InstallDir; git pull } else { git clone --depth 1 https://github.com/eren11qq/tuoman-sales.git $InstallDir; Push-Location $InstallDir }

# Venv
if (-not (Test-Path "$InstallDir\.venv")) { python -m venv .venv }

# Dependencies
Write-Host ">> 安装依赖..." -ForegroundColor Yellow
& "$InstallDir\.venv\Scripts\python.exe" -m pip install --upgrade pip --quiet 2>&1 | Out-Null
& "$InstallDir\.venv\Scripts\python.exe" -m pip install -e "$InstallDir" --quiet 2>&1
if ($LASTEXITCODE -ne 0) { & "$InstallDir\.venv\Scripts\python.exe" -m pip install -e "$InstallDir" 2>&1 }
& "$InstallDir\.venv\Scripts\python.exe" -m pip install pyyaml httpx rich prompt-toolkit python-dotenv tzlocal jinja2 --quiet 2>&1

# PATH
$venvPath = "$InstallDir\.venv\Scripts"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$venvPath*") {
    try { [Environment]::SetEnvironmentVariable("Path", "$userPath;$venvPath", "User") } catch {}
}

# .env提示
$envPath = "$env:LOCALAPPDATA\hermes\.env"
if (-not (Test-Path $envPath)) {
    Write-Host "`n配置 API Key: $envPath" -ForegroundColor Yellow
}

Pop-Location
Write-Host "`nOK! 终端运行: tuoman" -ForegroundColor Green
