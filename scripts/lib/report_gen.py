"""
Daily/weekly pipeline report generator.

Used by daily-report skill for structured markdown report generation.
"""

import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional


class PipelineState:
    """Tracks lead status transitions for pipeline movement reporting."""

    STATUSES = ["NEW", "TOUCHED", "ENGAGED", "MEETING", "NEGOTIATING", "CLOSED_WON", "CLOSED_LOST", "STALE"]

    def __init__(self, state_file: Optional[str] = None):
        self.state_file = state_file
        self.data: dict = {
            "last_report_date": "",
            "leads": {},
        }
        if state_file and Path(state_file).exists():
            self._load(state_file)

    def _load(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def save(self, path: Optional[str] = None) -> None:
        target = path or self.state_file
        if target:
            with open(target, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)

    def update_lead(self, name: str, status: str, priority: str) -> dict:
        """Update a lead's status. Returns before/after diff."""
        old_status = self.data["leads"].get(name, {}).get("status", "")
        self.data["leads"][name] = {
            "status": status,
            "priority": priority,
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
        }
        return {"lead": name, "from": old_status, "to": status}

    def movements(self, since_date: str = "") -> list[dict]:
        """Get list of status changes since a given date."""
        since = since_date or self.data.get("last_report_date", "")
        result = []
        for name, info in self.data["leads"].items():
            updated = info.get("last_updated", "")
            if since and updated >= since:
                result.append({
                    "lead": name,
                    "status": info["status"],
                    "priority": info["priority"],
                    "updated": updated,
                })
        return result


def pipeline_health_indicator(
    hot_leads: int,
    days_since_last_touch: int,
    new_leads_this_week: int,
) -> str:
    """Determine pipeline health: GREEN / YELLOW / RED."""
    if hot_leads >= 3 and days_since_last_touch <= 2 and new_leads_this_week >= 1:
        return "GREEN"
    elif hot_leads >= 1 and days_since_last_touch <= 7:
        return "YELLOW"
    else:
        return "RED"


def generate_daily_report(
    report_date: str,
    pipeline: PipelineState,
    hot_leads: list[dict],
    new_leads: list[dict],
    industry_updates: Optional[list[dict]] = None,
    follow_ups: Optional[list[dict]] = None,
) -> str:
    """
    Generate a daily pipeline report as markdown.

    Args:
        report_date: Date string YYYY-MM-DD.
        pipeline: Current pipeline state tracker.
        hot_leads: List of HOT lead dicts with keys: company, score, location, stage, last_touch, next_action.
        new_leads: List of NEW lead dicts with keys: company, priority, source, signal.
        industry_updates: Optional list of funding/competitor/news dicts.
        follow_ups: Optional list of scheduled touches.

    Returns:
        Markdown report string.
    """
    active_leads = pipeline.data["leads"]
    hot_count = len(hot_leads)
    touch_days = 0  # simplified
    new_count = len(new_leads)
    health = pipeline_health_indicator(hot_count, touch_days, new_count)

    lines = [
        f"# Daily Pipeline Report — {report_date}",
        "",
        "## Executive Summary",
        "",
        f"**Pipeline Health:** {health}",
        "",
        f"- **Active leads in pipeline:** {len(active_leads)}",
        f"- **Requiring action today:** {hot_count}",
    ]

    if hot_leads:
        lines.append(f"- **Highlight:** {hot_leads[0].get('company', 'N/A')} — top priority")
    lines.append("")

    # New leads
    lines.extend(["## New Leads", ""])
    if new_leads:
        lines.append("| Company | Priority | Source | Key Signal |")
        lines.append("|---|---|---|---|")
        for lead in new_leads:
            lines.append(
                f"| {lead['company']} | {lead.get('priority', '')} "
                f"| {lead.get('source', '')} | {lead.get('signal', '')} |"
            )
    else:
        lines.append("*No new leads since last report.*")
    lines.append("")

    # Hot leads
    lines.extend(["## Hot Leads — Requires Action", ""])
    for lead in hot_leads:
        lines.extend([
            f"### {lead.get('score', '?')}/10 — {lead['company']} ({lead.get('location', '')})",
            f"**Stage:** {lead.get('stage', 'NEW')} | "
            f"**Last Touch:** {lead.get('last_touch', 'None')} | "
            f"**Next Action:** {lead.get('next_action', 'TBD')}",
            "",
        ])

    # Follow-up calendar
    lines.extend([f"## Follow-up Calendar — {report_date}", ""])
    if follow_ups:
        lines.append("| Time | Lead | Channel | Action |")
        lines.append("|---|---|---|---|")
        for fu in follow_ups:
            lines.append(
                f"| {fu.get('time', '')} | {fu.get('company', '')} "
                f"| {fu.get('channel', '')} | {fu.get('action', '')} |"
            )
    else:
        lines.append("*No follow-ups scheduled for today.*")
    lines.append("")

    # Pipeline movement
    movements = pipeline.movements(pipeline.data.get("last_report_date", ""))
    lines.extend(["## Pipeline Movement", ""])
    if movements:
        lines.append("| Lead | From | To | Date |")
        lines.append("|---|---|---|---|")
        for m in movements:
            lines.append(
                f"| {m['lead']} | {m.get('from', '—')} | {m['status']} | {m['updated']} |"
            )
    else:
        lines.append("*No movement since last report.*")
    lines.append("")

    # Industry monitoring
    lines.extend(["## Industry Monitoring", ""])
    if industry_updates:
        funding = [u for u in industry_updates if u.get("type") == "funding"]
        if funding:
            lines.extend(["### Funding & Investment News", "",
                          "| Company | Round | Amount | Investors | Implication |",
                          "|---|---|---|---|---|"])
            for f in funding:
                lines.append(
                    f"| {f['company']} | {f.get('round', '')} | {f.get('amount', '')} "
                    f"| {f.get('investors', '')} | {f.get('implication', '')} |"
                )
            lines.append("")
    else:
        lines.append("*No significant industry updates since last report.*")

    pipeline.data["last_report_date"] = report_date
    return "\n".join(lines)
