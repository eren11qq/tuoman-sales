"""
Pipeline Runner — 编排多 stage 按序执行
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional

from tuoman.llm.client import LLMClient
from tuoman.models.lead import PlatformLead, AnalyzedLead, LeadDatabase
from tuoman.pipeline.finder import Finder
from tuoman.pipeline.analyzer import Analyzer
from tuoman.pipeline.outreach import OutreachGenerator
from tuoman.pipeline.reporter import Reporter

logger = logging.getLogger("tuoman.pipeline.runner")

ROOT = Path(__file__).parent.parent.parent
DATA_DIR = ROOT / "data"


class PipelineRunner:
    """管线编排器 — 支持全量运行和单 stage 运行"""

    STAGES = ["finder", "analyzer", "outreach", "reporter"]

    def __init__(
        self,
        headless: bool = True,
        model: str = "gpt-4o",
        data_dir: Optional[Path] = None,
        platforms: Optional[list[str]] = None,
    ):
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = LeadDatabase(self.data_dir / "leads.db")
        llm = LLMClient(model=model)
        self._finder = Finder(platforms=platforms, headless=headless, data_dir=self.data_dir)
        self._analyzer = Analyzer(llm=llm, data_dir=self.data_dir)
        self._outreach = OutreachGenerator(llm=llm, data_dir=self.data_dir)
        self._reporter = Reporter(llm=llm, data_dir=self.data_dir)

    def run_stage(self, stage: str, **kwargs) -> dict:
        """运行单个 stage"""
        stage_map = {
            "finder": self._run_finder,
            "analyzer": self._run_analyzer,
            "outreach": self._run_outreach,
            "reporter": self._run_reporter,
        }
        func = stage_map.get(stage)
        if not func:
            raise ValueError(f"未知 stage: {stage}，可用: {', '.join(self.STAGES)}")

        today = date.today().isoformat()
        logger.info("【单stage】%s", stage)
        result = {"date": today, "stage": stage, "status": "pending"}

        try:
            output = func(**kwargs)
            result["status"] = "ok"
            if isinstance(output, list):
                result["count"] = len(output)
            return result
        except Exception as e:
            logger.error("Stage %s 失败: %s", stage, e, exc_info=True)
            result["status"] = f"failed: {e}"
            return result

    def run(self) -> dict:
        """执行完整管线"""
        today = date.today().isoformat()
        logger.info("=" * 50)
        logger.info("拓漫管线启动: %s", today)
        logger.info("=" * 50)

        result = {
            "date": today,
            "stages": {},
        }

        # Stage 1: Finder
        logger.info("【Stage 1/4】Finder — 跨平台爬取")
        raw_leads = self._run_finder()
        result["stages"]["finder"] = {"status": "ok", "count": len(raw_leads)}

        # Stage 2: Analyzer
        logger.info("【Stage 2/4】Analyzer — LLM 分析")
        analyzed = self._run_analyzer(raw_leads)
        result["stages"]["analyzer"] = {"status": "ok", "count": len(analyzed)}

        # Stage 3: Outreach
        logger.info("【Stage 3/4】Outreach — 触达文案")
        outreach = self._run_outreach(analyzed)
        result["stages"]["outreach"] = {"status": "ok", "count": len(outreach)}

        # Stage 4: Reporter
        logger.info("【Stage 4/4】Reporter — 日报")
        self._run_reporter(raw_leads, analyzed, outreach)
        result["stages"]["reporter"] = {"status": "ok"}

        # 统计数据
        stats = self.db.get_stats()
        result["stats"] = stats

        # 保存管线结果
        result_path = self.data_dir / f"pipeline_result_{today}.json"
        result_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        logger.info("=" * 50)
        logger.info("管线完成!")
        logger.info("  Finder:    %d 条新发现", len(raw_leads))
        logger.info("  Analyzer:  %d 条分析", len(analyzed))
        logger.info("  Outreach:  %d 条文案", len(outreach))
        logger.info("  DB总计:    %d 条 (HOT=%d WARM=%d COLD=%d)",
                     stats["total"], stats["hot"], stats["warm"], stats["cold"])
        logger.info("  Reports:   %s", ROOT / "reports" / today)
        logger.info("=" * 50)

        return result

    def _run_finder(self) -> list[PlatformLead]:
        return self._finder.run()

    def _run_analyzer(self, raw_leads: Optional[list[PlatformLead]] = None) -> list:
        if not raw_leads:
            # 从数据库加载今天未分析的
            raw_leads = self._load_today_raw_leads()
        if raw_leads:
            return self._analyzer.run(raw_leads)
        return []

    def _run_outreach(self, analyzed=None) -> list:
        if analyzed is None:
            # 从数据库加载 HOT 线索
            hot = [h for h in self.db.list_hot() if not h.get("outreach_status")]
            # 转换为 AnalyzedLead
            analyzed = []
            for h in hot:
                pd = PlatformLead(
                    platform=h["platform"],
                    author_name=h["author_name"],
                    author_id=h["author_id"],
                    author_url=h["author_url"],
                    description=h.get("description", ""),
                )
                analyzed.append(AnalyzedLead(
                    platform_data=pd,
                    company_name=h.get("company_name", ""),
                    confidence=h.get("confidence", "LOW"),
                    priority="HOT",
                    icp_score=h.get("icp_score", 0),
                ))
        return self._outreach.run(analyzed)

    def _run_reporter(self, raw_leads=None, analyzed=None, outreach=None):
        stats = self.db.get_stats()
        self._reporter.run(
            raw_leads or [],
            analyzed or [],
            outreach or [],
            stats=stats,
        )

    def _load_today_raw_leads(self) -> list[PlatformLead]:
        """从数据库加载今天爬取的未分析数据"""
        with self.db._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM leads WHERE date(last_updated)=date('now') AND confidence='LOW'"
            ).fetchall()
        leads = []
        for r in rows:
            leads.append(PlatformLead(
                platform=r["platform"],
                author_name=r["author_name"],
                author_id=r["author_id"],
                author_url=r["author_url"],
                description=r.get("description", ""),
                follower_count=r.get("follower_count", 0),
                video_count=r.get("video_count", 0),
                is_verified=bool(r.get("is_verified", 0)),
            ))
        return leads
