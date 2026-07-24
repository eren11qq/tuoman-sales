"""
拓漫领域模型 — 原始平台数据 + 结构化分析结果
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class PlatformLead:
    """原始平台爬取数据 — B站UP主搜索结果"""
    platform: str                     # B站
    author_name: str                  # UP主名称
    author_id: str                    # UID
    author_url: str                   # space 主页链接
    description: str = ""             # UP主简介/签名
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

    def to_dict(self) -> dict:
        d = asdict(self)
        d["platform_data"] = self.platform_data.to_dict()
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AnalyzedLead":
        pd = PlatformLead.from_dict(d.pop("platform_data"))
        return cls(platform_data=pd, **d)
