"""Tests for scripts.lib.outreach."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib.outreach import OutreachGenerator


class TestOutreachGenerator:
    def test_substitute(self):
        g = OutreachGenerator({"company_name": "灵境AI", "founder": "张三"})
        r = g.substitute("Hello {company_name}, from {founder}")
        assert "灵境AI" in r and "张三" in r

    def test_substitute_missing(self):
        g = OutreachGenerator({"company_name": "T"})
        r = g.substitute("{company_name} ({unknown})")
        assert "{unknown}" in r

    def test_channel_routes(self):
        g = OutreachGenerator({})
        ch, tmpl = g.route_channel("funded")
        assert isinstance(ch, str) and isinstance(tmpl, str)

    def test_channel_default(self):
        g = OutreachGenerator({})
        ch, _ = g.route_channel("nonexistent")
        assert ch == "脉脉"

    def test_generate_first_message(self):
        g = OutreachGenerator({"company_name": "测试"})
        r = g.generate_first_message("您好 {company_name}", lead_type="funded")
        assert "测试" in r["message"]
        assert "follow_up_day1" in r

    def test_classify_funded(self):
        assert OutreachGenerator({}).classify_lead("内容制作", funded=True) == "funded"

    def test_classify_hiring(self):
        assert OutreachGenerator({}).classify_lead("内容制作", hiring=True) == "hiring"

    def test_classify_platform(self):
        assert OutreachGenerator({}).classify_lead("内容制作", is_platform=True) == "platform"

    def test_classify_soe(self):
        assert OutreachGenerator({}).classify_lead("国有企业") == "soe"
