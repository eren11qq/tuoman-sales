"""
Stage 3: Outreach — 为 HOT leads 生成触达文案
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional

from tuoman.models.lead import AnalyzedLead
from tuoman.llm.client import LLMClient

logger = logging.getLogger("tuoman.pipeline.outreach")

OUTREACH_SYSTEM = """你是一位AI漫剧行业的商务拓展专家。为HOT线索生成个性化触达文案。

规则：
1. 语气专业但亲切，不要过于销售化
2. 结合UP主实际内容（作品标题、简介）体现你真的了解他们
3. 点出拓漫能提供的价值：AI漫剧制作管线、获客系统、效率提升
4. 每条消息控制在200字以内
5. 给出推荐渠道（B站私信/邮箱/微信）

输出JSON：
{
    "channel": "推荐渠道",
    "channel_reason": "为什么选这个渠道",
    "message": "完整的触达文案",
    "follow_up_day1": "第一天跟进文案",
    "follow_up_day3": "第三天跟进文案",
    "follow_up_day7": "第七天跟进文案"
}"""


class OutreachGenerator:
    """为 HOT leads 生成触达文案"""

    def __init__(self, llm: Optional[LLMClient] = None, data_dir: Optional[Path] = None):
        self.llm = llm or LLMClient()
        self.data_dir = data_dir or (Path(__file__).parent.parent.parent / "data")

    def run(self, analyzed_leads: list[AnalyzedLead]) -> list[dict]:
        """为HOT leads生成触达文案"""
        hot = [l for l in analyzed_leads if l.priority == "HOT"]
        if not hot:
            logger.info("没有HOT leads，跳过触达")
            return []

        results = []
        for lead in hot:
            try:
                msg = self._generate(lead)
                lead.outreach_message = msg.get("message", "")
                results.append({"company": lead.company_name, **msg})
            except Exception as e:
                logger.warning("生成触达文案失败 %s: %s", lead.company_name, e)

        # 持久化
        today = date.today().isoformat()
        reports_dir = Path(__file__).parent.parent.parent / "reports" / today / "outreach"
        reports_dir.mkdir(parents=True, exist_ok=True)
        for item in results:
            safe_name = item["company"].replace(" ", "_").replace("/", "_")
            (reports_dir / f"{safe_name}.json").write_text(
                json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        (reports_dir / "outreach_summary.json").write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("触达文案已生成: %d 条", len(results))
        return results

    def _generate(self, lead: AnalyzedLead) -> dict:
        pd = lead.platform_data
        user_prompt = f"""为这家AI漫剧公司生成触达文案：

公司/工作室: {lead.company_name}
UP主: {pd.author_name}
简介: {pd.description}
最近作品: {', '.join(pd.recent_titles[:5])}
分析摘要: {lead.analysis_summary}

产出触达文案。"""
        return self.llm.chat_json(OUTREACH_SYSTEM, user_prompt)
