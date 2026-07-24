---
name: daily-report
description: Daily pipeline report generator for AI漫剧 sales
platforms: [win32, linux]
argument-hint: "[--weekly]"
triggers:
  - "日报"
  - "daily-report"
  - "每日报告"
  - "周报"
  - "报告"
  - "汇总"
handoff: pipeline-{date}-report.md
---

<Purpose>
Aggregate all pipeline stages (lead-finder → company-researcher → enterprise-filter → outreach-generator) into a structured daily or weekly report. The report tracks new leads, hot leads requiring immediate action, follow-up calendar, and pipeline movement.
</Purpose>

<Use_When>
- User needs a summary of today's pipeline activity
- User says "日报", "每日报告", "报告", "汇总", "daily-report"
- User needs weekly review of pipeline progress
- User needs handoff document for team or manager
</Use_When>

---

## Report Structure

### 1. Pipeline Summary

| Metric | Today | This Week | Change |
|---|---|---|---|
| New leads discovered | {count} | {count} | {+/-} |
| HOT leads | {count} | {count} | {+/-} |
| WARM leads | {count} | {count} | {+/-} |
| COLD leads | {count} | {count} | {+/-} |
| Outreach sent | {count} | {count} | {+/-} |
| Replies received | {count} | {count} | {+/-} |

### 2. HOT Leads (需要立即行动)

| Company | Score | Key Signal | Contact | Recommended Action |
|---|---|---|---|---|
| {name} | {score} | {signal} | {channel} | {action} |

### 3. Follow-up Calendar

| Company | Last Contact | Status | Next Action | Due Date |
|---|---|---|---|---|
| {name} | {date} | {stage} | {action} | {date} |

### 4. Pipeline Movement

- **New to pipeline**: {list of companies added today}
- **HOT to WARM**: {list and why downgraded}
- **WARM to COLD**: {list and why}
- **Closed/Lost**: {list and reason}
- **Responded**: {list of replies received}

### 5. Notes & Observations

{free-form observations about market trends, competitor activity, etc.}

---

## Data Sources

Gather data from:
- `leads-*.json` (lead-finder output)
- `research-*.md` (company-researcher dossiers)
- `filtered-leads-*.json` (enterprise-filter output)
- `outreach-*.md` (outreach-generator output)

Output report to: `pipeline-{date}-report.md`
