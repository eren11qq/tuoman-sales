"""Tests for scripts.lib.report_gen."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib.report_gen import PipelineState, generate_daily_report, pipeline_health_indicator


class TestPipelineState:
    def test_empty(self):
        s = PipelineState()
        assert s.data["leads"] == {}

    def test_update_lead(self):
        s = PipelineState()
        d = s.update_lead("灵境AI", "NEW", "HOT")
        assert d["lead"] == "灵境AI" and d["from"] == "" and d["to"] == "NEW"

    def test_transition(self):
        s = PipelineState()
        s.update_lead("A", "NEW", "HOT")
        d = s.update_lead("A", "TOUCHED", "HOT")
        assert d["from"] == "NEW"

    def test_movements(self):
        s = PipelineState()
        s.data["last_report_date"] = "2026-01-01"
        s.update_lead("A", "NEW", "HOT")
        assert len(s.movements("2026-01-01")) >= 1

    def test_save_load(self):
        s = PipelineState()
        s.update_lead("A", "NEW", "HOT")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as f:
            path = f.name
        try:
            s.save(path)
            assert PipelineState(path).data["leads"]["A"]["status"] == "NEW"
        finally:
            Path(path).unlink(missing_ok=True)


class TestPipelineHealth:
    def test_green(self):
        assert pipeline_health_indicator(5, 1, 3) == "GREEN"

    def test_yellow(self):
        assert pipeline_health_indicator(2, 5, 0) == "YELLOW"

    def test_red(self):
        assert pipeline_health_indicator(0, 10, 0) == "RED"


class TestGenerateReport:
    def test_empty(self):
        s = PipelineState()
        r = generate_daily_report("2026-07-24", s, [], [])
        assert "Daily Pipeline Report" in r
        assert "2026-07-24" in r

    def test_with_data(self):
        s = PipelineState()
        s.update_lead("灵境AI", "NEW", "HOT")
        r = generate_daily_report("2026-07-24", s,
            [{"company":"灵境AI","score":9.5,"location":"","stage":"","last_touch":"","next_action":""}],
            [{"company":"灵境AI","priority":"HIGH","source":"B站","signal":"融资"}])
        assert "灵境AI" in r
        assert "B站" in r

    def test_follow_ups(self):
        r = generate_daily_report("2026-07-24", PipelineState(), [], [],
            follow_ups=[{"time":"09:00","company":"灵境AI","channel":"脉脉","action":"发送"}])
        assert "Follow-up Calendar" in r
        assert "09:00" in r
