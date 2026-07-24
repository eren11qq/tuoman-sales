"""
OpenAI LLM 客户端 — 轻量封装，无框架依赖
"""

import os
import json
import logging
from typing import Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("tuoman.llm")


class LLMError(Exception):
    """LLM 调用失败"""


class LLMClient:
    """OpenAI API 封装 — 支持重试、超时、结构化输出"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY 未设置。请创建 .env 文件并添加 OPENAI_API_KEY=你的key"
            )
        base_url = os.environ.get("OPENAI_BASE_URL")
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        self.model = model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception_type(
            (ConnectionError, TimeoutError, Exception)
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
        logger.debug("LLM %s: %d tokens in", self.model, len(content))
        return content

    def chat_json(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
    ) -> dict:
        """对话 + 解析 JSON 输出"""
        raw = self.chat(system, user, temperature=temperature)
        # 从 ```json ... ``` 或裸 JSON 中提取
        try:
            start = raw.index("[") if "[" in raw else raw.index("{")
            end = raw.rindex("]") + 1 if "[" in raw else raw.rindex("}") + 1
            return json.loads(raw[start:end])
        except (ValueError, json.JSONDecodeError) as e:
            logger.warning("LLM JSON parse failed, raw=%s…", raw[:200])
            raise LLMError(f"JSON 解析失败: {e}") from e
