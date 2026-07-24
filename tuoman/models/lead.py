"""
拓漫领域模型 — 原始平台数据 + 结构化分析结果 + SQLite 持久化
"""

import json
import sqlite3
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("tuoman.models")


# ── 数据模型 ─────────────────────────────────────────────


@dataclass
class PlatformLead:
    """原始平台爬取数据 — UP主搜索结果"""
    platform: str                     # B站 / 小红书 / 抖音 / YouTube
    author_name: str                  # UP主/博主名称
    author_id: str                    # 平台UID
    author_url: str                   # 主页链接
    description: str = ""             # 简介/签名
    video_count: int = 0              # 稿件数
    follower_count: int = 0           # 粉丝数
    is_verified: bool = False         # 是否企业认证
    keywords_matched: list[str] = field(default_factory=list)
    recent_titles: list[str] = field(default_factory=list)
    signals: dict = field(default_factory=dict)
    crawled_at: str = ""

    def __post_init__(self):
        if not self.crawled_at:
            self.crawled_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "PlatformLead":
        return cls(**d)


@dataclass
class AnalyzedLead:
    """LLM分析后的结构化lead"""
    platform_data: PlatformLead
    company_name: str = ""            # 提取的公司名/工作室名
    is_enterprise: bool = False       # 是否企业
    confidence: str = "LOW"          # HIGH / MEDIUM / LOW
    enterprise_signals: dict = field(default_factory=dict)
    bant: dict = field(default_factory=lambda: {
        "budget": 0, "authority": 0, "need": 0, "timeline": 0
    })
    icp_score: float = 0.0           # 0-100 ICP匹配度
    priority: str = "COLD"           # HOT / WARM / COLD
    analysis_summary: str = ""
    outreach_message: str = ""
    outreach_status: str = ""         # "" / "draft" / "sent" / "replied"
    follow_up_date: str = ""          # 下次跟进日期 (ISO)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["platform_data"] = self.platform_data.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AnalyzedLead":
        pd = PlatformLead.from_dict(d.pop("platform_data"))
        return cls(platform_data=pd, **d)


# ── 线索数据库 (SQLite) ─────────────────────────────────


class LeadDatabase:
    """SQLite 持久化线索库 — 支持去重、状态追踪、统计"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (Path(__file__).parent.parent.parent / "data" / "leads.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS leads (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform        TEXT NOT NULL,
                    author_id       TEXT NOT NULL,
                    author_name     TEXT NOT NULL,
                    author_url      TEXT NOT NULL,
                    description     TEXT DEFAULT '',
                    video_count     INTEGER DEFAULT 0,
                    follower_count  INTEGER DEFAULT 0,
                    is_verified     INTEGER DEFAULT 0,

                    company_name    TEXT DEFAULT '',
                    is_enterprise   INTEGER DEFAULT 0,
                    confidence      TEXT DEFAULT 'LOW',
                    enterprise_signals TEXT DEFAULT '{}',
                    bant            TEXT DEFAULT '{}',
                    icp_score       REAL DEFAULT 0.0,
                    priority        TEXT DEFAULT 'COLD',
                    analysis_summary TEXT DEFAULT '',

                    outreach_message  TEXT DEFAULT '',
                    outreach_status   TEXT DEFAULT '',
                    follow_up_date    TEXT DEFAULT '',

                    first_seen      TEXT NOT NULL,
                    last_updated    TEXT NOT NULL,
                    UNIQUE(platform, author_id)
                );

                CREATE INDEX IF NOT EXISTS idx_leads_priority  ON leads(priority);
                CREATE INDEX IF NOT EXISTS idx_leads_status    ON leads(outreach_status);
                CREATE INDEX IF NOT EXISTS idx_leads_updated   ON leads(last_updated);
            """)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    # ── 写入 ──

    def upsert_platform_lead(self, lead: PlatformLead) -> bool:
        """插入或更新原始lead，返回是否新增"""
        now = datetime.now().isoformat()
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id, first_seen FROM leads WHERE platform=? AND author_id=?",
                (lead.platform, lead.author_id),
            ).fetchone()

            is_new = existing is None
            first_seen = existing["first_seen"] if existing else now

            conn.execute("""
                INSERT INTO leads
                    (platform, author_id, author_name, author_url, description,
                     video_count, follower_count, is_verified, first_seen, last_updated)
                VALUES (?,?,?,?,?, ?,?,?,?,?)
                ON CONFLICT(platform, author_id) DO UPDATE SET
                    author_name=excluded.author_name,
                    description=excluded.description,
                    video_count=excluded.video_count,
                    follower_count=excluded.follower_count,
                    is_verified=excluded.is_verified,
                    last_updated=excluded.last_updated
            """, (
                lead.platform, lead.author_id, lead.author_name, lead.author_url,
                lead.description, lead.video_count, lead.follower_count,
                1 if lead.is_verified else 0,
                first_seen, now,
            ))
            return is_new

    def update_analysis(self, analyzed: AnalyzedLead):
        """写入LLM分析结果"""
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute("""
                UPDATE leads SET
                    company_name=?, is_enterprise=?, confidence=?,
                    enterprise_signals=?, bant=?, icp_score=?,
                    priority=?, analysis_summary=?,
                    outreach_message=?, outreach_status=?,
                    follow_up_date=?, last_updated=?
                WHERE platform=? AND author_id=?
            """, (
                analyzed.company_name,
                1 if analyzed.is_enterprise else 0,
                analyzed.confidence,
                json.dumps(analyzed.enterprise_signals, ensure_ascii=False),
                json.dumps(analyzed.bant, ensure_ascii=False),
                analyzed.icp_score,
                analyzed.priority,
                analyzed.analysis_summary,
                analyzed.outreach_message,
                analyzed.outreach_status,
                analyzed.follow_up_date,
                now,
                analyzed.platform_data.platform, analyzed.platform_data.author_id,
            ))

    def mark_outreach(self, platform: str, author_id: str, status: str,
                      message: str = "", follow_up: str = ""):
        """更新触达状态"""
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute("""
                UPDATE leads SET
                    outreach_status=?, outreach_message=?,
                    follow_up_date=?, last_updated=?
                WHERE platform=? AND author_id=?
            """, (status, message, follow_up or "", now, platform, author_id))

    # ── 查询 ──

    def get_stats(self) -> dict:
        """管线统计"""
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
            by_priority = {
                r["priority"]: r["cnt"]
                for r in conn.execute(
                    "SELECT priority, COUNT(*) as cnt FROM leads GROUP BY priority"
                ).fetchall()
            }
            by_status = {
                r["outreach_status"]: r["cnt"]
                for r in conn.execute(
                    "SELECT outreach_status, COUNT(*) as cnt FROM leads GROUP BY outreach_status"
                ).fetchall()
            }
            new_today = conn.execute(
                "SELECT COUNT(*) FROM leads WHERE date(first_seen)=date('now')"
            ).fetchone()[0]
            return {
                "total": total,
                "hot": by_priority.get("HOT", 0),
                "warm": by_priority.get("WARM", 0),
                "cold": by_priority.get("COLD", 0),
                "outreach_draft": by_status.get("draft", 0),
                "outreach_sent": by_status.get("sent", 0),
                "outreach_replied": by_status.get("replied", 0),
                "new_today": new_today,
            }

    def list_hot(self, limit: int = 20) -> list[dict]:
        """HOT 线索列表"""
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT * FROM leads
                WHERE priority='HOT'
                ORDER BY icp_score DESC, last_updated DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def list_pending_outreach(self, limit: int = 50) -> list[dict]:
        """待触达的 HOT/WARM 线索"""
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT * FROM leads
                WHERE priority IN ('HOT','WARM')
                  AND (outreach_status = '' OR outreach_status = 'draft')
                ORDER BY priority DESC, icp_score DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def search(self, query: str) -> list[dict]:
        """搜索线索"""
        pattern = f"%{query}%"
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT * FROM leads
                WHERE author_name LIKE ? OR company_name LIKE ? OR description LIKE ?
                LIMIT 50
            """, (pattern, pattern, pattern)).fetchall()
            return [dict(r) for r in rows]

    def get_by_id(self, lead_id: int) -> Optional[dict]:
        with self._conn() as conn:
            r = conn.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone()
            return dict(r) if r else None

    def export_json(self) -> list[dict]:
        """导出全量数据为JSON"""
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM leads ORDER BY last_updated DESC").fetchall()
            return [dict(r) for r in rows]
