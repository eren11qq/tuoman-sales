"""B站爬虫 — 信号检测和解析工具函数测试"""

from tuoman.crawlers.bilibili import BilibiliCrawler


crawler = BilibiliCrawler(headless=True)


def test_parse_number():
    assert crawler._parse_number("1.2万粉丝") == 12000
    assert crawler._parse_number("3.5万") == 35000
    assert crawler._parse_number("100") == 100
    assert crawler._parse_number("1,234") == 1234
    assert crawler._parse_number("10万") == 100000


def test_parse_number_zero():
    assert crawler._parse_number("") == 0
    assert crawler._parse_number("无数据") == 0


def test_detect_signals():
    signals = crawler._detect_signals("AI漫剧工作室，专注原创，商务合作请联系微信")
    assert signals.get("工作室") is True
    assert signals.get("商务合作") is True
    assert signals.get("招聘") is not True


def test_detect_signals_empty():
    assert crawler._detect_signals("") == {}


def test_detect_signals_hiring():
    signals = crawler._detect_signals("我们正在招聘AI动画师，欢迎加入")
    assert signals.get("招聘") is True
    assert signals.get("工作室") is not True


def test_detect_signals_company():
    signals = crawler._detect_signals("XX科技有限公司官方账号")
    assert signals.get("公司") is True
    assert signals.get("官方") is True
