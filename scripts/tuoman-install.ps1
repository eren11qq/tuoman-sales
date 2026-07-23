<#
.SYNOPSIS
  拓漫 TouMan — 一键安装脚本
  用法: iex (irm https://你的域名/tuoman-install.ps1)
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

# ─── 检测或安装 Python ───────────────────────────────────────────────────────

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host ">> 正在安装 Python 3.11..." -ForegroundColor Yellow
    winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements
    refreshenv
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        Write-Host "!! 请手动安装 Python 3.11: https://www.python.org/downloads/" -ForegroundColor Red
        exit 1
    }
}

$ver = python --version 2>&1
Write-Host ">> 检测到: $ver" -ForegroundColor Green

# ─── 克隆仓库 ────────────────────────────────────────────────────────────────

if (Test-Path $InstallDir) {
    Write-Host ">> 目录已存在，更新中..." -ForegroundColor Yellow
    Set-Location $InstallDir
    git pull
} else {
    Write-Host ">> 克隆 拓漫 TouMan..." -ForegroundColor Yellow
    git clone https://github.com/eren11qq/tuoman-sales.git $InstallDir
    Set-Location $InstallDir
}

# ─── 创建虚拟环境 + 安装依赖 ──────────────────────────────────────────────────

if (-not (Test-Path "$InstallDir\.venv")) {
    Write-Host ">> 创建虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host ">> 安装依赖..." -ForegroundColor Yellow
& "$InstallDir\.venv\Scripts\pip.exe" install --upgrade pip
& "$InstallDir\.venv\Scripts\pip.exe" install -e . 2>&1 | Out-Null

# ─── 创建快捷方式 ────────────────────────────────────────────────────────────

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\拓漫.lnk")
$Shortcut.TargetPath = "$InstallDir\.venv\Scripts\python.exe"
$Shortcut.Arguments = "$InstallDir\cli.py"
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Save()

# ─── 创建配置文件引导 ────────────────────────────────────────────────────────

if (-not (Test-Path "$env:LOCALAPPDATA\hermes\.env")) {
    Write-Host @"

  下一步：配置 API Key

  在以下位置创建 .env 文件：
  $env:LOCALAPPDATA\hermes\.env

  写入你的 API Key，例如：
  OPENAI_API_KEY=sk-...
  DEEPSEEK_API_KEY=sk-...

"@ -ForegroundColor Yellow
}

# ─── 完成 ────────────────────────────────────────────────────────────────────

Write-Host @"

  ✅ 安装完成！

  启动方式：
  ① 双击桌面「拓漫」图标
  ② 或在命令行运行：
     cd $InstallDir
     .venv\Scripts\python cli.py

  详细文档：https://github.com/eren11qq/tuoman-sales

"@ -ForegroundColor Green
