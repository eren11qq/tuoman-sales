"""Tests for scripts.lib.lead_utils."""

import sys, json, tempfile, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.lib.lead_utils import Lead, LeadDatabase


class TestLead:
    def test_create_lead(self):
        lead = Lead(company_name="灵境AI", platform_source="B站")
        assert lead.company_name == "灵境AI"
        assert lead.platform_source == "B站"
        assert lead.confidence == "LOW"
        assert lead.discovered_date != ""

    def test_fingerprint_unique(self):
        a = Lead(company_name="灵境AI", platform_source="B站")
        b = Lead(company_name="灵境AI", platform_source="小红书")
        assert a.fingerprint != b.fingerprint

    def test_fingerprint_consistent(self):
        a = Lead(company_name="灵境AI", platform_source="B站")
        b = Lead(company_name="  灵境AI  ", platform_source="B站")
        assert a.fingerprint == b.fingerprint

    def test_csv_row(self):
        lead = Lead(
            company_name="灵境AI", platform_source="B站",
            signals_found="企业认证;3部连载", confidence="HIGH",
            contact_available="YES", notes="月产300部"
        )
        row = lead.to_csv_row()
        assert "灵境AI" in row
        assert "HIGH" in row
        assert "月产300部" in row

    def test_to_dict(self):
        lead = Lead(company_name="测试", platform_source="抖音")
        d = lead.to_dict()
        assert d["company_name"] == "测试"
        assert d["platform_source"] == "抖音"


class TestLeadDatabase:
    def test_empty_db(self):
        db = LeadDatabase()
        assert db.count() == 0

    def test_add_lead(self):
        db = LeadDatabase()
        lead = Lead(company_name="星迹互动", platform_source="36氪")
        assert db.add(lead) is True
        assert db.count() == 1

    def test_dedup(self):
        db = LeadDatabase()
        a = Lead(company_name="星迹互动", platform_source="36氪")
        b = Lead(company_name="星迹互动", platform_source="36氪")
        assert db.add(a) is True
        assert db.add(b) is False  # duplicate
        assert db.count() == 1

    def test_add_batch(self):
        db = LeadDatabase()
        leads = [
            Lead(company_name="A", platform_source="B站"),
            Lead(company_name="A", platform_source="B站"),  # duplicate
            Lead(company_name="B", platform_source="小红书"),
        ]
        added, dupes = db.add_batch(leads)
        assert added == 2
        assert dupes == 1

    def test_get_by_confidence(self):
        db = LeadDatabase()
        db.add(Lead(company_name="A", platform_source="B站", confidence="HIGH"))
        db.add(Lead(company_name="B", platform_source="抖音", confidence="LOW"))
        assert len(db.get_by_confidence("HIGH")) == 1
        assert len(db.get_by_confidence("LOW")) == 1

    def test_save_and_load_json(self):
        db = LeadDatabase()
        db.add(Lead(company_name="灵境AI", platform_source="融资新闻"))
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            path = f.name
        try:
            db.save_json(path)
            loaded = LeadDatabase.from_json(path)
            assert loaded.count() == 1
            leads = loaded.get_all()
            assert leads[0].company_name == "灵境AI"
        finally:
            os.unlink(path)
