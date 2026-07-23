<#
.SYNOPSIS
  拓漫 TouMan — PyInstaller 打包脚本
  用法: .\scripts\build_exe.ps1
  输出: dist\拓漫.exe
#>

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host @"

  ╔══════════════════════════════════════════╗
  ║    拓漫 TouMan — 打包 .exe             ║
  ╚══════════════════════════════════════════╝

"@ -ForegroundColor Cyan

Set-Location $ProjectRoot

# 检查 PyInstaller
$pyi = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyi) {
    Write-Host ">> 安装 PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# 检查虚拟环境
if (-not (Test-Path ".venv")) {
    Write-Host ">> 创建虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
    & ".venv\Scripts\pip.exe" install -e .
}

Write-Host ">> 打包中（约 2-5 分钟）..." -ForegroundColor Yellow

pyinstaller `
    --onefile `
    --name "拓漫" `
    --add-data "locales;locales" `
    --hidden-import "yaml" `
    --hidden-import "prompt_toolkit" `
    --hidden-import "rich" `
    --hidden-import "httpx" `
    --hidden-import "hermes_cli" `
    --hidden-import "agent" `
    --hidden-import "tools" `
    --hidden-import "cron" `
    --hidden-import "gateway" `
    --hidden-import "plugins" `
    --collect-all "hermes_cli" `
    --collect-all "agent" `
    --collect-all "tools" `
    --noconsole `
    run_agent.py

if ($LASTEXITCODE -eq 0) {
    Write-Host @"

  ✅ 打包成功！

  输出文件: $ProjectRoot\dist\拓漫.exe
  大小: $((Get-Item "$ProjectRoot\dist\拓漫.exe").Length / 1MB -as [int]) MB

  客户只需要这一个文件，双击即可运行。

"@ -ForegroundColor Green
} else {
    Write-Host "!! 打包失败，请检查错误信息" -ForegroundColor Red
}
