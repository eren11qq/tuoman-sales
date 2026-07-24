"""Tests for scripts.lib.scoring."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib.scoring import (
    compute_signal_score, BANTScores, compute_icp_score,
    compute_combined_score, priority_tier, icp_tier,
)


class TestSignalScoring:
    def test_perfect(self):
        s = compute_signal_score(
            {k: 3 for k in ("funding","hiring","product","team","contact","pain_match")},
            {k: 1 for k in ("funding","hiring","product","team")},
        )
        assert abs(s - 10.0) < 0.01

    def test_zero(self):
        s = compute_signal_score(
            {k: 0 for k in ("funding","hiring","product","team","contact","pain_match")},
        )
        assert abs(s - 0.0) < 0.01

    def test_average(self):
        s = compute_signal_score({"funding":1,"hiring":2,"product":1,"team":1,"contact":2,"pain_match":2})
        assert 3.0 < s < 5.0

    def test_clamp_upper(self):
        s = compute_signal_score({k: 999 for k in ("funding","hiring","product","team","contact","pain_match")})
        assert s <= 10.0


class TestBANT:
    def test_hot(self):
        b = BANTScores(budget=3, authority=3, need=3, timeline=3)
        assert b.total == 12 and b.tier == "HOT"

    def test_warm(self):
        b = BANTScores(budget=2, authority=2, need=2, timeline=2)
        assert b.total == 8 and b.tier == "WARM"

    def test_cold(self):
        b = BANTScores(budget=1, authority=0, need=1, timeline=0)
        assert b.tier == "COLD"

    def test_boundary_hot(self):
        assert BANTScores(budget=3, authority=3, need=2, timeline=2).tier == "HOT"


class TestICP:
    def test_perfect(self):
        p = compute_icp_score({k: 3 for k in ("industry","team_size","stage","geography","tech_maturity","pain_point_fit","budget_signal")})
        assert abs(p - 100.0) < 0.1
        assert icp_tier(p) == "CORE ICP"

    def test_zero(self):
        assert abs(compute_icp_score({}) - 0.0) < 0.1
        assert icp_tier(0) == "OUT OF SCOPE"


class TestCombined:
    def test_hot_lead(self):
        sig = compute_signal_score({k: 3 for k in ("funding","hiring","product","team","contact","pain_match")},
                                    {k: 1 for k in ("funding","hiring","product","team")})
        bant = BANTScores(3, 3, 3, 3)
        icp = compute_icp_score({k: 3 for k in ("industry","team_size","stage","geography","tech_maturity","pain_point_fit","budget_signal")})
        c = compute_combined_score(sig, bant, icp)
        assert c > 9.0 and priority_tier(c) == "HOT"

    def test_priority_boundaries(self):
        assert priority_tier(8.0) == "HOT"
        assert priority_tier(7.9) == "WARM"
        assert priority_tier(6.0) == "WARM"
        assert priority_tier(5.9) == "COLD"
        assert priority_tier(3.9) == "ON HOLD"
