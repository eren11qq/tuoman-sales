<#
.SYNOPSIS
    拓漫 TouMan — 一键安装 (Windows)
    用法: iex (irm https://raw.githubusercontent.com/eren11qq/tuoman-sales/main/scripts/tuoman-install.ps1)
.DESCRIPTION
    自动 Clone → venv → 安装依赖 → Playwright 浏览器 → 配置 API Key → 桌面快捷方式
#>

param(
    [string]$InstallDir = "$env:LOCALAPPDATA\tuoman"
)

$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Stop"

function Write-Step($msg) { Write-Host ">> $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "   OK $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "   ! $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "!! $msg" -ForegroundColor Red }

Write-Host @"

  ╔══════════════════════════════════════════╗
  ║    拓漫 TouMan — 一键安装               ║
  ╚══════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ── Step 1: Python ──
Write-Step "检查 Python..."
$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) {
    Write-Err "需要 Python 3.11+，请先安装: https://python.org"
    Read-Host "按回车退出"; exit 1
}
Write-Ok "Python: $(& $python --version 2>&1)"

# ── Step 2: Git ──
Write-Step "检查 Git..."
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
    try {
        winget install Git.Git --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
        $git = Get-Command git -ErrorAction SilentlyContinue
    } catch { }
}
if (-not $git) { Write-Warn "Git 不可用，将通过 ZIP 下载代码" }
else { Write-Ok "Git 可用" }

# ── Step 3: Clone/Update ──
Write-Step "获取拓漫代码..."
if (Test-Path "$InstallDir\.git") {
    Push-Location $InstallDir
    try { & git pull --ff-only 2>&1 | Out-Null; Write-Ok "已更新到最新" } catch { Write-Warn "git pull 失败" }
    Pop-Location
} else {
    if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir -ErrorAction SilentlyContinue }
    if ($git) {
        & git clone --depth 1 https://github.com/eren11qq/tuoman-sales.git $InstallDir 2>&1
        if ($LASTEXITCODE -ne 0) { Write-Err "克隆失败"; Read-Host "按回车退出"; exit 1 }
    } else {
        Write-Step "通过 ZIP 下载..."
        $zipUrl = "https://github.com/eren11qq/tuoman-sales/archive/refs/heads/main.zip"
        $zipPath = "$env:TEMP\tuoman.zip"
        try {
            Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
            Expand-Archive -Path $zipPath -DestinationPath "$env:TEMP\tuoman-extract" -Force
            Move-Item "$env:TEMP\tuoman-extract\tuoman-sales-main" $InstallDir
            Remove-Item "$env:TEMP\tuoman-extract" -Recurse -Force -ErrorAction SilentlyContinue
            Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
        } catch { Write-Err "下载失败: $_"; Read-Host "按回车退出"; exit 1 }
    }
    Write-Ok "代码已下载到 $InstallDir"
}

Push-Location $InstallDir

# ── Step 4: venv + 依赖 ──
Write-Step "创建虚拟环境..."
if (-not (Test-Path ".venv")) {
    & $python -m venv .venv
    if ($LASTEXITCODE -ne 0) { Write-Err "venv 创建失败"; exit 1 }
}
$pythonExe = "$InstallDir\.venv\Scripts\python.exe"
Write-Ok "虚拟环境已就绪"

Write-Step "安装核心依赖..."
$coreDeps = @(
    "openai>=1.0.0", "playwright>=1.40.0", "pyyaml>=6.0",
    "tenacity>=8.0.0", "python-dotenv>=1.0.0"
)
foreach ($dep in $coreDeps) {
    & $pythonExe -m pip install $dep --quiet 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Warn "安装失败: $dep" }
}
& $pythonExe -m pip install -e "." --quiet 2>&1
Write-Ok "依赖安装完成"

# ── Step 5: Playwright Chromium ──
Write-Step "安装 Playwright 浏览器..."
& $pythonExe -m playwright install chromium 2>&1
if ($LASTEXITCODE -eq 0) { Write-Ok "Chromium 安装完成" }
else { Write-Warn "Chromium 安装失败，可手动运行: playwright install chromium" }

# ── Step 6: .env ──
Write-Step "配置 API Key..."
$envFile = "$InstallDir\.env"
if (-not (Test-Path $envFile)) {
    $key = Read-Host "  输入 OpenAI API Key (Enter 跳过)"
    if ($key) {
        "OPENAI_API_KEY=$key" | Out-File $envFile -Encoding UTF8
        Write-Ok ".env 已创建"
    } else {
        Copy-Item "$InstallDir\.env.example" "$InstallDir\.env"
        Write-Warn "请手动编辑 .env 填入 API Key"
    }
} else { Write-Ok ".env 已存在" }

# ── Step 7: Desktop shortcut ──
Write-Step "创建桌面快捷方式..."
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = "$desktopPath\拓漫.lnk"
if (-not (Test-Path $shortcutPath)) {
    try {
        $wshell = New-Object -ComObject WScript.Shell
        $shortcut = $wshell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = "$InstallDir\.venv\Scripts\python.exe"
        $shortcut.Arguments = "-m tuoman.cli run"
        $shortcut.WorkingDirectory = "$InstallDir"
        $shortcut.Description = "拓漫 TouMan — AI漫剧行业智能获客助手"
        $shortcut.Save()
        Write-Ok "桌面快捷方式已创建"
    } catch { Write-Warn "快捷方式创建失败: $_" }
} else { Write-Ok "桌面快捷方式已存在" }

# ── Done ──
Pop-Location

Write-Host @"

  ╔══════════════════════════════════════════╗
  ║    拓漫 TouMan 安装完成!                ║
  ╚══════════════════════════════════════════╝

  运行:
    cd $InstallDir
    .venv\Scripts\python -m tuoman.cli run

  或:
    双击桌面「拓漫」图标

  其他命令:
    tuoman list hot      — 查看 HOT 线索
    tuoman stats         — 查看统计
    tuoman search 关键词  — 搜索线索

  首次运行前请确保 .env 中的 API Key 已配置。

"@ -ForegroundColor Green
