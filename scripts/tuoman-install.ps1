<#
.SYNOPSIS
  拓漫 TouMan — 一键安装
  用法: iex (irm https://raw.githubusercontent.com/eren11qq/tuoman-sales/main/scripts/tuoman-install.ps1)
  
  本脚本会自动:
  1. 检查/安装 Python 3.11-3.13
  2. 克隆/更新 拓漫 仓库
  3. 创建虚拟环境并安装所有依赖
  4. 安装 拓漫 技能到 Hermes 目录
  5. 创建桌面快捷方式
  6. 添加 PATH
#>

param(
  [string]$InstallDir = "$env:LOCALAPPDATA\tuoman"
)

$ProgressPreference = "SilentlyContinue"
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

# ── Retry helper ────────────────────────────────────────────────────────────
function Invoke-WithRetry {
    param([ScriptBlock]$Block, [int]$MaxRetries = 3, [string]$Label = "operation")
    $attempt = 0
    while ($attempt -lt $MaxRetries) {
        try {
            & $Block
            return
        } catch {
            $attempt++
            if ($attempt -ge $MaxRetries) { throw }
            $wait = [Math]::Pow(2, $attempt)
            Write-Warn "$Label failed (attempt $attempt/$MaxRetries), retrying in ${wait}s... $_"
            Start-Sleep -Seconds $wait
        }
    }
}

# ── Checksum verification ───────────────────────────────────────────────────
function Test-FileChecksum {
    param([string]$Path, [string]$ExpectedHash)
    if (-not $ExpectedHash) { return $true }  # Skip if no hash provided
    try {
        $hash = (Get-FileHash -Path $Path -Algorithm SHA256).Hash.ToUpper()
        return $hash -eq $ExpectedHash.ToUpper()
    } catch { return $false }
}

function Write-Step($msg) { Write-Host ">> $msg" -ForegroundColor Cyan }
function Write-Ok($msg) { Write-Host "   OK $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "   ! $msg" -ForegroundColor Yellow }
function Write-Err($msg) { Write-Host "!! $msg" -ForegroundColor Red }

# ── Banner ──
Write-Host @"

  ╔══════════════════════════════════════════╗
  ║    拓漫 TouMan — 一键安装               ║
  ╚══════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# ── Step 1: Check Python ──
Write-Step "检查 Python..."
$python = $null
$pythonVersion = $null

# Try python first, then python3
foreach ($cmd in @("python", "python3")) {
  try {
    $ver = & $cmd --version 2>&1
    if ($LASTEXITCODE -eq 0 -and $ver -match "(\d+)\.(\d+)") {
      $major = [int]$Matches[1]
      $minor = [int]$Matches[2]
      if ($major -eq 3 -and $minor -ge 11 -and $minor -le 13) {
        $python = $cmd
        $pythonVersion = "$major.$minor"
        Write-Ok "已安装 $cmd $pythonVersion"
        break
      }
    }
  } catch { continue }
}

if (-not $python) {
  Write-Step "安装 Python 3.11..."
  try {
    winget install "Python.Python.3.11" --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
    # winget doesn't add to PATH immediately, find the installed Python
    $possiblePaths = @(
      "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
      "C:\Program Files\Python311\python.exe",
      "C:\Python311\python.exe"
    )
    foreach ($p in $possiblePaths) {
      if (Test-Path $p) { $python = $p; break }
    }
    if (-not $python) { throw "Python 3.11 安装失败，请手动安装 https://www.python.org/downloads/" }
    Write-Ok "Python 3.11 已安装"
  } catch {
    Write-Err "请手动安装 Python 3.11+ (https://www.python.org/downloads/)"
    Read-Host "按回车退出"
    exit 1
  }
}

# ── Step 2: Git ──
Write-Step "检查 Git..."
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) {
  Write-Step "安装 Git..."
  try {
    winget install Git.Git --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
    $git = Get-Command git -ErrorAction SilentlyContinue
    if (-not $git) { throw "Git 安装失败" }
    Write-Ok "Git 已安装"
  } catch {
    Write-Warn "Git 不可用，尝试直接下载..."
  }
}

# ── Step 3: Clone/Update repo ──
Write-Step "获取拓漫代码..."
if (Test-Path "$InstallDir\.git") {
  Push-Location $InstallDir
  try { & git pull --ff-only 2>&1 | Out-Null } catch { Write-Warn "git pull 失败，将重新克隆" }
  Pop-Location
} else {
  if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir -ErrorAction SilentlyContinue }
  if ($git) {
    Invoke-WithRetry -Label "git clone" -Block {
      & git clone --depth 1 https://github.com/eren11qq/tuoman-sales.git $InstallDir 2>&1
      if ($LASTEXITCODE -ne 0) { throw "克隆失败 (exit $LASTEXITCODE)" }
    }
  } else {
    # Fallback: download ZIP with checksum
    Write-Step "通过 ZIP 下载..."
    $zipUrl = "https://github.com/eren11qq/tuoman-sales/archive/refs/heads/main.zip"
    $zipPath = "$env:TEMP\tuoman.zip"
    # Known good SHA256 (auto-updated on release) — empty = skip verification
    $expectedHash = ""
    try {
      [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
      Invoke-WithRetry -Label "ZIP download" -Block {
        Invoke-WebRequest -Uri $zipUrl -OutFile $zipPath -UseBasicParsing
        if (-not (Test-FileChecksum -Path $zipPath -ExpectedHash $expectedHash)) {
          throw "SHA256 checksum mismatch"
        }
      }
      Expand-Archive -Path $zipPath -DestinationPath "$env:TEMP\tuoman-extract" -Force
      if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir }
      Move-Item "$env:TEMP\tuoman-extract\tuoman-sales-main" $InstallDir
      Remove-Item "$env:TEMP\tuoman-extract" -Recurse -Force -ErrorAction SilentlyContinue
      Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
    } catch {
      Write-Err "下载失败: $_"
      Read-Host "按回车退出"
      exit 1
    }
  }
  Write-Ok "代码已下载到 $InstallDir"
}

Push-Location $InstallDir

# ── Step 4: Create venv & install deps ──
Write-Step "创建虚拟环境..."
if (-not (Test-Path ".venv")) {
  & "$python" -m venv .venv
  if ($LASTEXITCODE -ne 0) { throw "venv 创建失败" }
}
Write-Ok "虚拟环境已就绪"

Write-Step "安装核心依赖..."
$pip = "$InstallDir\.venv\Scripts\python.exe" -m pip

# Upgrade pip first
& $pip install --upgrade pip --quiet 2>&1 | Out-Null

# Install all core deps, exact-pinned per pyproject.toml
$coreDeps = @(
  "openai==2.24.0",
  "certifi==2026.5.20",
  "python-dotenv==1.2.2",
  "fire==0.7.1",
  "httpx[socks]==0.28.1",
  "rich==14.3.3",
  "tenacity==9.1.4",
  "pyyaml==6.0.3",
  "ruamel.yaml==0.18.17",
  "requests==2.33.0",
  "jinja2==3.1.6",
  "pydantic==2.13.4",
  "prompt_toolkit==3.0.52",
  "croniter==6.0.0",
  "packaging==26.0",
  "Markdown==3.10.2",
  "PyJWT[crypto]==2.13.0",
  "urllib3>=2.7.0,<3",
  "cryptography==46.0.7",
  "psutil==7.2.2",
  "websockets==15.0.1",
  "pathspec==1.1.1",
  "Pillow==12.2.0"
)

# Platform-specific deps
if ($env:OS -match "Windows") {
  $coreDeps += @(
    "tzdata==2025.3",
    "pywin32>=306,<312",
    "pywinpty>=2.0.0,<3",
    "concurrent-log-handler==0.9.29"
  )
}

# Try each dep individually so one failure doesn't block the rest
$failedDeps = @()
foreach ($dep in $coreDeps) {
  $output = & $pip install $dep --quiet 2>&1
  if ($LASTEXITCODE -ne 0) { $failedDeps += $dep }
}
if ($failedDeps.Count -gt 0) {
  Write-Warn "以下依赖安装失败，将重新尝试批量安装:"
  $failedDeps | ForEach-Object { Write-Warn "   - $_" }
  & $pip install @failedDeps 2>&1
  if ($LASTEXITCODE -ne 0) {
    Write-Warn "部分依赖仍失败，但核心功能可能正常"
  }
}

# Then install the project itself (editable mode, no extras to keep it lean)
& $pip install -e "." --quiet 2>&1 | Out-Null

Write-Ok "依赖安装完成"

# ── Step 5: Install Hermes skills ──
Write-Step "安装拓漫技能..."
$hermesSkillsDir = "$env:USERPROFILE\.hermes\skills"
if (-not (Test-Path $hermesSkillsDir)) {
  New-Item -ItemType Directory -Path $hermesSkillsDir -Force | Out-Null
}

# Copy tuoman skills to Hermes skills directory
$skillDirs = @("lead-finder", "company-researcher", "enterprise-filter", "outreach-generator", "daily-report", "sales-outreach")
$skillCount = 0
foreach ($skill in $skillDirs) {
  $srcSkill = "$InstallDir\skills\$skill"
  $dstSkill = "$hermesSkillsDir\$skill"
  if (Test-Path $srcSkill) {
    if (-not (Test-Path $dstSkill)) {
      New-Item -ItemType Directory -Path $dstSkill -Force | Out-Null
    }
    if (Test-Path "$srcSkill\SKILL.md") {
      Copy-Item "$srcSkill\SKILL.md" "$dstSkill\SKILL.md" -Force
      $skillCount++
    }
  }
}

# Also copy optional-skills (for advanced features)
$optSkillDirs = @("lead-finder", "company-researcher", "enterprise-filter", "outreach-generator", "daily-report")
foreach ($skill in $optSkillDirs) {
  $srcSkill = "$InstallDir\optional-skills\$skill"
  $dstSkill = "$hermesSkillsDir\$skill"
  if (Test-Path $srcSkill -and (Test-Path "$srcSkill\SKILL.md")) {
    if (-not (Test-Path $dstSkill)) {
      New-Item -ItemType Directory -Path $dstSkill -Force | Out-Null
    }
    Copy-Item "$srcSkill\SKILL.md" "$dstSkill\SKILL.md" -Force
  }
}

Write-Ok "已安装 $skillCount 个技能到 Hermes"

# ── Step 6: PATH setup ──
Write-Step "配置 PATH..."
$venvPath = "$InstallDir\.venv\Scripts"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$venvPath*") {
  [Environment]::SetEnvironmentVariable("Path", "$userPath;$venvPath", "User")
  Write-Ok "PATH 已添加"
} else {
  Write-Ok "PATH 已存在"
}

# ── Step 7: Desktop shortcut ──
Write-Step "创建桌面快捷方式..."
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = "$desktopPath\拓漫.lnk"
if (-not (Test-Path $shortcutPath)) {
  try {
    $wshell = New-Object -ComObject WScript.Shell
    $shortcut = $wshell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = "$InstallDir\.venv\Scripts\python.exe"
    $shortcut.Arguments = "-m hermes_cli.main"
    $shortcut.WorkingDirectory = "$env:USERPROFILE"
    $shortcut.Description = "拓漫 TouMan — AI漫剧行业智能获客助手"
    $shortcut.IconLocation = "$InstallDir\.venv\Scripts\python.exe,0"
    $shortcut.Save()
    Write-Ok "桌面快捷方式已创建"
  } catch {
    Write-Warn "桌面快捷方式创建失败: $_"
  }
} else {
  Write-Ok "桌面快捷方式已存在"
}

# ── Step 8: .env check ──
$envPath = "$env:LOCALAPPDATA\hermes\.env"
if (-not (Test-Path $envPath) -and -not (Test-Path "$InstallDir\.env")) {
  Write-Warn ""
  Write-Warn "首次使用需要配置 API Key！"
  Write-Warn "创建文件 $envPath，写入:"
  Write-Warn "   OPENAI_API_KEY=sk-你的key"
  Write-Warn "   或 DEEPSEEK_API_KEY=sk-你的key"
}

# ── Done ──
Write-Host @"

  ╔══════════════════════════════════════════╗
  ║    拓漫 TouMan 安装完成！               ║
  ╚══════════════════════════════════════════╝

  启动方式:
  1. 双击桌面「拓漫」图标
  2. 或打开终端运行: tuoman

  每日管线:
  python "$InstallDir\scripts\tuoman_daily.py"

  Windows 定时任务:
  powershell "$InstallDir\scripts\setup_scheduler.ps1"

  首次使用请配置 .env 中的 API Key。

"@ -ForegroundColor Green

Pop-Location
