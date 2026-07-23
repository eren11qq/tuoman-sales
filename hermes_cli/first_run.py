"""
拓漫 TouMan — 首次启动向导
检测到未配置 API Key 时自动弹出，引导用户完成配置。
"""

import os
import sys
from pathlib import Path


def _get_env_path() -> Path:
    """返回 .env 文件路径."""
    base = os.environ.get("HERMES_HOME", "")
    if not base:
        base = os.environ.get("LOCALAPPDATA", "")
        if base:
            base = str(Path(base) / "hermes")
        else:
            base = str(Path.home() / ".hermes")
    return Path(base) / ".env"


def _has_any_api_key(env_path: Path) -> bool:
    """检查 .env 中是否已有 API Key."""
    if not env_path.exists():
        return False
    try:
        content = env_path.read_text(encoding="utf-8")
        # 检查常见的 API Key 环境变量
        key_vars = ["OPENAI_API_KEY", "DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY",
                     "GROQ_API_KEY", "TOGETHER_API_KEY", "OPENROUTER_API_KEY",
                     "GEMINI_API_KEY", "MISTRAL_API_KEY"]
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                for var in key_vars:
                    if line.startswith(var + "=") and len(line) > len(var) + 3:
                        return True
    except Exception:
        return False
    return False


def _save_api_key(env_path: Path, key: str, provider: str) -> None:
    """保存 API Key 到 .env 文件."""
    env_path.parent.mkdir(parents=True, exist_ok=True)
    var_name = f"{provider.upper()}_API_KEY"
    
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        new_lines = []
        found = False
        for line in lines:
            if line.strip().startswith(var_name + "="):
                new_lines.append(f'{var_name}={key}')
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f'{var_name}={key}')
        env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    else:
        env_path.write_text(f'{var_name}={key}\n', encoding="utf-8")


def run_first_run_wizard() -> bool:
    """
    首次启动向导。检测 API Key 配置，如未配置则引导用户完成。
    
    Returns:
        True 表示配置完成可以继续，False 表示用户退出。
    """
    env_path = _get_env_path()
    
    if _has_any_api_key(env_path):
        return True  # 已配置，跳过
    
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║       拓漫 TouMan — 首次启动            ║")
    print("  ║    请先配置 AI 模型 API Key              ║")
    print("  ╚══════════════════════════════════════════╝")
    print()
    print("  拓漫需要一个 API Key 来调用 AI 模型。")
    print("  推荐使用 DeepSeek（便宜、稳定）或 OpenAI。")
    print()
    print("  支持以下服务：")
    print("   1) DeepSeek      —— 推荐，便宜且国内可访问")
    print("   2) OpenAI        —— 通用，需要海外访问")
    print("   3) OpenRouter    —— 聚合200+模型")
    print("   4) 已有 API Key  —— 手动输入")
    print("   5) 退出")
    print()
    
    while True:
        try:
            choice = input("  请选择 (1-5): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return False
        
        provider_map = {"1": "deepseek", "2": "openai", "3": "openrouter"}
        
        if choice == "5":
            return False
        elif choice == "4":
            print()
            provider = input("  输入服务商名称 (如 deepseek/openai): ").strip()
            if not provider:
                print("  !! 服务商名称不能为空")
                continue
            key = input("  输入 API Key: ").strip()
            if not key:
                print("  !! API Key 不能为空")
                continue
            if not key.startswith("sk-") and not key.startswith("gsk_"):
                print("  ⚠  Key 格式不太对，确认无误后继续")
            _save_api_key(env_path, key, provider)
            print(f"  ✅ 已保存到 {env_path}")
            print()
            break
        elif choice in provider_map:
            provider = provider_map[choice]
            key_prompt = f"  输入你的 {provider.upper()} API Key: "
            try:
                key = input(key_prompt).strip()
            except (EOFError, KeyboardInterrupt):
                return False
            if not key:
                print("  !! API Key 不能为空")
                continue
            _save_api_key(env_path, key, provider)
            print(f"  ✅ 已保存到 {env_path}")
            print()
            break
        else:
            print("  请输入 1-5")
    
    print("  ✅ 配置完成！正在启动拓漫...")
    print()
    return True
