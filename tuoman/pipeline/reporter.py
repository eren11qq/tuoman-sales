"""
Stage 4: Reporter — 汇总全管线数据，生成日报
"""

import logging
from datetime import date
from pathlib import Path
from typing import Optional

from tuoman.models.lead import AnalyzedLead, PlatformLead
from tuoman.llm.client import LLMClient

logger = logging.getLogger("tuoman.pipeline.reporter")

REPORT_SYSTEM = """你是拓漫TouMan的获客管线报告专家。根据今日管线数据生成简洁的日报。

报告结构：
1. 执行摘要 — 今日发现数量、HOT/WARM/COLD分布
2. 新发现线索 — 简要列表
3. HOT线索详情 — 需要立即跟进的
4. 管线健康度 — 数据质量、覆盖平台、趋势
5. 明日建议 — 下一步行动

风格：简洁、数据驱动、可执行。"""


class Reporter:
    """生成管线日报"""

    def __init__(self, llm: Optional[LLMClient] = None, data_dir: Optional[Path] = None):
        self.llm = llm or LLMClient()
        self.data_dir = data_dir or (Path(__file__).parent.parent.parent / "data")

    def run(
        self,
        raw_leads: list[PlatformLead],
        analyzed: list[AnalyzedLead],
        outreach: list[dict],
        stats: Optional[dict] = None,
    ) -> str:
        """生成日报"""
        today = date.today().isoformat()
        hot = [x for x in analyzed if x.priority == "HOT"]
        warm = [x for x in analyzed if x.priority == "WARM"]
        cold = [x for x in analyzed if x.priority == "COLD"]

        if stats is None:
            stats = {"total": 0, "hot": 0, "warm": 0, "cold": 0}

        # LLM增强报告
        hot_lines = ""
        for lead in hot[:10]:
            bant = sum(int(lead.bant.get(k, 0)) for k in ("budget", "authority", "need", "timeline"))
            hot_lines += f"- {lead.company_name} (ICP:{lead.icp_score:.0f}%, BANT:{bant})\n"
        if not hot_lines:
            hot_lines = "无"

        user_prompt = f"""拓漫获客管线日报 — {today}

今日原始发现: {len(raw_leads)} 个博主
完成分析: {len(analyzed)} 条
HOT: {len(hot)}
WARM: {len(warm)}
COLD: {len(cold)}
触达文案: {len(outreach)} 条
数据库总计: {stats.get('total', 0)} 条

HOT线索列表:
{hot_lines}
请生成日报。"""

        md_report = self.llm.chat(REPORT_SYSTEM, user_prompt)

        # 结构化摘要
        summary = (
            f"# 拓漫获客日报 {today}\n\n"
            f"## 执行摘要\n\n"
            f"- 今日发现: {len(raw_leads)} 个博主\n"
            f"- 完成分析: {len(analyzed)} 条\n"
            f"- 待跟进(HOT): {len(hot)} 个\n"
            f"- 持续关注(WARM): {len(warm)} 个\n"
            f"- 已生成触达文案: {len(outreach)} 条\n"
            f"- 数据库累计: {stats.get('total', 0)} 条\n\n"
        )

        if hot:
            summary += "## HOT 线索\n\n"
            for x in hot:
                platform = x.platform_data.platform if hasattr(x, 'platform_data') and hasattr(x.platform_data, 'platform') else ""
                url = x.platform_data.author_url if hasattr(x, 'platform_data') else ""
                summary += f"- **{x.company_name}** (ICP: {x.icp_score:.0f}%)\n"
                summary += f"  - {x.analysis_summary}\n"
                if url:
                    summary += f"  - {platform}: {url}\n\n"

        # 持久化
        reports_dir = Path(__file__).parent.parent.parent / "reports" / today
        reports_dir.mkdir(parents=True, exist_ok=True)

        full_report = summary + "\n---\n## LLM 分析\n\n" + md_report
        (reports_dir / "pipeline_report.md").write_text(full_report, encoding="utf-8")

        logger.info("日报已生成: %s", reports_dir / "pipeline_report.md")
        return full_report
