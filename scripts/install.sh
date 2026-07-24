#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/eren11qq/tuoman-sales.git"
INSTALL_DIR="${HOME}/tuoman-sales"

echo "╔══════════════════════════════════════════╗"
echo "║       拓漫 TouMan 远程安装               ║"
echo "╚══════════════════════════════════════════╝"

# 1. Check prerequisites
echo -e "\n[1/5] 检查环境..."
command -v git >/dev/null 2>&1 || { echo "  ❌ 需要 Git"; exit 1; }
echo "  ✅ git"
command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1 || { echo "  ❌ 需要 Python 3.11+"; exit 1; }
PYTHON=$(command -v python3 || command -v python)
echo "  ✅ $($PYTHON --version)"

# 2. Clone / update repo
echo -e "\n[2/5] 获取代码..."
if [ -d "$INSTALL_DIR" ]; then
  echo "  ↻ 更新已有仓库..."
  cd "$INSTALL_DIR" && git pull origin main
  echo "  ✅ 已更新到最新版"
else
  git clone "$REPO_URL" "$INSTALL_DIR"
  echo "  ✅ Clone 完成"
fi

cd "$INSTALL_DIR"

# 3. Create venv + install deps
echo -e "\n[3/5] 安装 Python 依赖..."
if [ ! -d ".venv" ]; then
  $PYTHON -m venv .venv
  echo "  ✅ venv 创建完成"
fi
source .venv/bin/activate
pip install -e . 2>&1
echo "  ✅ Python 依赖安装完成"

# 4. Playwright browser
echo -e "\n[4/5] 安装 Playwright 浏览器..."
python -m playwright install chromium 2>&1
echo "  ✅ Chromium 安装完成"

# 5. Configure .env
echo -e "\n[5/5] 配置..."
if [ ! -f ".env" ]; then
  read -p "  输入你的 OpenAI API Key (留空可跳过): " key
  if [ -n "$key" ]; then
    echo "OPENAI_API_KEY=$key" > .env
    echo "  ✅ .env 已创建"
  else
    cp .env.example .env
    echo "  ⚠️  .env 从模板创建，请手动填入 API Key"
  fi
else
  echo "  ✅ .env 已存在"
fi

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║    安装完成!                              ║"
echo "║                                          ║"
echo "║  运行:                                   ║"
echo "║    cd ~/tuoman-sales                      ║"
echo "║    source .venv/bin/activate              ║"
echo "║    python scripts/daily.py                ║"
echo "╚══════════════════════════════════════════╝"
