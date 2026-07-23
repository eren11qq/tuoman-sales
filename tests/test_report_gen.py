"""Tests for scripts.lib.report_gen."""

import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.lib.report_gen import (
    pipeline_health_indicator,
    generate_daily_report,
    PipelineState,
)


class TestPipelineHealth:
    def test_green(self):
        assert pipeline_health_indicator(hot_leads=5, days_since_last_touch=0, new_leads_this_week=3) == "GREEN"

    def test_yellow(self):
        assert pipeline_health_indicator(hot_leads=1, days_since_last_touch=3, new_leads_this_week=0) == "YELLOW"

    def test_red(self):
        assert pipeline_health_indicator(hot_leads=0, days_since_last_touch=10, new_leads_this_week=0) == "RED"

    def test_green_boundary(self):
        assert pipeline_health_indicator(hot_leads=3, days_since_last_touch=2, new_leads_this_week=1) == "GREEN"

    def test_yellow_boundary(self):
        assert pipeline_health_indicator(hot_leads=1, days_since_last_touch=7, new_leads_this_week=0) == "YELLOW"


class TestPipelineState:
    def test_empty_state(self):
        state = PipelineState()
        assert state.data["last_report_date"] == ""
        assert len(state.data["leads"]) == 0

    def test_update_lead(self):
        state = PipelineState()
        diff = state.update_lead("灵境AI", "NEW", "HOT")
        assert diff["lead"] == "灵境AI"
        assert diff["from"] == ""
        assert diff["to"] == "NEW"

    def test_update_tracks_status_change(self):
        state = PipelineState()
        state.update_lead("灵境AI", "NEW", "HOT")
        diff = state.update_lead("灵境AI", "TOUCHED", "HOT")
        assert diff["from"] == "NEW"
        assert diff["to"] == "TOUCHED"

    def test_movements(self):
        state = PipelineState()
        state.data["last_report_date"] = "2026-07-01"
        state.update_lead("灵境AI", "NEW", "HOT")
        state.data["leads"]["灵境AI"]["last_updated"] = "2026-07-23"
        moves = state.movements("2026-07-20")
        assert len(moves) >= 1

    def test_save_and_load(self):
        state = PipelineState()
        state.update_lead("测试公司", "NEW", "HOT")
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            path = f.name
        try:
            state.save(path)
            loaded = PipelineState(path)
            assert "测试公司" in loaded.data["leads"]
            assert loaded.data["leads"]["测试公司"]["status"] == "NEW"
        finally:
            os.unlink(path)


class TestGenerateReport:
    def test_daily_report_basic(self):
        state = PipelineState()
        state.update_lead("灵境AI", "NEW", "HOT")
        report = generate_daily_report(
            report_date="2026-07-23",
            pipeline=state,
            hot_leads=[{"company": "灵境AI", "score": "9.5", "location": "杭州",
                        "stage": "NEW", "last_touch": "None", "next_action": "脉脉触达"}],
            new_leads=[{"company": "灵境AI", "priority": "HOT", "source": "36氪", "signal": "3轮融资"}],
        )
        assert "Daily Pipeline Report — 2026-07-23" in report
        assert "灵境AI" in report
        assert "Executive Summary" in report
        assert "Hot Leads" in report or "Hot" in report

    def test_report_no_new_leads(self):
        state = PipelineState()
        report = generate_daily_report(
            report_date="2026-07-23",
            pipeline=state,
            hot_leads=[],
            new_leads=[],
        )
        assert "No new leads since last report" in report

    def test_report_with_industry_updates(self):
        state = PipelineState()
        report = generate_daily_report(
            report_date="2026-07-23",
            pipeline=state,
            hot_leads=[],
            new_leads=[],
            industry_updates=[{
                "type": "funding",
                "company": "八点八数字",
                "round": "Unknown",
                "amount": "近亿元",
                "investors": "北京泰中合",
                "implication": "集成合作机会",
            }],
        )
        assert "八点八数字" in report
