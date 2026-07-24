"""
Pipeline Runner — 编排4个stage按序执行
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional

from tuoman.llm.client import LLMClient
from tuoman.models.lead import PlatformLead
from tuoman.pipeline.finder import Finder
from tuoman.pipeline.analyzer import Analyzer
from tuoman.pipeline.outreach import OutreachGenerator
from tuoman.pipeline.reporter import Reporter

logger = logging.getLogger("tuoman.pipeline.runner")

ROOT = Path(__file__).parent.parent.parent
DATA_DIR = ROOT / "data"


class PipelineRunner:
    """管线编排器 — 负责4 stage的调度和错误处理"""

    def __init__(
        self,
        headless: bool = True,
        model: str = "gpt-4o",
        data_dir: Optional[Path] = None,
    ):
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        llm = LLMClient(model=model)
        self._finder = Finder(data_dir=self.data_dir, headless=headless)
        self._analyzer = Analyzer(llm=llm, data_dir=self.data_dir)
        self._outreach = OutreachGenerator(llm=llm, data_dir=self.data_dir)
        self._reporter = Reporter(llm=llm, data_dir=self.data_dir)

    def run(self, keywords: Optional[list[str]] = None) -> dict:
        """执行完整管线"""
        today = date.today().isoformat()
        logger.info("=" * 50)
        logger.info("拓漫管线启动: %s", today)
        logger.info("=" * 50)

        result = {
            "date": today,
            "stage1_finder": {"status": "pending", "count": 0},
            "stage2_analyzer": {"status": "pending", "count": 0},
            "stage3_outreach": {"status": "pending", "count": 0},
            "stage4_reporter": {"status": "pending"},
        }

        # Stage 1: Finder
        try:
            logger.info("【Stage 1/4】Finder — B站爬取")
            raw_leads = self._finder.run(keywords)
            result["stage1_finder"]["status"] = "ok"
            result["stage1_finder"]["count"] = len(raw_leads)
        except Exception as e:
            logger.error("Finder 失败: %s", e, exc_info=True)
            result["stage1_finder"]["status"] = f"failed: {e}"
            raw_leads = []

        # Stage 2: Analyzer
        try:
            logger.info("【Stage 2/4】Analyzer — LLM分析")
            if not raw_leads:
                # 尝试从文件加载
                raw_file = self.data_dir / f"raw_leads_{today}.json"
                if raw_file.exists():
                    raw_data = json.loads(raw_file.read_text(encoding="utf-8"))
                    raw_leads = [PlatformLead.from_dict(d) for d in raw_data]
                    logger.info("从文件加载 %d 条原始数据", len(raw_leads))

            if raw_leads:
                analyzed = self._analyzer.run(raw_leads)
            else:
                analyzed = []
            result["stage2_analyzer"]["status"] = "ok"
            result["stage2_analyzer"]["count"] = len(analyzed)
        except Exception as e:
            logger.error("Analyzer 失败: %s", e, exc_info=True)
            result["stage2_analyzer"]["status"] = f"failed: {e}"
            analyzed = []

        # Stage 3: Outreach
        try:
            logger.info("【Stage 3/4】Outreach — 触达文案")
            outreach = self._outreach.run(analyzed)
            result["stage3_outreach"]["status"] = "ok"
            result["stage3_outreach"]["count"] = len(outreach)
        except Exception as e:
            logger.error("Outreach 失败: %s", e, exc_info=True)
            result["stage3_outreach"]["status"] = f"failed: {e}"
            outreach = []

        # Stage 4: Reporter
        try:
            logger.info("【Stage 4/4】Reporter — 日报")
            self._reporter.run(raw_leads, analyzed, outreach)
            result["stage4_reporter"]["status"] = "ok"
        except Exception as e:
            logger.error("Reporter 失败: %s", e, exc_info=True)
            result["stage4_reporter"]["status"] = f"failed: {e}"

        # 保存管线结果
        result_path = self.data_dir / f"pipeline_result_{today}.json"
        result_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        logger.info("=" * 50)
        logger.info("管线完成!")
        logger.info("  Finder:   %d UP主", result["stage1_finder"]["count"])
        logger.info("  Analyzer: %d 条", result["stage2_analyzer"]["count"])
        logger.info("  Outreach: %d 文案", result["stage3_outreach"]["count"])
        logger.info("  Reports:  %s", ROOT / "reports" / today)
        logger.info("=" * 50)

        return result
