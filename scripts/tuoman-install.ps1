<#
.SYNOPSIS
  拓漫 TouMan — 一键安装
  用法: iex (irm https://raw.githubusercontent.com/eren11qq/tuoman-sales/main/scripts/tuoman-install.ps1)
#>

param([string]$InstallDir = "$env:LOCALAPPDATA\tuoman")

$ProgressPreference = "SilentlyContinue"
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()

Write-Host ">> 拓漫 TouMan 安装中..." -ForegroundColor Cyan

# Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host ">> 安装 Python..." -ForegroundColor Yellow
    winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
    refreshenv
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) { Write-Host "!! 请装 Python 3.11" -ForegroundColor Red; Read-Host; exit 1 }
}
Write-Host "$(python --version 2>&1)" -ForegroundColor Green

# Git
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host ">> 安装 Git..." -ForegroundColor Yellow
    winget install Git.Git --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
    refreshenv
    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) { Write-Host "!! 请装 Git" -ForegroundColor Red; Read-Host; exit 1 }
}

# Clone
if (Test-Path $InstallDir) {
    Set-Location $InstallDir; git pull
} else {
    git clone --depth 1 https://github.com/eren11qq/tuoman-sales.git $InstallDir
    Set-Location $InstallDir
}

# Venv
if (-not (Test-Path ".venv")) { python -m venv .venv }

# Deps
Write-Host ">> 安装依赖..." -ForegroundColor Yellow
.venv\Scripts\python -m pip install --upgrade pip --quiet 2>$null
.venv\Scripts\python -m pip install -e "." --quiet 2>$null
.venv\Scripts\python -m pip install pyyaml httpx rich prompt-toolkit python-dotenv tzlocal jinja2 requests tiktoken openai --quiet 2>$null

# PATH
$venvPath = "$InstallDir\.venv\Scripts"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$venvPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$venvPath", "User")
}

# .env
$envPath = "$env:LOCALAPPDATA\hermes\.env"
if (-not (Test-Path $envPath)) {
    Write-Host "`n配置 API Key: $envPath" -ForegroundColor Yellow
}

Write-Host "`nOK! 终端运行: tuoman" -ForegroundColor Green
