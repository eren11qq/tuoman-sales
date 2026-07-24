"""
CLI 单元测试 — 参数解析、子命令路由
"""

import pytest
from pathlib import Path
from tuoman.models.lead import LeadDatabase, PlatformLead


class TestCLICommands:
    """CLI 子命令逻辑测试（不触发网络请求）"""

    @pytest.fixture
    def db_with_leads(self, tmp_path: Path) -> LeadDatabase:
        db = LeadDatabase(tmp_path / "test.db")
        for i in range(3):
            lead = PlatformLead(
                platform="B站",
                author_name=f"工作室{i}",
                author_id=str(i),
                author_url=f"https://bilibili.com/{i}",
            )
            db.upsert_platform_lead(lead)
        return db

    def test_list_hot_empty(self, tmp_path: Path):
        """空数据库 list hot 应返回空"""
        db = LeadDatabase(tmp_path / "empty.db")
        assert db.list_hot() == []

    def test_list_pending_outreach(self, db_with_leads: LeadDatabase):
        """待触达列表"""
        pending = db_with_leads.list_pending_outreach()
        # 默认全是 COLD, 所以 pending 应为空
        assert len(pending) == 0

    def test_get_stats_formula(self, db_with_leads: LeadDatabase):
        """统计格式正确"""
        s = db_with_leads.get_stats()
        assert "total" in s
        assert "hot" in s
        assert "warm" in s
        assert "cold" in s
        assert s["total"] == 3

    def test_search_no_result(self, db_with_leads: LeadDatabase):
        """不存在的搜索词返回空"""
        assert db_with_leads.search("不存在的关键词") == []


class TestCLIParser:
    def test_run_stage_valid(self):
        """验证允许的 stage 名称"""
        from tuoman.pipeline.runner import PipelineRunner
        assert "finder" in PipelineRunner.STAGES
        assert "analyzer" in PipelineRunner.STAGES
        assert "outreach" in PipelineRunner.STAGES
        assert "reporter" in PipelineRunner.STAGES
        assert len(PipelineRunner.STAGES) == 4

    def test_db_path_resolution(self):
        """数据库路径应可解析"""
        from tuoman.models.lead import LeadDatabase
        db = LeadDatabase()
        assert db.db_path is not None
        assert str(db.db_path).endswith("leads.db")
