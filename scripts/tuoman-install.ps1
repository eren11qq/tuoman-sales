<#
.SYNOPSIS
  拓漫 TouMan — 一键安装脚本
  用法: iex (irm https://raw.githubusercontent.com/eren11qq/tuoman-sales/main/scripts/tuoman-install.ps1)
#>

param(
    [string]$InstallDir = "$env:LOCALAPPDATA\tuoman",
    [switch]$SkipSetup
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()

Write-Host @"

  ╔══════════════════════════════════════════╗
  ║      拓漫 TouMan — 一键安装             ║
  ║   AI漫剧行业智能获客Agent               ║
  ╚══════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ─── 检测 Python ─────────────────────────────────────────────────────────────

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host ">> 正在安装 Python 3.11..." -ForegroundColor Yellow
    try {
        winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
        refreshenv
        $python = Get-Command python -ErrorAction SilentlyContinue
    } catch {
        Write-Host ""
    }
    if (-not $python) {
        Write-Host "!! 未检测到 Python" -ForegroundColor Red
        Write-Host "!! 请手动安装: https://www.python.org/downloads/" -ForegroundColor Red
        Write-Host "!! 安装后重新运行此命令" -ForegroundColor Red
        exit 1
    }
}

$ver = python --version 2>&1
Write-Host ">> 检测到: $ver" -ForegroundColor Green

# ─── 检测 Git ─────────────────────────────────────────────────────────────────

$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host ">> 正在安装 Git..." -ForegroundColor Yellow
    try {
        winget install Git.Git --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
        refreshenv
        $git = Get-Command git -ErrorAction SilentlyContinue
    } catch {
        Write-Host ""
    }
    if (-not $git) {
        Write-Host "!! 请手动安装 Git: https://git-scm.com/download/win" -ForegroundColor Red
        exit 1
    }
}

# ─── 克隆仓库 ────────────────────────────────────────────────────────────────

if (Test-Path $InstallDir) {
    Write-Host ">> 目录已存在，更新中..." -ForegroundColor Yellow
    Push-Location $InstallDir
    git pull
} else {
    Write-Host ">> 正在下载 拓漫 TouMan..." -ForegroundColor Yellow
    git clone --depth 1 https://github.com/eren11qq/tuoman-sales.git $InstallDir
    Push-Location $InstallDir
}

# ─── 创建虚拟环境 + 安装核心依赖 ──────────────────────────────────────────────

if (-not (Test-Path "$InstallDir\.venv")) {
    Write-Host ">> 创建虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host ">> 安装依赖（首次约 2-3 分钟）..." -ForegroundColor Yellow
& "$InstallDir\.venv\Scripts\python.exe" -m pip install --upgrade pip --quiet 2>&1 | Out-Null

# 先安装包本身
& "$InstallDir\.venv\Scripts\python.exe" -m pip install -e "$InstallDir" --quiet 2>&1
if ($LASTEXITCODE -ne 0) {
    & "$InstallDir\.venv\Scripts\python.exe" -m pip install -e "$InstallDir" 2>&1
}

# 再装核心依赖
& "$InstallDir\.venv\Scripts\python.exe" -m pip install pyyaml httpx rich prompt-toolkit python-dotenv tzlocal jinja2 --quiet 2>&1

# ─── 加入 PATH 提示 ─────────────────────────────────────────────────────────

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$venvPath = "$InstallDir\.venv\Scripts"
if ($userPath -notlike "*$venvPath*") {
    try {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$venvPath", "User")
        Write-Host ">> 已添加到 PATH，重启终端后可直接运行 tuoman" -ForegroundColor Green
    } catch {
        Write-Host ">> PATH 添加失败，手动将以下目录加入 PATH：$venvPath" -ForegroundColor Gray
    }
}

# ─── .env配置引导 ──────────────────────────────────────────────────────────

$envPath = "$env:LOCALAPPDATA\hermes\.env"
if (-not (Test-Path $envPath)) {
    Write-Host @"

  ⚠  还需要配置 API Key

  创建文件: $envPath
  写入内容（至少一个）:

  OPENAI_API_KEY=sk-你的key
  DEEPSEEK_API_KEY=sk-你的key

"@ -ForegroundColor Yellow
}

# ─── 完成 ────────────────────────────────────────────────────────────────────

Pop-Location

Write-Host @"

  ✅ 拓漫 TouMan 安装成功！

  启动方式：
  直接在终端运行：
     tuoman

  如果 tuoman 命令找不到，运行：
     cd $InstallDir
     .venv\Scripts\python cli.py

  首次启动需配置 API Key（见上方说明）

"@ -ForegroundColor Green
