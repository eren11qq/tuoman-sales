"""
Stage 1: Finder — 多平台爬虫，发现 AI漫剧 UP主/博主

支持平台: B站、小红书 (可扩展)
使用 Playwright 直接爬取，不依赖外部 API。
"""

import logging
from pathlib import Path
from typing import Optional

from tuoman.models.lead import PlatformLead, LeadDatabase
from tuoman.crawlers.bilibili import BilibiliCrawler, DEFAULT_KEYWORDS as BILI_KEYWORDS
from tuoman.crawlers.xiaohongshu import XiaohongshuCrawler, DEFAULT_KEYWORDS as XHS_KEYWORDS

logger = logging.getLogger("tuoman.pipeline.finder")


class Finder:
    """多平台爬虫调度 — 发现 AI漫剧企业线索"""

    # 各平台默认关键词（平台可以覆盖）
    PLATFORM_KEYWORDS: dict[str, list[str]] = {
        "bilibili": BILI_KEYWORDS,
        "xiaohongshu": XHS_KEYWORDS,
    }

    def __init__(
        self,
        platforms: Optional[list[str]] = None,
        headless: bool = True,
        data_dir: Optional[Path] = None,
    ):
        self.platforms = platforms or list(self.PLATFORM_KEYWORDS.keys())
        self.headless = headless
        self.data_dir = data_dir or (Path(__file__).parent.parent.parent / "data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = LeadDatabase(self.data_dir / "leads.db")

    def run(self, keywords: Optional[dict[str, list[str]]] = None) -> list[PlatformLead]:
        """执行全平台发现流程

        Args:
            keywords: {platform: [keyword, ...]} — 覆盖默认关键词
        Returns:
            本次新发现的 PlatformLead 列表
        """
        merged_keywords = {**self.PLATFORM_KEYWORDS, **(keywords or {})}
        all_new_leads: list[PlatformLead] = []

        for platform in self.platforms:
            kw = merged_keywords.get(platform, [])
            if not kw:
                logger.info("跳过平台 %s: 无关键词", platform)
                continue

            try:
                raw = self._crawl_platform(platform, kw)
                new_leads = self._dedup_and_save(raw, platform)
                all_new_leads.extend(new_leads)
            except Exception as e:
                logger.error("平台 %s 爬取失败: %s", platform, e, exc_info=True)

        logger.info(
            "Finder 完成: 本次新增 %d 条 (累计 %d)",
            len(all_new_leads),
            self.db.get_stats()["total"],
        )
        return all_new_leads

    def _crawl_platform(self, platform: str, keywords: list[str]) -> list[PlatformLead]:
        """调用对应平台的爬虫"""
        logger.info("【%s】开始爬取 (%d 个关键词)", platform, len(keywords))

        if platform == "bilibili":
            crawler = BilibiliCrawler(headless=self.headless)
            return crawler.search(keywords)
        elif platform == "xiaohongshu":
            crawler = XiaohongshuCrawler(headless=self.headless)
            return crawler.search(keywords)
        else:
            logger.warning("未知平台: %s, 跳过", platform)
            return []

    def _dedup_and_save(self, leads: list[PlatformLead], platform: str) -> list[PlatformLead]:
        """去重入库，返回新增的 lead"""
        new_leads: list[PlatformLead] = []
        for lead in leads:
            try:
                is_new = self.db.upsert_platform_lead(lead)
                if is_new:
                    new_leads.append(lead)
            except Exception as e:
                logger.warning("入库失败 %s/%s: %s", platform, lead.author_id, e)

        logger.info("  %s: %d 条中 %d 条新增", platform, len(leads), len(new_leads))
        return new_leads
