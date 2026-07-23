"""
Lead data structures, deduplication, and CSV formatting.

Used by lead-finder skill for structuring discovered leads.
"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Lead:
    """A discovered lead with enterprise qualification signals."""
    company_name: str
    platform_source: str  # B站 / 小红书 / 抖音 / YouTube / GitHub
    signals_found: str = ""  # semicolon-separated signal list
    confidence: str = "LOW"  # HIGH / MEDIUM / LOW
    contact_available: str = "NO"  # YES / NO
    notes: str = ""
    discovered_date: str = ""
    url: str = ""
    batch_id: str = ""

    def __post_init__(self):
        if not self.discovered_date:
            self.discovered_date = datetime.now().strftime("%Y-%m-%d")

    @property
    def fingerprint(self) -> str:
        """Unique identifier for dedup: company + platform."""
        raw = f"{self.company_name.strip().lower()}|{self.platform_source.strip()}"
        return hashlib.md5(raw.encode()).hexdigest()

    def to_csv_row(self) -> str:
        """Pipe-delimited CSV row matching lead-finder output schema."""
        return (
            f"{self.company_name} | {self.platform_source} | {self.signals_found} "
            f"| {self.confidence} | {self.contact_available} | {self.notes}"
        )

    def to_dict(self) -> dict:
        return asdict(self)


class LeadDatabase:
    """In-memory lead store with dedup and batch tracking."""

    def __init__(self, leads: Optional[list[Lead]] = None):
        self._leads: dict[str, Lead] = {}
        if leads:
            for lead in leads:
                self._leads[lead.fingerprint] = lead

    @classmethod
    def from_json(cls, path: str) -> "LeadDatabase":
        """Load leads from a JSON file."""
        import json
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            leads = [Lead(**item) for item in data]
            return cls(leads)
        except (FileNotFoundError, json.JSONDecodeError):
            return cls()

    def add(self, lead: Lead) -> bool:
        """Add a lead. Returns False if duplicate."""
        fp = lead.fingerprint
        if fp in self._leads:
            return False
        self._leads[fp] = lead
        return True

    def add_batch(self, leads: list[Lead]) -> tuple[int, int]:
        """Add multiple leads. Returns (added_count, duplicate_count)."""
        added = 0
        dupes = 0
        for lead in leads:
            if self.add(lead):
                added += 1
            else:
                dupes += 1
        return added, dupes

    def get_by_confidence(self, confidence: str) -> list[Lead]:
        return [l for l in self._leads.values() if l.confidence == confidence]

    def get_all(self) -> list[Lead]:
        return list(self._leads.values())

    def save_json(self, path: str) -> None:
        """Save all leads to a JSON file."""
        data = [l.to_dict() for l in self._leads.values()]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def count(self) -> int:
        return len(self._leads)
