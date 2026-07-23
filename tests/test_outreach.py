"""Tests for scripts.lib.outreach."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.lib.outreach import OutreachGenerator


class TestOutreachGenerator:
    def test_substitute_known_vars(self):
        gen = OutreachGenerator({"company_name": "灵境AI", "founder_name": "许金城"})
        result = gen.substitute("{founder_name}，恭喜{company_name}完成融资！")
        assert result == "许金城，恭喜灵境AI完成融资！"

    def test_substitute_unknown_var_kept(self):
        gen = OutreachGenerator({"company_name": "测试"})
        result = gen.substitute("{company_name} - {unknown_var}")
        assert result == "测试 - {unknown_var}"

    def test_substitute_empty_vars(self):
        gen = OutreachGenerator({})
        result = gen.substitute("{company_name}")
        assert result == "{company_name}"

    def test_route_channel_funded(self):
        gen = OutreachGenerator({})
        channel, template = gen.route_channel("funded")
        assert channel == "脉脉"
        assert template == "A"

    def test_route_channel_soe(self):
        gen = OutreachGenerator({})
        channel, template = gen.route_channel("soe")
        assert channel == "邮件"
        assert template == "E"

    def test_route_channel_unknown(self):
        gen = OutreachGenerator({})
        channel, template = gen.route_channel("nonexistent")
        assert template == "H"  # cold default

    def test_classify_lead(self):
        gen = OutreachGenerator({})
        assert gen.classify_lead("内容制作", funded=True) == "funded"
        assert gen.classify_lead("国有企业") == "soe"
        assert gen.classify_lead("内容制作", funded=False, hiring=True) == "hiring"
        assert gen.classify_lead("内容制作", is_platform=True) == "platform"
        assert gen.classify_lead("内容制作") == "content_capacity"

    def test_generate_first_message(self):
        gen = OutreachGenerator({"company_name": "灵境AI", "founder_name": "许金城"})
        result = gen.generate_first_message(
            "您好{founder_name}，看到{company_name}近期融资，恭喜！",
            lead_type="funded",
        )
        assert result["channel"] == "脉脉"
        assert result["template"] == "A"
        assert "灵境AI" in result["message"]
        assert "许金城" in result["message"]
        assert len(result["follow_up_day1"]) > 0
