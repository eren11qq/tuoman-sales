"""领域模型单元测试"""

from tuoman.models.lead import PlatformLead, AnalyzedLead


def test_platform_lead_defaults():
    lead = PlatformLead(platform="B站", author_name="测试工作室", author_id="12345", author_url="https://space.bilibili.com/12345")
    assert lead.platform == "B站"
    assert lead.author_id == "12345"
    assert lead.crawled_at != ""
    assert not lead.is_verified
    assert lead.follower_count == 0


def test_platform_lead_with_signals():
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


def test_platform_lead_serialization():
    lead = PlatformLead(platform="B站", author_name="测试", author_id="1", author_url="https://space.bilibili.com/1")
    d = lead.to_dict()
    restored = PlatformLead.from_dict(d)
    assert restored.author_name == lead.author_name
    assert restored.author_id == lead.author_id


def test_analyzed_lead_defaults():
    pd = PlatformLead(platform="B站", author_name="测试", author_id="1", author_url="https://space.bilibili.com/1")
    al = AnalyzedLead(platform_data=pd)
    assert al.confidence == "LOW"
    assert al.priority == "COLD"
    assert al.company_name == ""


def test_analyzed_lead_hot():
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
    )
    assert al.is_enterprise
    assert al.priority == "HOT"
    assert al.icp_score == 85.0


def test_analyzed_lead_serialization():
    pd = PlatformLead(platform="B站", author_name="测试工作室", author_id="3", author_url="https://space.bilibili.com/3")
    al = AnalyzedLead(platform_data=pd, company_name="测试工作室", confidence="MEDIUM", priority="WARM")
    d = al.to_dict()
    restored = AnalyzedLead.from_dict(d)
    assert restored.company_name == al.company_name
    assert restored.confidence == al.confidence
    assert restored.platform_data.author_id == "3"
