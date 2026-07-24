"""领域模型单元测试 — 数据模型、序列化、边界条件"""

from tuoman.models.lead import PlatformLead, AnalyzedLead


class TestPlatformLead:
    def test_defaults(self):
        lead = PlatformLead(
            platform="B站", author_name="测试工作室", author_id="12345",
            author_url="https://space.bilibili.com/12345",
        )
        assert lead.platform == "B站"
        assert lead.author_id == "12345"
        assert lead.crawled_at != ""
        assert not lead.is_verified
        assert lead.follower_count == 0

    def test_with_signals(self):
        lead = PlatformLead(
            platform="B站",
            author_name="AI漫剧工作室",
            author_id="999",
            author_url="https://space.bilibili.com/999",
            description="专注AI漫剧制作，商务合作请联系微信",
            video_count=120,
            follower_count=50000,
            is_verified=True,
            keywords_matched=["AI漫剧 工作室"],
            recent_titles=["AI漫剧第1集", "AI漫剧第2集"],
            signals={"工作室": True, "商务合作": True},
        )
        assert lead.is_verified
        assert lead.video_count == 120
        assert lead.follower_count == 50000
        assert len(lead.recent_titles) == 2

    def test_serialization(self):
        lead = PlatformLead(
            platform="B站", author_name="测试", author_id="1",
            author_url="https://space.bilibili.com/1",
        )
        d = lead.to_dict()
        restored = PlatformLead.from_dict(d)
        assert restored.author_name == lead.author_name
        assert restored.author_id == lead.author_id

    def test_all_platforms(self):
        for platform in ["B站", "小红书", "抖音", "YouTube"]:
            lead = PlatformLead(
                platform=platform, author_name="测试", author_id="1",
                author_url=f"https://{platform}.com/1",
            )
            assert lead.platform == platform

    def test_crawled_at_auto(self):
        lead = PlatformLead(
            platform="B站", author_name="测试", author_id="1",
            author_url="https://bilibili.com/1",
        )
        assert "T" in lead.crawled_at  # ISO format

    def test_empty_recent_titles(self):
        lead = PlatformLead(
            platform="B站", author_name="测试", author_id="1",
            author_url="https://bilibili.com/1",
        )
        assert lead.recent_titles == []


class TestAnalyzedLead:
    def test_defaults(self):
        pd = PlatformLead(platform="B站", author_name="测试", author_id="1", author_url="https://space.bilibili.com/1")
        al = AnalyzedLead(platform_data=pd)
        assert al.confidence == "LOW"
        assert al.priority == "COLD"
        assert al.company_name == ""

    def test_hot(self):
        pd = PlatformLead(platform="B站", author_name="大工作室", author_id="2", author_url="https://space.bilibili.com/2")
        al = AnalyzedLead(
            platform_data=pd,
            company_name="大工作室",
            is_enterprise=True,
            confidence="HIGH",
            bant={"budget": 3, "authority": 2, "need": 3, "timeline": 2},
            icp_score=85.0,
            priority="HOT",
            analysis_summary="强企业信号，高预算",
            outreach_status="draft",
            follow_up_date="2026-08-01",
        )
        assert al.is_enterprise
        assert al.priority == "HOT"
        assert al.icp_score == 85.0
        assert al.outreach_status == "draft"
        assert al.follow_up_date == "2026-08-01"

    def test_serialization(self):
        pd = PlatformLead(platform="B站", author_name="测试工作室", author_id="3", author_url="https://space.bilibili.com/3")
        al = AnalyzedLead(platform_data=pd, company_name="测试工作室", confidence="MEDIUM", priority="WARM")
        d = al.to_dict()
        restored = AnalyzedLead.from_dict(d)
        assert restored.company_name == al.company_name
        assert restored.confidence == al.confidence
        assert restored.platform_data.author_id == "3"

    def test_bant_defaults(self):
        pd = PlatformLead(platform="B站", author_name="测试", author_id="4", author_url="https://bilibili.com/4")
        al = AnalyzedLead(platform_data=pd)
        assert al.bant["budget"] == 0
        assert al.bant["authority"] == 0
        assert al.bant["need"] == 0
        assert al.bant["timeline"] == 0
