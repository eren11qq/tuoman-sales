<#
.SYNOPSIS
   拓漫 TouMan — 远程一键安装 (Windows)
   用法: iex (irm https://raw.githubusercontent.com/eren11qq/tuoman-sales/main/scripts/tuoman-install.ps1)
.DESCRIPTION
   自动 Clone 仓库 → 创建 venv → 安装依赖 → Playwright → 配置 API Key
#>

$ErrorActionPreference = "Stop"
$REPO_URL = "https://github.com/eren11qq/tuoman-sales.git"
$INSTALL_DIR = "$HOME\tuoman-sales"

Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       拓漫 TouMan 远程安装               ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan

# 1. 环境检查
Write-Host "`n[1/5] 检查环境..." -ForegroundColor Yellow
$gitVer = git --version 2>$null
if (-not $gitVer) { Write-Host "  ❌ 需要 Git: https://git-scm.com" -ForegroundColor Red; exit 1 }
Write-Host "  ✅ $gitVer"
$pyVer = python --version 2>$null
if (-not $pyVer) { Write-Host "  ❌ 需要 Python 3.11+: https://python.org" -ForegroundColor Red; exit 1 }
Write-Host "  ✅ $pyVer"

# 2. Clone/更新
Write-Host "`n[2/5] 获取代码..." -ForegroundColor Yellow
if (Test-Path $INSTALL_DIR) {
    Push-Location $INSTALL_DIR
    $null = & git pull origin main 2>&1
    $exit = $LASTEXITCODE
    Pop-Location
    if ($exit -ne 0) { Write-Host "  ⚠️ 更新可能不完整 (exit=$exit)" -ForegroundColor Yellow }
    Write-Host "  ✅ 已同步最新代码"
} else {
    $null = & git clone $REPO_URL $INSTALL_DIR 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Host "  ❌ Clone 失败" -ForegroundColor Red; exit 1 }
    Write-Host "  ✅ Clone 完成"
}

# 3. 安装依赖
Write-Host "`n[3/5] 安装 Python 依赖..." -ForegroundColor Yellow
Push-Location $INSTALL_DIR
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "  ✅ venv 创建完成"
}
$pipResult = .\.venv\Scripts\pip install -e . 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ pip 安装失败: $pipResult" -ForegroundColor Red
    Pop-Location
    exit 1
}
Write-Host "  ✅ Python 依赖安装完成"

# 4. Playwright
Write-Host "`n[4/5] 安装 Playwright 浏览器..." -ForegroundColor Yellow
.\.venv\Scripts\python -m playwright install chromium 2>&1
Write-Host "  ✅ Chromium 安装完成"

# 5. 配置 .env
Write-Host "`n[5/5] 配置..." -ForegroundColor Yellow
$envFile = "$INSTALL_DIR\.env"
if (-not (Test-Path $envFile)) {
    $key = Read-Host "  输入你的 OpenAI API Key (留空可跳过)"
    if ($key) {
        "OPENAI_API_KEY=$key" | Out-File $envFile -Encoding UTF8
        Write-Host "  ✅ .env 已创建"
    } else {
        Copy-Item "$INSTALL_DIR\.env.example" $envFile
        Write-Host "  ⚠️  .env 从模板创建，请手动填入 API Key"
    }
} else {
    Write-Host "  ✅ .env 已存在"
}
Pop-Location

Write-Host "`n╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║    安装完成!                              ║" -ForegroundColor Green
Write-Host "║                                          ║" -ForegroundColor Green
Write-Host "║  运行:                                   ║" -ForegroundColor Green
Write-Host "║    cd $HOME\tuoman-sales                  ║" -ForegroundColor Green
Write-Host "║    .venv\Scripts\python scripts/daily.py ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
