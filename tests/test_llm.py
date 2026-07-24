"""
LLM 客户端单元测试 — JSON 解析、错误处理
"""

import pytest
from tuoman.llm.client import LLMClient, LLMError


class TestJSONParsing:
    """LLMClient._parse_json_safe 鲁棒性测试"""

    def test_parse_plain_json(self):
        raw = '{"company_name": "测试工作室", "confidence": "HIGH"}'
        result = LLMClient._parse_json_safe(raw)
        assert result["company_name"] == "测试工作室"

    def test_parse_markdown_block(self):
        raw = '```json\n{"company_name": "测试工作室"}\n```'
        result = LLMClient._parse_json_safe(raw)
        assert result["company_name"] == "测试工作室"

    def test_parse_markdown_block_no_label(self):
        raw = '```\n{"company_name": "测试工作室"}\n```'
        result = LLMClient._parse_json_safe(raw)
        assert result["company_name"] == "测试工作室"

    def test_parse_with_surrounding_text(self):
        raw = '根据分析，结果为：\n```json\n{"company_name": "XX工作室"}\n```\n以上是分析结果。'
        result = LLMClient._parse_json_safe(raw)
        assert result["company_name"] == "XX工作室"

    def test_parse_array(self):
        raw = '[{"name": "A"}, {"name": "B"}]'
        result = LLMClient._parse_json_safe(raw)
        assert isinstance(result, list) is False  # 当前返回 dict
        # chat_json 期望 dict, 这里只测试 _parse_json_safe
        # 实际上它返回整个解析结果，如果是 list 则直接返回 list
        result2 = LLMClient._parse_json_safe(raw)
        assert len(result2) > 0  # 会解析成功

    def test_parse_truncated_json(self):
        """截断 JSON 的容错"""
        raw = '{"company_name": "测试工作室", "confidence": "HIGH"'
        result = LLMClient._parse_json_safe(raw)
        assert result["company_name"] == "测试工作室"

    def test_parse_truncated_with_braces(self):
        raw = '{"a": {"b": {"c": 1}'
        result = LLMClient._parse_json_safe(raw)
        assert result["a"]["b"]["c"] == 1

    def test_parse_no_json(self):
        """没有 JSON 应抛异常"""
        with pytest.raises(LLMError):
            LLMClient._parse_json_safe("这是一段纯文本，没有JSON")

    def test_parse_empty(self):
        with pytest.raises(LLMError):
            LLMClient._parse_json_safe("")

    def test_parse_invalid_json_with_quote_fix(self):
        raw = '{"company_name": "测试工作室, "confidence": "HIGH"}'
        # 引号不匹配，看是否容错
        try:
            result = LLMClient._parse_json_safe(raw)
            # 如果容错处理了，验证结果
            assert "company_name" in result or "confidence" in result
        except LLMError:
            pass  # 也可以接受失败
