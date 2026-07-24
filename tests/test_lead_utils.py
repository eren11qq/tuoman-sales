"""Tests for scripts.lib.lead_utils."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib.lead_utils import Lead, LeadDatabase


class TestLead:
    def test_default_date(self):
        lead = Lead(company_name="Test", platform_source="B站")
        assert lead.discovered_date != ""
        assert lead.confidence == "LOW"
        assert lead.contact_available == "NO"

    def test_fingerprint_dedup(self):
        a = Lead(company_name="灵境AI", platform_source="B站")
        b = Lead(company_name="灵境AI", platform_source="B站")
        c = Lead(company_name="灵境AI", platform_source="小红书")
        assert a.fingerprint == b.fingerprint
        assert a.fingerprint != c.fingerprint

    def test_fingerprint_case_insensitive(self):
        a = Lead(company_name="TestCorp", platform_source="B站")
        b = Lead(company_name="testcorp", platform_source="B站")
        assert a.fingerprint == b.fingerprint

    def test_to_csv_row(self):
        lead = Lead(
            company_name="灵境AI", platform_source="B站",
            signals_found="融资;团队", confidence="HIGH",
            contact_available="YES", notes="月产300部",
        )
        row = lead.to_csv_row()
        assert "灵境AI" in row
        assert "B站" in row
        assert "HIGH" in row

    def test_to_dict(self):
        lead = Lead(company_name="X", platform_source="抖音")
        d = lead.to_dict()
        assert d["company_name"] == "X"


class TestLeadDatabase:
    def test_empty(self):
        db = LeadDatabase()
        assert db.count() == 0
        assert db.get_all() == []

    def test_add_and_dedup(self):
        db = LeadDatabase()
        assert db.add(Lead("A", "B站")) is True
        assert db.add(Lead("A", "B站")) is False
        assert db.count() == 1

    def test_add_batch(self):
        db = LeadDatabase()
        added, dupes = db.add_batch([
            Lead("A", "B站"), Lead("A", "B站"), Lead("B", "小红书"),
        ])
        assert added == 2
        assert dupes == 1

    def test_get_by_confidence(self):
        db = LeadDatabase()
        db.add(Lead("A", "B站", confidence="HIGH"))
        db.add(Lead("B", "抖音", confidence="LOW"))
        assert len(db.get_by_confidence("HIGH")) == 1

    def test_save_and_load_json(self):
        db = LeadDatabase()
        db.add(Lead("A", "B站"))
        db.add(Lead("B", "抖音"))
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as f:
            path = f.name
        try:
            db.save_json(path)
            loaded = LeadDatabase.from_json(path)
            assert loaded.count() == 2
        finally:
            Path(path).unlink(missing_ok=True)
