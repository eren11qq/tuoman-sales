#!/usr/bin/env python3
"""
拓漫 TouMan — 每日获客管线
用法: python scripts/tuoman_daily.py

依次执行:
  1. lead-finder — 扫描各平台新线索
  2. company-researcher — 深度调研新线索
  3. enterprise-filter — 打分排序
  4. daily-report — 生成日报

输出: ~/.hermes/reports/{date}/
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
REPORT_DIR = Path.home() / ".hermes" / "reports" / datetime.now().strftime("%Y-%m-%d")

HERMES_CMD = [sys.executable, "-m", "hermes_cli.main"]


def run_skill(skill_name: str, prompt: str) -> dict:
    """Run a single skill via hermes oneshot mode."""
    print(f"\n{'='*60}")
    print(f">> Running: {skill_name}")
    print(f"{'='*60}")

    result = subprocess.run(
        [*HERMES_CMD, "oneshot", "--skill", skill_name, prompt],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        timeout=600,
    )

    if result.returncode != 0:
        print(f"WARN {skill_name} non-zero exit: {result.returncode}")
        print(result.stderr[-500:])
        return {"skill": skill_name, "status": "error", "error": result.stderr[-500:]}

    print(f"OK {skill_name} done")
    return {"skill": skill_name, "status": "ok", "output": result.stdout[-2000:]}


def main():
    today = datetime.now()
    print(f"TouMan Daily Pipeline — {today.strftime('%Y-%m-%d %H:%M')}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    results.append(run_skill(
        "lead-finder",
        f"Scan Bilibili/Xiaohongshu/Douyin/YouTube for new AI comic drama leads. Date: {today.strftime('%Y-%m-%d')}. Return only new leads from this week."
    ))

    results.append(run_skill(
        "company-researcher",
        "Deep research on today's new leads: funding, team, products, pain points, buying signals."
    ))

    results.append(run_skill(
        "enterprise-filter",
        "Score all leads with 3-mode ranking: Signal Scoring + BANT + ICP Matching. Output priority-sorted list."
    ))

    results.append(run_skill(
        "daily-report",
        f"Generate daily outreach report. Date: {today.strftime('%Y-%m-%d')}. Include new leads, hot leads requiring action, follow-up calendar, pipeline movement."
    ))

    report_file = REPORT_DIR / "pipeline_result.json"
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "date": today.isoformat(),
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    ok_count = sum(1 for r in results if r["status"] == "ok")
    print(f"\n{'='*60}")
    print(f"Pipeline done: {ok_count}/{len(results)} steps OK")
    print(f"Reports: {REPORT_DIR}")
    print(f"{'='*60}")

    return 0 if ok_count == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
