"""
Stage 2: Analyzer — LLM 分析爬取数据，提取企业信号 + BANT + ICP 评分
"""

import json
import logging
from pathlib import Path
from typing import Optional

from tuoman.models.lead import PlatformLead, AnalyzedLead, LeadDatabase
from tuoman.llm.client import LLMClient

logger = logging.getLogger("tuoman.pipeline.analyzer")

SYSTEM_PROMPT = """你是拓漫TouMan的AI漫剧行业分析师。你的任务是从博主数据中识别出真正的AI漫剧企业/工作室。

企业信号判断标准：
1. 简介含"工作室"/"公司"/"团队"/"官方"/"企业认证" → 可能是企业
2. 有招聘信息 → 确定是企业
3. 多部连载作品同时运行 → 有产能
4. 商务合作联系方式 → 商业运营
5. 粉丝数>1万 + 持续更新 → 有稳定产出

评分规则：
- confidence: HIGH(≥3个强信号) / MEDIUM(2个) / LOW(≤1个)
- BANT: 每项0-3分 (budget预算信号, authority决策权, need需求强度, timeline时间线)
- ICP: 行业匹配度0-100 (AI漫剧领域越相关越高)

输出严格的JSON格式（不要用markdown代码块，直接输出纯JSON）：
{
    "company_name": "提取的公司或工作室名称",
    "is_enterprise": true/false,
    "confidence": "HIGH/MEDIUM/LOW",
    "enterprise_signals": {"信号类型": true},
    "bant": {"budget": 0, "authority": 0, "need": 0, "timeline": 0},
    "icp_score": 0,
    "analysis_summary": "一句话分析摘要"
}"""


class Analyzer:
    """LLM分析原始数据，输出结构化评分"""

    def __init__(self, llm: Optional[LLMClient] = None, data_dir: Optional[Path] = None):
        self.llm = llm or LLMClient()
        self.data_dir = data_dir or (Path(__file__).parent.parent.parent / "data")
        self.db = LeadDatabase(self.data_dir / "leads.db")

    def run(self, raw_leads: list[PlatformLead]) -> list[AnalyzedLead]:
        """分析一批原始 lead，结果写入 LeadDatabase"""
        results: list[AnalyzedLead] = []

        for lead in raw_leads:
            try:
                analyzed = self._analyze_one(lead)
                results.append(analyzed)
                self.db.update_analysis(analyzed)
            except Exception as e:
                logger.warning("分析失败 %s: %s", lead.author_name, e)
                fallback = AnalyzedLead(
                    platform_data=lead,
                    company_name=lead.author_name,
                    confidence="LOW",
                    priority="COLD",
                    analysis_summary=f"LLM分析失败: {e}",
                )
                results.append(fallback)
                self.db.update_analysis(fallback)

        stats = self.db.get_stats()
        logger.info(
            "分析完成: %d 条, 数据库累计: HOT=%d WARM=%d COLD=%d 总计=%d",
            len(results), stats["hot"], stats["warm"], stats["cold"], stats["total"],
        )
        return results

    def _analyze_one(self, lead: PlatformLead) -> AnalyzedLead:
        """单条 LLM 分析"""
        user_prompt = f"""请分析这个博主是否为AI漫剧企业/工作室：

博主名称: {lead.author_name}
平台: {lead.platform}
UID: {lead.author_id}
简介: {lead.description}
粉丝数: {lead.follower_count}
稿件数: {lead.video_count}
企业认证: {'是' if lead.is_verified else '否'}
搜索关键词命中: {', '.join(lead.keywords_matched)}
检测到的信号: {json.dumps(lead.signals, ensure_ascii=False)}

请严格按JSON格式输出分析结果。"""

        result = self.llm.chat_json(SYSTEM_PROMPT, user_prompt)

        company_name = result.get("company_name", lead.author_name) or lead.author_name
        is_enterprise = bool(result.get("is_enterprise", False))
        confidence = result.get("confidence", "LOW")
        if confidence not in ("HIGH", "MEDIUM", "LOW"):
            confidence = "LOW"

        bant = result.get("bant", {})
        if not isinstance(bant, dict):
            bant = {}
        icp_score = float(result.get("icp_score", 0))
        analysis = result.get("analysis_summary", "") or ""

        # 计算优先级
        priority = self._calc_priority(confidence, bant, icp_score)

        return AnalyzedLead(
            platform_data=lead,
            company_name=company_name,
            is_enterprise=is_enterprise,
            confidence=confidence,
            enterprise_signals=result.get("enterprise_signals", {}),
            bant=bant,
            icp_score=icp_score,
            priority=priority,
            analysis_summary=analysis,
        )

    @staticmethod
    def _calc_priority(confidence: str, bant: dict, icp: float) -> str:
        """HOT / WARM / COLD 判定"""
        bant_total = sum(
            int(bant.get(k, 0)) for k in ("budget", "authority", "need", "timeline")
        )
        if confidence == "HIGH" and bant_total >= 6 and icp >= 60:
            return "HOT"
        if confidence == "HIGH" and bant_total >= 4 and icp >= 40:
            return "WARM"
        if confidence == "MEDIUM" and bant_total >= 4:
            return "WARM"
        return "COLD"
