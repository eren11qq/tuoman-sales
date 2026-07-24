"""
Pipeline 单元测试 — 优先级计算、数据流
"""

from tuoman.models.lead import PlatformLead, AnalyzedLead
from tuoman.pipeline.analyzer import Analyzer
from tuoman.pipeline.runner import PipelineRunner


class TestAnalyzerPriority:
    """Analyzer 优先级计算"""

    def test_hot_high_bant_icp(self):
        assert Analyzer._calc_priority("HIGH", {"budget": 3, "authority": 2, "need": 3, "timeline": 2}, 80) == "HOT"
        # bant_total=6, icp=70 => HOT (bant>=6 AND icp>=60)
        assert Analyzer._calc_priority("HIGH", {"budget": 2, "authority": 2, "need": 1, "timeline": 1}, 70) == "HOT"

    def test_warm_high_low_bant(self):
        assert Analyzer._calc_priority("HIGH", {"budget": 1, "authority": 1, "need": 1, "timeline": 1}, 40) == "WARM"
        # bant_total=12 BUT icp=30 < 40 => falls through to COLD
        assert Analyzer._calc_priority("HIGH", {"budget": 3, "authority": 3, "need": 3, "timeline": 3}, 30) == "COLD"

    def test_warm_medium_bant4(self):
        assert Analyzer._calc_priority("MEDIUM", {"budget": 2, "authority": 1, "need": 1, "timeline": 0}, 50) == "WARM"
        assert Analyzer._calc_priority("MEDIUM", {"budget": 9, "authority": 9, "need": 9, "timeline": 9}, 100) == "WARM"

    def test_cold_low(self):
        assert Analyzer._calc_priority("LOW", {"budget": 1, "authority": 1, "need": 1, "timeline": 1}, 50) == "COLD"
        assert Analyzer._calc_priority("LOW", {"budget": 0, "authority": 0, "need": 0, "timeline": 0}, 0) == "COLD"

    def test_cold_medium_low_bant(self):
        assert Analyzer._calc_priority("MEDIUM", {"budget": 1, "authority": 0, "need": 1, "timeline": 0}, 30) == "COLD"

    def test_edge_empty_bant(self):
        assert Analyzer._calc_priority("HIGH", {}, 80) == "COLD"
        assert Analyzer._calc_priority("MEDIUM", {}, 50) == "COLD"

    def test_edge_negative_icp(self):
        # icp=-10 < 40, falls to COLD
        assert Analyzer._calc_priority("HIGH", {"budget": 3, "authority": 3, "need": 3, "timeline": 3}, -10) == "COLD"

    def test_analyzed_lead_creation(self):
        pd = PlatformLead(
            platform="B站", author_name="工作室", author_id="1",
            author_url="https://bilibili.com/1",
        )
        al = AnalyzedLead(
            platform_data=pd,
            company_name="工作室",
            is_enterprise=True,
            confidence="HIGH",
            priority="HOT",
            icp_score=85.0,
        )
        assert al.company_name == "工作室"
        assert al.is_enterprise is True
        assert al.priority == "HOT"

    def test_analyzed_lead_defaults(self):
        pd = PlatformLead(
            platform="B站", author_name="未知", author_id="0",
            author_url="https://bilibili.com/0",
        )
        al = AnalyzedLead(platform_data=pd)
        assert al.confidence == "LOW"
        assert al.priority == "COLD"
        assert al.icp_score == 0.0
        assert al.outreach_message == ""

    def test_serialization_roundtrip(self):
        pd = PlatformLead(
            platform="B站", author_name="测试", author_id="1",
            author_url="https://bilibili.com/1",
            description="AI漫剧制作",
            video_count=50,
            follower_count=10000,
        )
        al = AnalyzedLead(
            platform_data=pd,
            company_name="测试工作室",
            confidence="HIGH",
            priority="HOT",
            icp_score=90.0,
        )
        d = al.to_dict()
        restored = AnalyzedLead.from_dict(d)
        assert restored.company_name == al.company_name
        assert restored.priority == al.priority
        assert restored.platform_data.author_id == "1"
        assert restored.platform_data.description == "AI漫剧制作"


class TestPipelineRunner:
    def test_stage_list(self):
        assert "finder" in PipelineRunner.STAGES
        assert len(PipelineRunner.STAGES) == 4

    def test_stage_validation(self):
        from tuoman.pipeline.runner import PipelineRunner
        # 验证 stage 名称
        for stage in PipelineRunner.STAGES:
            assert stage in ["finder", "analyzer", "outreach", "reporter"]
