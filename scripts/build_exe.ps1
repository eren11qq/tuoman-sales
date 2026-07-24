<#
.SYNOPSIS
   拓漫 TouMan — PyInstaller 打包为单个 .exe
   用法: .\scripts\build_exe.ps1
   输出: dist\拓漫.exe
#>

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

Write-Host @"
  ╔══════════════════════════════════════════╗
  ║    拓漫 TouMan — 打包 .exe             ║
  ╚══════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# 确保 venv 和依赖
if (-not (Test-Path ".venv")) {
    Write-Host ">> 创建虚拟环境..." -ForegroundColor Yellow
    python -m venv .venv
    & ".venv\Scripts\pip.exe" install -e .
    & ".venv\Scripts\python.exe" -m playwright install chromium
}

# 安装 PyInstaller
$pyi = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyi) {
    Write-Host ">> 安装 PyInstaller..." -ForegroundColor Yellow
    & ".venv\Scripts\pip.exe" install pyinstaller
}

Write-Host ">> 打包中（约 2-5 分钟）..." -ForegroundColor Yellow

pyinstaller `
    --onefile `
    --name "拓漫" `
    --add-data "tuoman;tuoman" `
    --add-data "config;config" `
    --add-data "data;data" `
    --hidden-import "tuoman" `
    --hidden-import "tuoman.cli" `
    --hidden-import "tuoman.pipeline" `
    --hidden-import "tuoman.crawlers" `
    --hidden-import "tuoman.llm" `
    --hidden-import "tuoman.models" `
    --hidden-import "openai" `
    --hidden-import "playwright" `
    --hidden-import "yaml" `
    --hidden-import "tenacity" `
    --hidden-import "dotenv" `
    --collect-all "tuoman" `
    --noconsole `
    --entry-point tuoman.cli:main

if ($LASTEXITCODE -eq 0) {
    $size = (Get-Item "$ProjectRoot\dist\拓漫.exe").Length / 1MB -as [int]
    Write-Host @"
  ✅ 打包成功! 输出: dist\拓漫.exe ($size MB)
  客户只需要这一个文件 + data/ 目录即可运行。
"@ -ForegroundColor Green
} else {
    Write-Host "!! 打包失败" -ForegroundColor Red
}
