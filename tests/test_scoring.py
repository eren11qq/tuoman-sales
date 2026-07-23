"""Tests for scripts.lib.scoring."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.lib.scoring import (
    compute_signal_score,
    BANTScores,
    compute_icp_score,
    icp_tier,
    compute_combined_score,
    priority_tier,
)


class TestSignalScoring:
    def test_perfect_score(self):
        score = compute_signal_score(
            {"funding": 3, "hiring": 3, "product": 3, "team": 3, "contact": 3, "pain_match": 3},
            {"funding": 1, "hiring": 1}
        )
        assert score >= 9.0
        assert score <= 10.0

    def test_minimum_score(self):
        score = compute_signal_score(
            {"funding": 0, "hiring": 0, "product": 0, "team": 0, "contact": 0, "pain_match": 0}
        )
        assert score == 0.0

    def test_partial_score(self):
        score = compute_signal_score(
            {"funding": 2, "hiring": 2, "product": 1, "team": 1, "contact": 0, "pain_match": 1}
        )
        assert 3.0 <= score <= 7.0


class TestBANT:
    def test_hot_bant(self):
        bant = BANTScores(budget=3, authority=3, need=3, timeline=3)
        assert bant.total == 12
        assert bant.tier == "HOT"

    def test_warm_bant(self):
        bant = BANTScores(budget=2, authority=2, need=2, timeline=2)
        assert bant.total == 8
        assert bant.tier == "WARM"

    def test_cold_bant(self):
        bant = BANTScores(budget=0, authority=0, need=0, timeline=0)
        assert bant.total == 0
        assert bant.tier == "COLD"


class TestICPMatching:
    def test_perfect_icp(self):
        scores = {
            "industry": 3, "team_size": 3, "stage": 3, "geography": 3,
            "tech_maturity": 3, "pain_point_fit": 3, "budget_signal": 3,
        }
        pct = compute_icp_score(scores)
        assert pct == 100.0
        assert icp_tier(pct) == "CORE ICP"

    def test_mid_icp(self):
        scores = {
            "industry": 2, "team_size": 2, "stage": 1, "geography": 2,
            "tech_maturity": 1, "pain_point_fit": 2, "budget_signal": 1,
        }
        pct = compute_icp_score(scores)
        assert 40.0 <= pct <= 70.0
        assert icp_tier(pct) in ("ADJACENT ICP", "OUT OF SCOPE")

    def test_empty_icp(self):
        scores = {}
        pct = compute_icp_score(scores)
        assert pct == 0.0
        assert icp_tier(pct) == "OUT OF SCOPE"


class TestCombinedRanking:
    def test_hot_combined(self):
        bant = BANTScores(budget=3, authority=3, need=3, timeline=3)
        score = compute_combined_score(signal_score=9.0, bant=bant, icp_pct=90.0)
        assert score >= 8.0
        assert priority_tier(score) == "HOT"

    def test_cold_combined(self):
        bant = BANTScores(budget=0, authority=0, need=0, timeline=0)
        score = compute_combined_score(signal_score=1.0, bant=bant, icp_pct=20.0)
        assert score <= 4.0
        assert priority_tier(score) in ("COLD", "ON HOLD")

    def test_priority_tier_boundaries(self):
        assert priority_tier(8.0) == "HOT"
        assert priority_tier(7.0) == "WARM"
        assert priority_tier(5.0) == "COLD"
        assert priority_tier(3.0) == "ON HOLD"
