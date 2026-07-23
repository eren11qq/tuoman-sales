"""
Lead scoring engine: Signal Scoring, BANT qualification, ICP matching.

Used by enterprise-filter skill for structured lead ranking.
"""

from dataclasses import dataclass
from typing import Optional


def _clamp(value: float, low: float = 0.0, high: float = 10.0) -> float:
    return max(low, min(high, value))


# ─── Signal Scoring ──────────────────────────────────────────────────────────

SIGNAL_MAX_SCORES = {
    "funding": 4,    # 0-3 + 1 bonus
    "hiring": 4,     # 0-3 + 1 bonus
    "product": 4,    # 0-3 + 1 bonus
    "team": 4,       # 0-3 + 1 bonus
    "contact": 3,    # 0-3
    "pain_match": 3, # 0-3
}

SIGNAL_WEIGHTS = {
    "funding": 0.25,
    "hiring": 0.20,
    "product": 0.20,
    "team": 0.15,
    "contact": 0.10,
    "pain_match": 0.10,
}


def compute_signal_score(scores: dict[str, int], bonuses: Optional[dict[str, int]] = None) -> float:
    """
    Compute weighted signal score (0-10).

    Args:
        scores: Raw scores per category (0-3). Keys: funding, hiring, product, team, contact, pain_match
        bonuses: Optional bonus points per category (0-1).

    Returns:
        Normalized score 0-10.
    """
    bonuses = bonuses or {}
    raw_total = 0.0
    max_total = 0.0

    for category, weight in SIGNAL_WEIGHTS.items():
        max_score = SIGNAL_MAX_SCORES.get(category, 3)
        raw = scores.get(category, 0)
        bonus = bonuses.get(category, 0)
        category_score = (raw + bonus) / max_score * weight * 10
        raw_total += category_score
        max_total += weight * 10

    return _clamp(raw_total / max_total * 10) if max_total > 0 else 0.0


# ─── BANT Qualification ──────────────────────────────────────────────────────

@dataclass
class BANTScores:
    budget: int = 0     # 0-3
    authority: int = 0   # 0-3
    need: int = 0        # 0-3
    timeline: int = 0    # 0-3

    @property
    def total(self) -> int:
        return self.budget + self.authority + self.need + self.timeline

    @property
    def tier(self) -> str:
        if self.total >= 10:
            return "HOT"
        elif self.total >= 7:
            return "WARM"
        else:
            return "COLD"


# ─── ICP Matching ────────────────────────────────────────────────────────────

ICP_DIMENSIONS = [
    "industry",
    "team_size",
    "stage",
    "geography",
    "tech_maturity",
    "pain_point_fit",
    "budget_signal",
]


def compute_icp_score(dimension_scores: dict[str, int]) -> float:
    """
    Compute ICP fit percentage from 7 dimension scores (0-3 each).

    Args:
        dimension_scores: Dict mapping dimension name to score 0-3.

    Returns:
        Fit percentage 0-100.
    """
    total = 0
    max_total = len(ICP_DIMENSIONS) * 3
    for dim in ICP_DIMENSIONS:
        total += dimension_scores.get(dim, 0)
    return round((total / max_total) * 100, 1) if max_total > 0 else 0.0


def icp_tier(fit_pct: float) -> str:
    if fit_pct >= 80:
        return "CORE ICP"
    elif fit_pct >= 50:
        return "ADJACENT ICP"
    else:
        return "OUT OF SCOPE"


# ─── Combined Ranking ────────────────────────────────────────────────────────

def compute_combined_score(signal_score: float, bant: BANTScores, icp_pct: float) -> float:
    """
    Compute final priority score using weighted combination.

    Formula: Signal Score (40%) + BANT Score (35%) + ICP Fit (25%)
    """
    bant_normalized = (bant.total / 12.0) * 10
    icp_normalized = (icp_pct / 100.0) * 10

    combined = (
        signal_score * 0.40 +
        bant_normalized * 0.35 +
        icp_normalized * 0.25
    )
    return round(_clamp(combined), 1)


def priority_tier(score: float) -> str:
    if score >= 8.0:
        return "HOT"
    elif score >= 6.0:
        return "WARM"
    elif score >= 4.0:
        return "COLD"
    else:
        return "ON HOLD"
