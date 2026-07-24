"""
B站爬虫 — 搜索 AI漫剧 UP主，提取企业信号

MVP: 用 Playwright 打开 search.bilibili.com 搜索关键词，
从搜索结果提取 UP主信息，然后访问 space 页面获取详细资料。
"""

import logging
import re
import time
from typing import Optional
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

from tuoman.models.lead import PlatformLead

logger = logging.getLogger("tuoman.crawlers.bilibili")

# 搜索关键词 — 按精准度排序，越靠前越精准
DEFAULT_KEYWORDS = [
    "AI漫剧 工作室",
    "AI漫剧 原创",
    "AI动态漫 制作",
    "AI漫剧 商务合作",
    "AI短剧 制作 公司",
    "AI漫剧 招聘",
    "AIGC短剧 工作室",
    "AI漫画 团队",
]

# 企业信号关键词 — 出现在简介中视为企业信号
ENTERPRISE_SIGNAL_WORDS = [
    "工作室", "公司", "团队", "企业", "工作室成立于",
    "商务合作", "商务", "合作", "招聘", "招人",
    "创始人", "CEO", "创始人/CEO",
    "官方", "认证", "企业认证",
]


class BilibiliCrawler:
    """B站爬虫 — 搜索AI漫剧UP主并提取企业信号"""

    SEARCH_URL = "https://search.bilibili.com/all"
    MAX_PAGES = 2  # MVP: 每个关键词搜2页

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout

    def search(self, keywords: Optional[list[str]] = None) -> list[PlatformLead]:
        """搜索多个关键词，返回去重后的 UP主列表"""
        keywords = keywords or DEFAULT_KEYWORDS
        seen_uids: set[str] = set()
        results: list[PlatformLead] = []

        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            )
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                locale="zh-CN",
            )
            page = context.new_page()

            for keyword in keywords:
                logger.info("搜索关键词: %s", keyword)
                leads = self._search_keyword(page, keyword)
                for lead in leads:
                    if lead.author_id not in seen_uids:
                        seen_uids.add(lead.author_id)
                        results.append(lead)
                logger.info("  → 新发现 %d 个UP主（累计 %d）", len(leads), len(results))

            browser.close()

        logger.info("B站爬虫完成: 共发现 %d 个UP主", len(results))
        return results

    def _search_keyword(self, page, keyword: str) -> list[PlatformLead]:
        """搜索单个关键词，返回该关键词下的UP主"""
        leads: list[PlatformLead] = []

        for page_num in range(1, self.MAX_PAGES + 1):
            try:
                params = urlencode({"keyword": keyword, "page": page_num})
                url = f"{self.SEARCH_URL}?{params}"
                logger.debug("  GET %s", url)
                page.goto(url, wait_until="networkidle", timeout=self.timeout)

                # 等搜索结果加载
                page.wait_for_selector(".video-list-item,.bili-video-card", timeout=10000)

                # 提取搜索结果中的 UP主信息
                up_entries = self._extract_search_results(page, keyword)
                if not up_entries:
                    logger.debug("  第%d页无结果", page_num)
                    break

                # 对每个 UP主访问 space 页获取详细信息
                for entry in up_entries:
                    uid = entry["uid"]
                    try:
                        detail = self._get_up_detail(page, uid)
                        if detail:
                            detail.keywords_matched = [keyword]
                            leads.append(detail)
                    except Exception as e:
                        logger.warning("  获取UP主 %s 详情失败: %s", uid, e)

            except PWTimeout:
                logger.warning("  第%d页超时", page_num)
                break
            except Exception as e:
                logger.warning("  第%d页异常: %s", page_num, e)
                break

        return leads

    def _extract_search_results(self, page, keyword: str) -> list[dict]:
        """从搜索结果页提取 UP主信息"""
        entries = []
        try:
            # B站搜索结果每个视频项包含 UP主链接
            up_links = page.eval_on_selector_all(
                "a[href*='space.bilibili.com']",
                "els => els.map(el => ({href: el.href, text: el.innerText.trim()}))",
            )
            # 去重 by UID
            seen = set()
            for link in up_links or []:
                uid_match = re.search(r"space\.bilibili\.com/(\d+)", link.get("href", ""))
                if uid_match:
                    uid = uid_match.group(1)
                    if uid not in seen:
                        seen.add(uid)
                        entries.append({"uid": uid, "name": link.get("text", "")})
        except Exception as e:
            logger.debug("  提取搜索结果失败: %s", e)

        return entries

    def _get_up_detail(self, page, uid: str) -> Optional[PlatformLead]:
        """访问 UP 主 space 页，提取详细资料"""
        space_url = f"https://space.bilibili.com/{uid}"
        try:
            page.goto(space_url, wait_until="networkidle", timeout=self.timeout)
            page.wait_for_timeout(2000)  # 等页面渲染

            # 提取简介
            desc = ""
            try:
                desc_el = page.query_selector(".user-desc-text,.h-description")
                if desc_el:
                    desc = desc_el.inner_text().strip()
            except Exception:
                pass

            # 提取用户名
            name = ""
            try:
                name_el = page.query_selector(".h-name,.user-name")
                if name_el:
                    name = name_el.inner_text().strip()
            except Exception:
                pass

            # 提取粉丝数、稿件数
            video_count = 0
            follower_count = 0
            try:
                stats = page.query_selector_all(".n-data-v,.user-stat")
                for stat in stats or []:
                    text = stat.inner_text()
                    num = self._parse_number(text)
                    if "稿" in text or "视频" in text:
                        video_count = num
                    elif "粉丝" in text or "粉" in text:
                        follower_count = num
            except Exception:
                pass

            # 企业认证检测
            is_verified = False
            try:
                badge = page.query_selector(".verify-badge,.official-badge")
                if badge:
                    is_verified = True
            except Exception:
                pass

            # 企业信号检测
            signals = self._detect_signals(desc)

            # 最近作品标题
            recent_titles = []
            try:
                items = page.query_selector_all(".video-title,.title")
                for item in (items or [])[:5]:
                    t = item.inner_text().strip()
                    if t:
                        recent_titles.append(t)
            except Exception:
                pass

            return PlatformLead(
                platform="B站",
                author_name=name or uid,
                author_id=uid,
                author_url=space_url,
                description=desc,
                video_count=video_count,
                follower_count=follower_count,
                is_verified=is_verified,
                recent_titles=recent_titles,
                signals=signals,
            )

        except PWTimeout:
            logger.debug("  UP主 %s space页超时", uid)
        except Exception as e:
            logger.debug("  获取UP主 %s 详情异常: %s", uid, e)

        return None

    def _detect_signals(self, text: str) -> dict:
        """检测文本中的企业信号"""
        signals = {}
        for word in ENTERPRISE_SIGNAL_WORDS:
            if word in text:
                signals[word] = True
        return signals

    @staticmethod
    def _parse_number(text: str) -> int:
        """解析数字，如 '1.2万粉丝' → 12000"""
        text = text.replace(",", "").replace(" ", "")
        match = re.search(r"([\d.]+)\s*万", text)
        if match:
            return int(float(match.group(1)) * 10000)
        match = re.search(r"(\d+)", text)
        return int(match.group(1)) if match else 0
