"""
小红书爬虫 — 搜索 AI漫剧 博主，提取企业信号

搜索小红书作者/笔记，从 profile 页提取企业信息。
"""

import logging
import re
from typing import Optional
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

from tuoman.models.lead import PlatformLead

logger = logging.getLogger("tuoman.crawlers.xiaohongshu")

# 搜索关键词
DEFAULT_KEYWORDS = [
    "AI漫剧工作室",
    "AI短剧制作",
    "AI漫画团队",
    "AI动画公司",
    "AI漫剧 招聘",
    "AI漫剧 融资",
    "AI短剧接单",
    "AI视频创业",
]

# 企业信号关键词
ENTERPRISE_SIGNAL_WORDS = [
    "工作室", "公司", "团队", "企业",
    "商务合作", "合作", "招聘", "招人",
    "创始人", "CEO",
    "官方", "认证",
]


class XiaohongshuCrawler:
    """小红书爬虫 — 搜索AI漫剧博主并提取企业信号"""

    SEARCH_URL = "https://www.xiaohongshu.com/search_result"
    MAX_PAGES = 2

    def __init__(self, headless: bool = True, timeout: int = 30000):
        self.headless = headless
        self.timeout = timeout

    def search(self, keywords: Optional[list[str]] = None) -> list[PlatformLead]:
        """搜索多个关键词，返回去重后的博主列表"""
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
                logger.info("[小红书] 搜索关键词: %s", keyword)
                leads = self._search_keyword(page, keyword)
                for lead in leads:
                    if lead.author_id not in seen_uids:
                        seen_uids.add(lead.author_id)
                        results.append(lead)
                logger.info("  → 新发现 %d 个博主（累计 %d）", len(leads), len(results))

            browser.close()

        logger.info("[小红书] 完成: 共发现 %d 个博主", len(results))
        return results

    def _search_keyword(self, page, keyword: str) -> list[PlatformLead]:
        """搜索单个关键词"""
        leads: list[PlatformLead] = []

        for page_num in range(1, self.MAX_PAGES + 1):
            try:
                params = urlencode({"keyword": keyword, "page": page_num})
                url = f"{self.SEARCH_URL}?{params}"
                logger.debug("  GET %s", url)
                page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
                page.wait_for_timeout(3000)

                # 提取搜索页中的作者链接
                author_links = self._extract_author_links(page, keyword)
                if not author_links:
                    logger.debug("  第%d页无结果", page_num)
                    break

                for entry in author_links:
                    user_id = entry["user_id"]
                    try:
                        detail = self._get_user_detail(page, user_id)
                        if detail:
                            detail.keywords_matched = [keyword]
                            leads.append(detail)
                    except Exception as e:
                        logger.warning("  获取博主 %s 详情失败: %s", user_id, e)

            except PWTimeout:
                logger.warning("  第%d页超时", page_num)
                break
            except Exception as e:
                logger.warning("  第%d页异常: %s", page_num, e)
                break

        return leads

    def _extract_author_links(self, page, keyword: str) -> list[dict]:
        """从搜索结果提取作者链接"""
        entries = []
        try:
            # 小红书搜索结果中的作者链接
            links = page.eval_on_selector_all(
                "a[href*='user']",
                "els => els.map(el => ({href: el.href, text: el.innerText.trim()}))",
            )
            seen = set()
            for link in links or []:
                uid_match = re.search(r"user/([0-9a-f]+)", link.get("href", ""))
                if uid_match:
                    uid = uid_match.group(1)
                    if uid not in seen:
                        seen.add(uid)
                        entries.append({"user_id": uid, "name": link.get("text", "")})
        except Exception as e:
            logger.debug("  提取搜索结果失败: %s", e)
        return entries

    def _get_user_detail(self, page, user_id: str) -> Optional[PlatformLead]:
        """访问用户 profile 页"""
        profile_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
        try:
            page.goto(profile_url, wait_until="domcontentloaded", timeout=self.timeout)
            page.wait_for_timeout(3000)

            # 提取用户名
            name = ""
            try:
                el = page.query_selector(".username, .user-name, [class*='name']")
                if el:
                    name = el.inner_text().strip()
            except Exception:
                pass

            # 提取简介
            desc = ""
            try:
                el = page.query_selector(".desc, .user-desc, [class*='desc']")
                if el:
                    desc = el.inner_text().strip()
            except Exception:
                pass

            # 提取粉丝数、笔记数
            note_count = 0
            follower_count = 0
            try:
                stats = page.query_selector_all(".count, [class*='count']")
                texts = [s.inner_text().strip() for s in (stats or [])]
                for i, t in enumerate(texts):
                    num = self._parse_number(t)
                    if i == 0:
                        note_count = num
                    elif i == 1:
                        follower_count = num
            except Exception:
                pass

            # 企业认证检测
            is_verified = False
            try:
                badge = page.query_selector("[class*='verify'], [class*='badge']")
                if badge:
                    is_verified = True
            except Exception:
                pass

            signals = self._detect_signals(desc)

            return PlatformLead(
                platform="小红书",
                author_name=name or user_id,
                author_id=user_id,
                author_url=profile_url,
                description=desc,
                video_count=note_count,
                follower_count=follower_count,
                is_verified=is_verified,
                signals=signals,
            )

        except PWTimeout:
            logger.debug("  博主 %s profile 超时", user_id)
        except Exception as e:
            logger.debug("  获取博主 %s 异常: %s", user_id, e)

        return None

    def _detect_signals(self, text: str) -> dict:
        signals = {}
        for word in ENTERPRISE_SIGNAL_WORDS:
            if word in text:
                signals[word] = True
        return signals

    @staticmethod
    def _parse_number(text: str) -> int:
        text = text.replace(",", "").replace(" ", "")
        match = re.search(r"([\d.]+)\s*万", text)
        if match:
            return int(float(match.group(1)) * 10000)
        match = re.search(r"(\d+)", text)
        return int(match.group(1)) if match else 0
