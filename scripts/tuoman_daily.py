#!/usr/bin/env python3
"""
拓漫 TouMan — 每日获客管线 (Hermes Agent Grade)

Architecture:
  Orchestrates 5 pipeline stages using Hermes Agent oneshot (-z) for LLM
  inference, then structures results with lib/ data modules.

  Stage 1: lead-finder      → Hermes discovers leads → LeadDatabase stores
  Stage 2: company-researcher → Hermes researches → research/ dir
  Stage 3: enterprise-filter  → Hermes signals + scoring.py computes scores
  Stage 4: outreach-generator → Hermes drafts + outreach.py substitutes
  Stage 5: daily-report       → report_gen.py assembles final markdown

  Data flows between stages via structured files (JSON + parsed objects).
  Each stage is checkpointed so resume works after partial failure.

Usage:
    python scripts/tuoman_daily.py                  # full pipeline
    python scripts/tuoman_daily.py --stage lead-finder  # single stage
    python scripts/tuoman_daily.py --weekly          # weekly mode
    python scripts/tuoman_daily.py --resume           # resume from checkpoint
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, date
from pathlib import Path
from typing import Optional

import yaml

try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exit_code
except ImportError:
    # Fallback: no-op retry if tenacity not installed
    def retry(*a, **kw):
        def deco(f):
            return f
        return deco
    stop_after_attempt = None

# ─── lib/ imports ─────────────────────────────────────────────────────────
from scripts.lib.lead_utils import Lead, LeadDatabase
from scripts.lib.scoring import (
    compute_signal_score, BANTScores, compute_icp_score,
    compute_combined_score, priority_tier, icp_tier,
)
from scripts.lib.outreach import OutreachGenerator
from scripts.lib.report_gen import PipelineState, generate_daily_report

# ─── Paths ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
REPORT_DIR = Path.home() / ".hermes" / "reports"
CHECKPOINT_FILE = PROJECT_ROOT / "data" / "pipeline_checkpoint.json"
LEADS_DB_FILE = PROJECT_ROOT / "data" / "leads_db.json"
HERMES_CMD = [sys.executable, "-m", "hermes_cli.main"]

# ─── Logging ───────────────────────────────────────────────────────────────
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("tuoman.pipeline")

# ─── Retry config ──────────────────────────────────────────────────────────
MAX_RETRIES = 3
ONESHOT_TIMEOUT = 600  # seconds; overridable via env TUOMAN_TIMEOUT


def _get_oneshot_timeout() -> int:
    try:
        return int(os.environ.get("TUOMAN_TIMEOUT", str(ONESHOT_TIMEOUT)))
    except (TypeError, ValueError):
        return ONESHOT_TIMEOUT


# ─── Stage Prompts ─────────────────────────────────────────────────────────
# Externalized as dict so prompts are version-controllable and editable
# without touching Python code.  Override via PROMPTS_FILE env var.
DEFAULT_PROMPTS = {
    "lead-finder": (
        "You are an AI漫剧 lead discovery specialist. "
        "Use the lead-finder skill instructions.\n\n"
        "Scan Bilibili, Xiaohongshu, Douyin, and YouTube for new AI漫剧/AI短剧 "
        "companies, studios, and production teams. Today: {date}.\n\n"
        "Output each lead as a single pipe-delimited row:\n"
        "company_name | platform_source | signals_found | confidence | contact_available | notes\n\n"
        "RULES:\n"
        "1. ONLY enterprise-level leads (companies, studios, teams)\n"
        "2. NO individual creators or tutorial accounts\n"
        "3. confidence must be HIGH / MEDIUM / LOW\n"
        "4. If no new leads found, output exactly: NO_NEW_LEADS"
    ),
    "company-researcher": (
        "You are a business research analyst. Use the company-researcher skill instructions.\n\n"
        "Research these {count} AI漫剧 leads in depth. For EACH lead, investigate:\n"
        "- Funding history, team size, hiring activity\n"
        "- Products, tech stack, monthly output\n"
        "- Pain points, purchase signals, decision makers\n\n"
        "Leads to research:\n{leads_text}\n\n"
        "Output format per lead \u2014 a JSON object with keys:\n"
        "company_name, funding_summary, team_size, hiring_velocity, products, "
        "pain_points, purchase_signals, decision_makers, recommended_channel, notes\n\n"
        "Wrap all objects in a JSON array."
    ),
    "enterprise-filter": (
        "You are a lead scoring specialist. Use the enterprise-filter skill instructions.\n\n"
        "Score these {count} AI漫剧 leads. For EACH lead:\n"
        "1. Assign raw signal scores (0-3 per category): funding, hiring, product, team, contact, pain_match\n"
        "2. Assign BANT scores (0-3 per criterion): budget, authority, need, timeline\n"
        "3. Assign ICP dimension scores (0-3): industry, team_size, stage, geography, "
        "tech_maturity, pain_point_fit, budget_signal\n\n"
        "Leads:\n{leads_text}\n\n"
        "Output JSON array, each object:\n"
        "company_name, signal_scores:{{funding,hiring,product,team,contact,pain_match}}, "
        "bonuses:{{funding,hiring,product,team}}, "
        "bant:{{budget,authority,need,timeline}}, "
        "icp:{{industry,team_size,stage,geography,tech_maturity,pain_point_fit,budget_signal}}"
    ),
    "outreach-generator": (
        "You are a sales copywriter. Use the outreach-generator skill instructions.\n\n"
        "Generate personalized outreach messages for these HOT leads:\n{leads_text}\n\n"
        "For EACH lead, produce:\n"
        "- Channel recommendation (email / \u8109\u8109 / LinkedIn) with reasoning\n"
        "- Personalized message body\n"
        "- Follow-up plan (Day 1, Day 3, Day 7)\n\n"
        "Output JSON array:\n"
        "company_name, channel, template_letter, message, follow_up_day1, follow_up_day3, follow_up_day7"
    ),
    "daily-report": (
        "You are a pipeline reporting specialist. Use the daily-report skill instructions.\n\n"
        "Generate a {mode} pipeline report for AI漫剧 lead generation.\n"
        "Date: {date}\n\n"
        "Pipeline status:\n"
        "- Total leads in database: {total_leads}\n"
        "- New leads this session: {new_leads}\n"
        "- HOT leads: {hot_count}\n"
        "- WARM leads: {warm_count}\n"
        "- COLD leads: {cold_count}\n\n"
        "Recent activity:\n{activity}\n\n"
        "Output: structured markdown report with sections:\n"
        "Executive Summary, New Leads, Hot Leads, Follow-up Calendar, Pipeline Movement, Industry Monitoring"
    ),
}


def _load_prompts() -> dict:
    """Load prompts from YAML file or env override, falling back to DEFAULT_PROMPTS."""
    prompts_file = os.environ.get("TUOMAN_PROMPTS_FILE", "")
    if prompts_file and Path(prompts_file).exists():
        try:
            with open(prompts_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning("Failed to load prompts file %s: %s", prompts_file, e)
    return dict(DEFAULT_PROMPTS)


# ─── Oneshot runner with retry ────────────────────────────────────────────

class OneshotError(Exception):
    """Raised when Hermes oneshot returns non-zero after retries."""


@retry(
    stop=stop_after_attempt(MAX_RETRIES) if stop_after_attempt else None,
    wait=wait_exponential(multiplier=2, min=4, max=60),
    retry=retry_if_exit_code(lambda c: c != 0),
)
def run_oneshot(skill_name: str, prompt: str) -> str:
    """Run a Hermes oneshot with retry. Returns FULL stdout (NO truncation)."""
    timeout = _get_oneshot_timeout()
    logger.info("Stage=%s timeout=%ds prompt=%s...",
                skill_name, timeout, prompt[:60].replace("\n", " "))
    result = subprocess.run(
        [*HERMES_CMD, "-z", prompt],
        capture_output=True, text=True,
        cwd=str(PROJECT_ROOT), timeout=timeout,
    )
    if result.returncode != 0:
        stderr_full = result.stderr or ""
        logger.error("oneshot exit %d (stage=%s). stderr (%d chars): %s",
                     result.returncode, skill_name, len(stderr_full), stderr_full[:500])
        raise OneshotError(f"exit {result.returncode}: {stderr_full}")

    stdout = result.stdout or ""
    logger.info("Stage=%s OK \u2014 %d chars stdout", skill_name, len(stdout))
    return stdout


# ─── Stage Implementations ─────────────────────────────────────────────────

def stage_lead_finder(prompts: dict, db: LeadDatabase, mode: str, date_str: str) -> list[Lead]:
    """Stage 1: Discover new leads via Hermes, parse into Lead objects."""
    prompt = prompts["lead-finder"].format(date=date_str)
    stdout = run_oneshot("lead-finder", prompt)

    new_leads: list[Lead] = []
    if not stdout or "NO_NEW_LEADS" in stdout:
        logger.info("lead-finder: no new leads found")
        return new_leads

    for line in stdout.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("|") or line.startswith("company_name"):
            continue
        if "|" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        lead = Lead(
            company_name=parts[0],
            platform_source=parts[1] if len(parts) > 1 else "unknown",
            signals_found=parts[2] if len(parts) > 2 else "",
            confidence=parts[3] if len(parts) > 3 else "LOW",
            contact_available=parts[4] if len(parts) > 4 else "NO",
            notes=parts[5] if len(parts) > 5 else "",
            batch_id=date_str,
        )
        new_leads.append(lead)

    added, dupes = db.add_batch(new_leads)
    logger.info("lead-finder: %d leads parsed, %d new, %d dupes", len(new_leads), added, dupes)
    db.save_json(str(LEADS_DB_FILE))
    return new_leads


def stage_company_researcher(prompts: dict, leads: list[Lead], date_str: str) -> list[dict]:
    """Stage 2: Deep research on new leads. Receives leads from stage 1."""
    if not leads:
        logger.info("company-researcher: no leads to research, skipping")
        return []

    lead_summary = "\n".join(
        f"- {l.company_name} ({l.platform_source}, {l.confidence})"
        for l in leads[:10]
    )
    prompt = prompts["company-researcher"].format(
        count=min(len(leads), 10),
        leads_text=lead_summary,
    )
    stdout = run_oneshot("company-researcher", prompt)

    research_dir = PROJECT_ROOT / "reports" / date_str / "research"
    research_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    try:
        start = stdout.find("[")
        end = stdout.rfind("]") + 1
        if start >= 0 and end > start:
            results = json.loads(stdout[start:end])
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("company-researcher: JSON parse failed: %s", e)
        (research_dir / "raw_output.txt").write_text(stdout, encoding="utf-8")
        return results

    for r in results:
        name = r.get("company_name", "unknown").replace(" ", "_")
        (research_dir / f"{name}.json").write_text(
            json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    logger.info("company-researcher: %d companies researched", len(results))
    return results


def stage_enterprise_filter(prompts: dict, db: LeadDatabase, date_str: str) -> list[dict]:
    """Stage 3: Score leads using LLM signals + scoring.py for STRUCTURED computation."""
    all_leads = db.get_all()
    if not all_leads:
        logger.info("enterprise-filter: no leads, skipping")
        return []

    lead_summary = "\n".join(
        f"- {l.company_name}: platform={l.platform_source}, confidence={l.confidence}"
        for l in all_leads
    )
    prompt = prompts["enterprise-filter"].format(
        count=len(all_leads),
        leads_text=lead_summary,
    )
    stdout = run_oneshot("enterprise-filter", prompt)

    scored: list[dict] = []
    try:
        start = stdout.find("[")
        end = stdout.rfind("]") + 1
        if start >= 0 and end > start:
            scored = json.loads(stdout[start:end])
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("enterprise-filter: JSON parse failed: %s", e)
        return scored

    ranked = []
    for entry in scored:
        name = entry.get("company_name", "unknown")
        sig_scores = {k: int(v) for k, v in entry.get("signal_scores", {}).items() if isinstance(v, (int, float))}
        bonuses = {k: int(v) for k, v in entry.get("bonuses", {}).items() if isinstance(v, (int, float))}
        bant_raw = entry.get("bant", {})
        icp_raw = entry.get("icp", {})

        sig_score = compute_signal_score(sig_scores, bonuses)
        bant = BANTScores(
            budget=int(bant_raw.get("budget", 0)),
            authority=int(bant_raw.get("authority", 0)),
            need=int(bant_raw.get("need", 0)),
            timeline=int(bant_raw.get("timeline", 0)),
        )
        icp_pct = compute_icp_score(
            {k: int(v) for k, v in icp_raw.items() if isinstance(v, (int, float))}
        )
        combined = compute_combined_score(sig_score, bant, icp_pct)

        ranked.append({
            "company_name": name,
            "signal_score": round(sig_score, 1),
            "bant_total": bant.total,
            "bant_tier": bant.tier,
            "icp_fit_pct": icp_pct,
            "icp_tier": icp_tier(icp_pct),
            "combined_score": combined,
            "priority": priority_tier(combined),
        })

    ranked.sort(key=lambda x: x["combined_score"], reverse=True)

    filter_dir = PROJECT_ROOT / "reports" / date_str
    filter_dir.mkdir(parents=True, exist_ok=True)
    (filter_dir / "ranked_leads.json").write_text(
        json.dumps(ranked, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    hot = sum(1 for r in ranked if r["priority"] == "HOT")
    warm = sum(1 for r in ranked if r["priority"] == "WARM")
    cold = sum(1 for r in ranked if r["priority"] == "COLD")
    logger.info("enterprise-filter: %d scored, HOT=%d WARM=%d COLD=%d", len(ranked), hot, warm, cold)
    return ranked


def stage_outreach_generator(prompts: dict, ranked_leads: list[dict], date_str: str) -> list[dict]:
    """Stage 4: Generate outreach messages for HOT leads."""
    hot_leads = [r for r in ranked_leads if r["priority"] == "HOT"]
    if not hot_leads:
        logger.info("outreach-generator: no HOT leads, skipping")
        return []

    lead_text = "\n".join(
        f"- {r['company_name']} (score={r['combined_score']}, icp={r['icp_fit_pct']}%)"
        for r in hot_leads
    )
    prompt = prompts["outreach-generator"].format(leads_text=lead_text)
    stdout = run_oneshot("outreach-generator", prompt)

    results: list[dict] = []
    try:
        start = stdout.find("[")
        end = stdout.rfind("]") + 1
        if start >= 0 and end > start:
            results = json.loads(stdout[start:end])
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning("outreach-generator: JSON parse failed: %s", e)
        return results

    outreach_dir = PROJECT_ROOT / "reports" / date_str / "outreach"
    outreach_dir.mkdir(parents=True, exist_ok=True)

    for msg in results:
        name = msg.get("company_name", "unknown").replace(" ", "_")
        (outreach_dir / f"{name}.json").write_text(
            json.dumps(msg, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    logger.info("outreach-generator: %d messages", len(results))
    return results


def stage_daily_report(prompts: dict, db: LeadDatabase, ranked: list[dict],
                       new_leads: list[Lead], mode: str, date_str: str) -> str:
    """Stage 5: Generate daily/weekly report using report_gen.py + Hermes."""
    state = PipelineState()

    hot = [{"company": r["company_name"], "score": r["combined_score"],
             "location": "", "stage": "NEW", "last_touch": "",
             "next_action": "Contact this week"}
            for r in ranked if r["priority"] == "HOT"]
    warm = [r for r in ranked if r["priority"] == "WARM"]
    cold = [r for r in ranked if r["priority"] == "COLD"]
    new_lead_data = [{"company": l.company_name, "priority": l.confidence,
                      "source": l.platform_source, "signal": l.signals_found}
                     for l in new_leads]

    for r in ranked:
        state.update_lead(r["company_name"], "NEW", r["priority"])

    prompt = prompts["daily-report"].format(
        mode=mode, date=date_str,
        total_leads=db.count(), new_leads=len(new_leads),
        hot_count=len(hot), warm_count=len(warm), cold_count=len(cold),
        activity=f"New leads: {len(new_leads)}, Scored: {len(ranked)}",
    )
    md_report = generate_daily_report(
        report_date=date_str, pipeline=state,
        hot_leads=hot, new_leads=new_lead_data,
    )
    llm_stdout = run_oneshot("daily-report", prompt)

    report_dir = PROJECT_ROOT / "reports" / date_str
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "pipeline_report.md").write_text(md_report, encoding="utf-8")
    (report_dir / "pipeline_report_llm.md").write_text(llm_stdout, encoding="utf-8")
    state.save(str(report_dir / "pipeline_state.json"))

    logger.info("daily-report: saved to %s", report_dir)
    return md_report


# ─── Checkpoint ────────────────────────────────────────────────────────────

def save_checkpoint(completed_stages: list[str]) -> None:
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {"completed_stages": completed_stages, "timestamp": datetime.now().isoformat()}
    CHECKPOINT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Checkpoint saved: %s", completed_stages)


def load_checkpoint() -> list[str]:
    if not CHECKPOINT_FILE.exists():
        return []
    try:
        data = json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
        stages = data.get("completed_stages", [])
        logger.info("Checkpoint loaded: %d stages completed", len(stages))
        return stages
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.warning("Checkpoint load failed: %s", e)
        return []


# ─── Main Pipeline ─────────────────────────────────────────────────────────

def run_pipeline(stage_filter: Optional[str] = None,
                 mode: str = "daily",
                 resume: bool = False) -> int:
    date_str = date.today().isoformat()
    prompts = _load_prompts()
    completed = load_checkpoint() if resume else []

    if LEADS_DB_FILE.exists():
        db = LeadDatabase.from_json(str(LEADS_DB_FILE))
        logger.info("Loaded %d leads from %s", db.count(), LEADS_DB_FILE)
    else:
        db = LeadDatabase()
        logger.info("New lead database")

    # Stage 1
    new_leads: list[Lead] = []
    if (not stage_filter or stage_filter == "lead-finder") and "lead-finder" not in completed:
        logger.info("=== Stage 1: lead-finder ===")
        try:
            new_leads = stage_lead_finder(prompts, db, mode, date_str)
            completed.append("lead-finder")
            save_checkpoint(completed)
        except Exception as e:
            logger.error("lead-finder failed: %s", e, exc_info=True)
            if not resume:
                return 1
    else:
        logger.info("lead-finder: skipped")

    # Stage 2: receives new_leads from stage 1
    if (not stage_filter or stage_filter == "company-researcher") and "company-researcher" not in completed:
        logger.info("=== Stage 2: company-researcher ===")
        try:
            stage_company_researcher(prompts, new_leads, date_str)
            completed.append("company-researcher")
            save_checkpoint(completed)
        except Exception as e:
            logger.error("company-researcher failed: %s", e, exc_info=True)
            if not resume:
                return 1
    else:
        logger.info("company-researcher: skipped")

    # Stage 3: reads from DB (populated by stage 1)
    ranked: list[dict] = []
    if (not stage_filter or stage_filter == "enterprise-filter") and "enterprise-filter" not in completed:
        logger.info("=== Stage 3: enterprise-filter ===")
        try:
            ranked = stage_enterprise_filter(prompts, db, date_str)
            completed.append("enterprise-filter")
            save_checkpoint(completed)
        except Exception as e:
            logger.error("enterprise-filter failed: %s", e, exc_info=True)
            if not resume:
                return 1
    else:
        logger.info("enterprise-filter: skipped")

    # Stage 4: receives ranked from stage 3
    if (not stage_filter or stage_filter == "outreach-generator") and "outreach-generator" not in completed:
        logger.info("=== Stage 4: outreach-generator ===")
        try:
            stage_outreach_generator(prompts, ranked, date_str)
            completed.append("outreach-generator")
            save_checkpoint(completed)
        except Exception as e:
            logger.error("outreach-generator failed: %s", e, exc_info=True)
            if not resume:
                return 1
    else:
        logger.info("outreach-generator: skipped")

    # Stage 5: receives ranked + new_leads from previous stages
    if (not stage_filter or stage_filter == "daily-report") and "daily-report" not in completed:
        logger.info("=== Stage 5: daily-report ===")
        try:
            stage_daily_report(prompts, db, ranked, new_leads, mode, date_str)
            completed.append("daily-report")
            save_checkpoint(completed)
        except Exception as e:
            logger.error("daily-report failed: %s", e, exc_info=True)
            if not resume:
                return 1
    else:
        logger.info("daily-report: skipped")

    logger.info("=" * 50)
    logger.info("Pipeline complete! Stages: %s", completed)
    logger.info("Reports: %s", PROJECT_ROOT / "reports" / date_str)
    logger.info("Lead DB: %s (%d leads)", LEADS_DB_FILE, db.count())
    logger.info("=" * 50)
    return 0


def main():
    parser = argparse.ArgumentParser(description="拓漫 TouMan \u6bcf\u65e5\u83b7\u5ba2\u7ba1\u7ebf")
    parser.add_argument("--stage", choices=[
        "lead-finder", "company-researcher", "enterprise-filter",
        "outreach-generator", "daily-report"
    ], help="\u53ea\u8fd0\u884c\u5355\u4e2a\u6b65\u9aa4")
    parser.add_argument("--weekly", action="store_true", help="\u5468\u6a21\u5f0f")
    parser.add_argument("--resume", action="store_true", help="\u4ece\u68c0\u67e5\u70b9\u6062\u590d")
    args = parser.parse_args()

    mode = "weekly" if args.weekly else "daily"
    logger.info("TouMan %s Pipeline starting", mode.capitalize())

    return run_pipeline(
        stage_filter=args.stage,
        mode=mode,
        resume=args.resume,
    )


if __name__ == "__main__":
    sys.exit(main())
