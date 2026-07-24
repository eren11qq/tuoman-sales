"""
OpenAI LLM 客户端 — 轻量封装，支持重试、超时、结构化输出、多provider
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Optional

from openai import OpenAI, APIError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger("tuoman.llm")


class LLMError(Exception):
    """LLM 调用失败"""


class LLMClient:
    """OpenAI API 封装 — 支持重试、超时、结构化输出"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
        if not self.api_key:
            # 尝试从 .env 文件加载
            env_paths = [
                Path(os.environ.get("HOME", "~")) / ".hermes" / ".env",
                Path.cwd() / ".env",
            ]
            for env_path in env_paths:
                expanded = env_path.expanduser()
                if expanded.exists():
                    for line in expanded.read_text(encoding="utf-8").splitlines():
                        if "=" in line and not line.strip().startswith("#"):
                            k, v = line.strip().split("=", 1)
                            if k == "OPENAI_API_KEY":
                                self.api_key = v
                                break
                            elif k == "DEEPSEEK_API_KEY" and not self.api_key:
                                self.api_key = v
                    if self.api_key:
                        break

        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY 未设置。请创建 .env 文件并添加 OPENAI_API_KEY=sk-你的key"
            )

        base_url = os.environ.get("OPENAI_BASE_URL")
        # 如果用的是 DEEPSEEK_API_KEY 且没设 BASE_URL，自动用 DeepSeek
        if not base_url and os.environ.get("DEEPSEEK_API_KEY"):
            base_url = "https://api.deepseek.com/v1"
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        self.model = model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type(
            (ConnectionError, TimeoutError, APIError)
        ),
    )
    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """普通对话"""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = resp.choices[0].message.content or ""
        logger.debug("LLM %s: %d chars out", self.model, len(content))
        return content

    def chat_json(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
    ) -> dict:
        """对话 + 鲁棒 JSON 解析（支持 markdown 代码块、截断修复）"""
        raw = self.chat(system, user, temperature=temperature)
        return self._parse_json_safe(raw)

    @staticmethod
    def _parse_json_safe(raw: str) -> dict:
        """从 LLM 输出中提取 JSON，支持 markdown 包裹和常见截断"""
        # 1. 尝试 ```json ... ``` 代码块
        block_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
        cleaned = block_match.group(1) if block_match else raw

        # 2. 从 { 或 [ 开始截取
        brace_start = cleaned.find("{")
        arr_start = cleaned.find("[")
        start = brace_start if brace_start >= 0 else arr_start
        if start < 0:
            raise LLMError(f"JSON 起始符号未找到: {raw[:200]}")

        # 3. 尝试完整解析，如果失败则尝试修复截断
        text = cleaned[start:]

        # 尝试完整解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试修复：补全缺失的引号、花括号
        if text.startswith("{"):
            # 找到最长的合法前缀
            for end_pos in range(len(text), start, -1):
                candidate = text[:end_pos]
                # 补全引号
                if candidate.count('"') % 2 != 0:
                    candidate += '"'
                # 补全花括号
                open_braces = candidate.count("{") - candidate.count("}")
                if open_braces > 0:
                    candidate += "}" * open_braces
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue

        raise LLMError(f"JSON 解析失败 (len={len(text)}): {text[:200]}")
