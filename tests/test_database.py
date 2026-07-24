"""
LeadDatabase 单元测试 — SQLite 持久化 + CRUD + 统计
"""

import pytest
from pathlib import Path
from tuoman.models.lead import PlatformLead, AnalyzedLead, LeadDatabase


@pytest.fixture
def db(tmp_path: Path) -> LeadDatabase:
    return LeadDatabase(tmp_path / "test_leads.db")


@pytest.fixture
def sample_lead() -> PlatformLead:
    return PlatformLead(
        platform="B站",
        author_name="测试工作室",
        author_id="12345",
        author_url="https://space.bilibili.com/12345",
        description="专注AI漫剧制作，商务合作请私信",
        video_count=120,
        follower_count=50000,
        is_verified=True,
        keywords_matched=["AI漫剧 工作室"],
        recent_titles=["AI漫剧第1集", "AI漫剧第2集"],
        signals={"工作室": True, "商务合作": True},
    )


class TestLeadDatabase:
    def test_init_creates_table(self, db: LeadDatabase):
        """初始化应自动创建表"""
        stats = db.get_stats()
        assert stats["total"] == 0

    def test_upsert_new_lead(self, db: LeadDatabase, sample_lead: PlatformLead):
        """首次插入应返回 is_new=True"""
        is_new = db.upsert_platform_lead(sample_lead)
        assert is_new is True
        assert db.get_stats()["total"] == 1

    def test_upsert_duplicate(self, db: LeadDatabase, sample_lead: PlatformLead):
        """重复插入应返回 is_new=False"""
        db.upsert_platform_lead(sample_lead)
        is_new = db.upsert_platform_lead(sample_lead)
        assert is_new is False
        assert db.get_stats()["total"] == 1

    def test_upsert_updates_existing(self, db: LeadDatabase, sample_lead: PlatformLead):
        """重复插入应更新字段"""
        db.upsert_platform_lead(sample_lead)
        updated = PlatformLead(
            platform="B站",
            author_name="测试工作室（已更名）",
            author_id="12345",
            author_url="https://space.bilibili.com/12345",
            description="新的简介",
            video_count=200,
            follower_count=80000,
            is_verified=True,
        )
        db.upsert_platform_lead(updated)

        rows = db.export_json()
        assert len(rows) == 1
        assert rows[0]["author_name"] == "测试工作室（已更名）"
        assert rows[0]["video_count"] == 200

    def test_update_analysis(self, db: LeadDatabase, sample_lead: PlatformLead):
        """分析结果应正确写入"""
        db.upsert_platform_lead(sample_lead)

        analyzed = AnalyzedLead(
            platform_data=sample_lead,
            company_name="测试工作室",
            is_enterprise=True,
            confidence="HIGH",
            bant={"budget": 3, "authority": 2, "need": 3, "timeline": 2},
            icp_score=85.0,
            priority="HOT",
            analysis_summary="强企业信号，高预算",
            outreach_status="draft",
        )
        db.update_analysis(analyzed)

        rows = db.export_json()
        assert rows[0]["priority"] == "HOT"
        assert rows[0]["company_name"] == "测试工作室"
        assert rows[0]["outreach_status"] == "draft"

    def test_mark_outreach(self, db: LeadDatabase, sample_lead: PlatformLead):
        """触达状态更新"""
        db.upsert_platform_lead(sample_lead)
        db.mark_outreach("B站", "12345", "sent", "已发送触达消息", "2026-08-01")

        rows = db.export_json()
        assert rows[0]["outreach_status"] == "sent"

    def test_get_stats(self, db: LeadDatabase):
        """统计应正确聚合"""
        leads = [
            PlatformLead(platform="B站", author_name=f"工作室{i}", author_id=str(i),
                         author_url=f"https://bilibili.com/{i}")
            for i in range(5)
        ]
        for lead in leads:
            db.upsert_platform_lead(lead)

        stats = db.get_stats()
        assert stats["total"] == 5

    def test_search(self, db: LeadDatabase, sample_lead: PlatformLead):
        """搜索应返回匹配结果"""
        db.upsert_platform_lead(sample_lead)
        results = db.search("测试工作室")
        assert len(results) == 1

        results = db.search("不存在的关键词")
        assert len(results) == 0

    def test_list_hot(self, db: LeadDatabase, sample_lead: PlatformLead):
        """HOT 线索列表"""
        db.upsert_platform_lead(sample_lead)
        analyzed = AnalyzedLead(
            platform_data=sample_lead,
            company_name="测试工作室",
            confidence="HIGH",
            bant={"budget": 3, "authority": 2, "need": 3, "timeline": 2},
            icp_score=85.0,
            priority="HOT",
        )
        db.update_analysis(analyzed)

        hot = db.list_hot()
        assert len(hot) == 1

    def test_export_json(self, db: LeadDatabase, sample_lead: PlatformLead):
        """导出 JSON"""
        db.upsert_platform_lead(sample_lead)
        exported = db.export_json()
        assert len(exported) == 1
        assert exported[0]["author_id"] == "12345"


class TestDatabaseWithMultipleLeads:
    def test_multi_platform_dedup(self, db: LeadDatabase):
        """不同平台相同 author_id 算不同记录"""
        bilibili = PlatformLead(
            platform="B站", author_name="同一人", author_id="999",
            author_url="https://bilibili.com/999",
        )
        xhs = PlatformLead(
            platform="小红书", author_name="同一人", author_id="999",
            author_url="https://xiaohongshu.com/999",
        )
        assert db.upsert_platform_lead(bilibili) is True
        assert db.upsert_platform_lead(xhs) is True  # 不同平台，应新增
        assert db.get_stats()["total"] == 2

    def test_empty_db(self, db: LeadDatabase):
        """空数据库应返回空结果"""
        assert db.list_hot() == []
        assert db.list_pending_outreach() == []
        assert db.search("anything") == []
        assert db.get_by_id(1) is None
