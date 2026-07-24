"""
爬虫工具函数测试 — 信号检测、数字解析、数据清洗
"""

from tuoman.crawlers.bilibili import BilibiliCrawler
from tuoman.crawlers.xiaohongshu import XiaohongshuCrawler


class TestBilibiliCrawlerUtils:
    crawler = BilibiliCrawler(headless=True)

    def test_parse_number_wan(self):
        assert self.crawler._parse_number("1.2万粉丝") == 12000
        assert self.crawler._parse_number("3.5万") == 35000
        assert self.crawler._parse_number("10万") == 100000
        assert self.crawler._parse_number("100.5万") == 1005000

    def test_parse_number_raw(self):
        assert self.crawler._parse_number("100") == 100
        assert self.crawler._parse_number("1,234") == 1234

    def test_parse_number_zero(self):
        assert self.crawler._parse_number("") == 0
        assert self.crawler._parse_number("无数据") == 0
        assert self.crawler._parse_number("abc") == 0

    def test_detect_signals_workshop(self):
        signals = self.crawler._detect_signals("AI漫剧工作室，专注原创，商务合作请联系微信")
        assert signals.get("工作室") is True
        assert signals.get("商务合作") is True

    def test_detect_signals_empty(self):
        assert self.crawler._detect_signals("") == {}

    def test_detect_signals_hiring(self):
        signals = self.crawler._detect_signals("我们正在招聘AI动画师")
        assert signals.get("招聘") is True

    def test_detect_signals_company(self):
        signals = self.crawler._detect_signals("XX科技有限公司官方账号")
        assert signals.get("公司") is True
        assert signals.get("官方") is True

    def test_detect_signals_multiple(self):
        signals = self.crawler._detect_signals("AI漫剧工作室招聘CEO")
        assert signals.get("工作室") is True
        assert signals.get("招聘") is True
        assert signals.get("CEO") is True


class TestXiaohongshuCrawlerUtils:
    crawler = XiaohongshuCrawler(headless=True)

    def test_parse_number_wan(self):
        assert self.crawler._parse_number("1.2万") == 12000
        assert self.crawler._parse_number("10万") == 100000

    def test_parse_number_raw(self):
        assert self.crawler._parse_number("100") == 100
        assert self.crawler._parse_number("0") == 0

    def test_detect_signals(self):
        signals = self.crawler._detect_signals("AI漫剧工作室，招聘人才")
        assert signals.get("工作室") is True
        assert signals.get("招聘") is True

    def test_detect_signals_empty(self):
        assert self.crawler._detect_signals("") == {}
