"""
Stage 1: Finder — 用爬虫在B站搜索 AI漫剧 UP主，输出结构化原始数据
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional

from tuoman.models.lead import PlatformLead
from tuoman.crawlers.bilibili import BilibiliCrawler, DEFAULT_KEYWORDS

logger = logging.getLogger("tuoman.pipeline.finder")

DATA_DIR = Path(__file__).parent.parent.parent / "data"


class Finder:
    """爬取 B站，发现 AI漫剧 UP主"""

    def __init__(self, data_dir: Optional[Path] = None, headless: bool = True):
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless

    def run(self, keywords: Optional[list[str]] = None) -> list[PlatformLead]:
        """执行发现流程"""
        crawler = BilibiliCrawler(headless=self.headless)
        leads = crawler.search(keywords or DEFAULT_KEYWORDS)

        # 持久化
        today = date.today().isoformat()
        out_path = self.data_dir / f"raw_leads_{today}.json"
        out_path.write_text(
            json.dumps([l.to_dict() for l in leads], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("原始数据已保存: %s (%d 条)", out_path, len(leads))

        # 同时更新总库
        db_path = self.data_dir / "leads_db.json"
        if db_path.exists():
            existing = json.loads(db_path.read_text(encoding="utf-8"))
        else:
            existing = []
        existing_ids = {e["author_id"] for e in existing}
        new_count = 0
        for lead in leads:
            if lead.author_id not in existing_ids:
                existing.append(lead.to_dict())
                existing_ids.add(lead.author_id)
                new_count += 1
        db_path.write_text(
            json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        logger.info("总库已更新: %s (%d 总, %d 新增)", db_path, len(existing), new_count)

        return leads
