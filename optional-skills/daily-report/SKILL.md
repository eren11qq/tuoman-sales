---
name: daily-report
description: Daily/weekly pipeline reports for AI漫剧获客 system
platforms: [win32, linux]
argument-hint: "date (YYYY-MM-DD | 'today' | 'week')"
triggers:
  - "日报"
  - "daily-report"
  - "daily report"
  - "今日报告"
  - "今日汇报"
  - "周报"
  - "weekly report"
  - "weekly-report"
  - "pipeline report"
  - "线索报告"
  - "pipeline"
handoff: daily-report-{date}.md
---

<Purpose>
Generate structured daily (and weekly) pipeline reports for the AI漫剧获客 system. Each report provides a snapshot of the lead pipeline at a given date — health status, new leads, hot leads requiring action, today's follow-up calendar, pipeline movement, and industry monitoring. Weekly reports include a conversion funnel rollup and week-over-week trend analysis.

Data is sourced from the lead tracker and related files on the desktop, then formatted into a clean, actionable markdown report suitable for team consumption or automated delivery.
</Purpose>

<Use_When>
- User says "日报", "daily report", "今日报告", or asks for a pipeline status update
- User says "周报" or "weekly report" (generates weekly rollup variant)
- User provides a specific date or asks for "today" or "this week"
- User needs to review hot leads requiring immediate action
- User needs a follow-up calendar for the current day
- User wants to track pipeline movements (status changes, new contacts, lost leads)
- User wants to monitor industry news, funding rounds, competitor moves, or viral works relevant to the AI漫剧 space
</Use_When>

<Do_Not_Use_When>
- User needs to generate outreach copy for a specific lead (use `outreach-generator` instead)
- User needs to research a new lead from scratch (use a research skill)
- User needs to update the lead tracker file itself (do that directly)
- User needs a general business report unrelated to the AI漫剧 lead pipeline
</Do_Not_Use_When>

---

## Data Sources

The report draws from these files — verify they exist before running; if any are missing, warn the user and generate the report from available data only.

| Source | Path | Frequency | Content |
|---|---|---|---|
| **Top 10 Leads Tracker** | `../../references/AI漫剧获客-Top10线索表.md` | Updated on research | Lead profiles, priority scores, pain points, contact info |
| **Outreach Templates** | `../../references/AI漫剧获客-行业话术模板库.md` | Static reference | Template library used for outreach status notes |
| **Generated Outreach Files** | `$PROJECT_ROOT/optional-skills/daily-report/` (and sibling dirs) | Daily | Previous handoff files from outreach-generator, used to track follow-up status |
| **Pipeline State File** | `$PROJECT_ROOT/optional-skills/daily-report/pipeline-state.json` (optional, created on first run) | Updated per report | Cached pipeline state for movement tracking |

If the Pipeline State File does not exist yet, the report will create a baseline snapshot and note that movement tracking starts from the next report.

---

## Argument: Date

The first argument specifies the report date. Accepted formats:

| Value | Behavior |
|---|---|
| `"today"` (default) | Generates a daily report for the current date |
| `"week"` | Generates a weekly rollup report for the current week |
| `YYYY-MM-DD` | Generates a daily report for the specified date |
| `week:YYYY-MM-DD` | Generates a weekly report ending on the specified date |

If no argument is given, default to `"today"`.

---

## Report Structure

### Daily Report Sections

1. **Executive Summary** — Pipeline health at a glance
2. **New Leads** — Leads added since the last report
3. **Hot Leads** — High-priority leads requiring action today
4. **Follow-up Calendar** — Scheduled touches for today
5. **Pipeline Movement** — Status changes since last report
6. **Industry Monitoring** — Funding news, competitor moves, viral works

### Weekly Report Additions

When `argument-hint` resolves to a weekly report (date argument is `"week"` or `week:YYYY-MM-DD`), append these sections after section 6:

7. **Conversion Funnel** — Stage-by-stage funnel with counts
8. **Week-over-Week Trends** — MoM changes in key metrics

---

## Section 1: Executive Summary

A one-block overview. Always start with the **Pipeline Health Indicator** — one of three emoji-statuses:

| Status | Indicator | Condition |
|---|---|---|
| Healthy | GREEN | 3+ HOT leads, active follow-ups this week, new leads coming in |
| Watch | YELLOW | 1-2 HOT leads, or no follow-ups scheduled, or stale pipeline |
| Critical | RED | 0 HOT leads, or no touches in 7+ days, or stale data |

Then a 3-line summary covering:
- Total active leads in pipeline
- Number requiring action today
- Key highlight or risk for the day

**Template:**

```markdown
## Executive Summary

**Pipeline Health:** {GREEN / YELLOW / RED}

- **Active leads in pipeline:** {count}
- **Requiring action today:** {count}
- **Highlight:** {one-sentence key takeaway, e.g. "灵境AI enters week 2 of follow-up sequence — send new case study"}
- **Risk:** {one-sentence risk, e.g. "星迹互动 CEO out of office until July 28 — reschedule touch"}
```

---

## Section 2: New Leads

List leads added to the pipeline since the last report. If no new leads, state "None."

| Column | Description |
|---|---|
| Company | Lead name with link to source |
| Priority | HOT / WARM / COLD |
| Source | Where the lead was found (36氪, LinkedIn, referral, etc.) |
| Key Signal | The trigger that qualified them (funding, hiring, news) |
| Added By | Who added the lead |

**Template:**

```markdown
## New Leads (since {last_report_date})

| Company | Priority | Source | Key Signal | Added By |
|---|---|---|---|---|
| {company_name} | {HOT/WARM/COLD} | {source} | {signal} | {name} |

*No new leads since last report.*
```

---

## Section 3: Hot Leads

Leads with `HOT` priority that require action today. Sorted by score descending. Each lead gets a brief action block.

**Template:**

```markdown
## Hot Leads — Requires Action

### {score}/10 — {company_name} ({location})
**Stage:** {stage} | **Last Touch:** {date} | **Next Action:** {description}

| Field | Value |
|---|---|
| Founder/Contact | {name}, {title} |
| Funding | {amount}, {round}, {investors} |
| Pain Point | {primary pain} |
| Next Touch | {channel}: {message or goal} |
| Assigned To | {name} |
```

---

## Section 4: Follow-up Calendar

All scheduled touches for today. Group by lead, sorted by priority.

**Template:**

```markdown
## Follow-up Calendar — {date}

| Time | Lead | Channel | Action | Owner |
|---|---|---|---|---|
| {HH:MM} | {company_name} | 脉脉/LinkedIn/邮件/微信 | {brief action} | {name} |
| {HH:MM} | {company_name} | 脉脉/LinkedIn/邮件/微信 | {brief action} | {name} |

**Total touches scheduled:** {count}
```

If no touches are scheduled for today:

```markdown
*No follow-ups scheduled for today. Consider warming leads via industry insight sharing.*
```

---

## Section 5: Pipeline Movement

Changes since the last report date. Track status transitions for each lead. If no Pipeline State File exists yet, create a baseline and note that tracking starts from next report.

**Statuses used:**
- `NEW` — Just added to pipeline
- `TOUCHED` — First contact made
- `ENGAGED` — Lead responded positively
- `MEETING` — Demo/meeting scheduled
- `NEGOTIATING` — In commercial discussion
- `CLOSED_WON` — Customer
- `CLOSED_LOST` — Lost
- `STALE` — No response after full sequence

**Template:**

```markdown
## Pipeline Movement

### Status Changes

| Lead | From | To | Date | Notes |
|---|---|---|---|---|
| {company_name} | {old_status} | {new_status} | {date} | {notes} |

### Summary

- **New to pipeline:** {count}
- **Moved forward:** {count}
- **Moved backward / stalled:** {count}
- **Closed won:** {count}
- **Closed lost:** {count}

*Baseline snapshot created — movement tracking begins with next report.*
```

---

## Section 6: Industry Monitoring

Track external signals relevant to the AI漫剧 space. Three sub-sections:

### Funding & Investment News

| Company | Round | Amount | Investors | Date | Implication |
|---|---|---|---|---|---|
| {name} | {round} | {amount} | {list} | {date} | {impact on pipeline} |

### Competitor Moves

| Competitor | Move | Date | Our Response |
|---|---|---|---|
| {name} | {product launch / partnership / pricing change} | {date} | {threat/opportunity} |

### Viral Works & Market Trends

| Work | Platform | Views | Trend Signal |
|---|---|---|---|
| {title} | {short-video platform} | {count} | {e.g. "角色一致性标杆", "新风格验证"} |

If no industry updates to report:

```markdown
*No significant industry updates since last report.*
```

---

## Weekly Report: Section 7 — Conversion Funnel

Only included in weekly reports. Summarizes the pipeline stage distribution and conversion rates.

**Template:**

```markdown
## Conversion Funnel (Week of {start_date} — {end_date})

### Stage Distribution

| Stage | Count | % of Total |
|---|---|---|
| NEW | {count} | {pct}% |
| TOUCHED | {count} | {pct}% |
| ENGAGED | {count} | {pct}% |
| MEETING | {count} | {pct}% |
| NEGOTIATING | {count} | {pct}% |
| CLOSED_WON | {count} | {pct}% |
| CLOSED_LOST | {count} | {pct}% |
| STALE | {count} | {pct}% |
| **Total** | **{total}** | **100%** |

### Conversion Rates

| Transition | Rate | vs Last Week |
|---|---|---|
| NEW → TOUCHED | {pct}% | {+/-} |
| TOUCHED → ENGAGED | {pct}% | {+/-} |
| ENGAGED → MEETING | {pct}% | {+/-} |
| MEETING → NEGOTIATING | {pct}% | {+/-} |
| NEGOTIATING → CLOSED | {pct}% | {+/-} |
```

---

## Weekly Report: Section 8 — Week-over-Week Trends

Only included in weekly reports. Compare this week's key metrics to the previous week.

**Metrics tracked:**

| Metric | This Week | Last Week | Change | Direction |
|---|---|---|---|---|
| Active leads | {count} | {count} | {+/-} | {up/down/stable} |
| New leads added | {count} | {count} | {+/-} | {up/down/stable} |
| Touches made | {count} | {count} | {+/-} | {up/down/stable} |
| Positive responses | {count} | {count} | {+/-} | {up/down/stable} |
| Meetings booked | {count} | {count} | {+/-} | {up/down/stable} |
| Deals closed | {count} | {count} | {+/-} | {up/down/stable} |

**Direction legend:** up / down / stable (within 10% = stable)

---

## Scheduling Rules

When invoked by a scheduler or cron hook:

| Frequency | Day | Time | Command |
|---|---|---|---|
| Daily | Every weekday | 09:00 | `daily-report today` |
| Weekly | Monday | 09:00 | `daily-report week` |

These times are local (Asia/Shanghai timezone assumed). The report is generated and written to the output path. Weekday-only generation avoids weekend noise — if Saturday or Sunday is explicitly requested, generate the report but note it is an off-day.

---

## Delivery Channels

### Primary: File Output

The report is written to:

```
$PROJECT_ROOT/optional-skills/daily-report/{date}-report.md
```

Where `{date}` is `YYYY-MM-DD` for daily reports or `YYYY-MM-DD-weekly` for weekly reports.

### Optional: Telegram

If a Telegram bot token and chat ID are configured in the environment, send the report summary (first 3 sections + link to full file) via Telegram. Configure via:

- `TELEGRAM_BOT_TOKEN` — Bot token from @BotFather
- `TELEGRAM_CHAT_ID` — Target chat or channel ID

### Optional: WeChat (微信)

If configured, send a condensed version to WeChat via available integration. Configuration depends on the WeChat integration method available (e.g., WeCom bot webhook URL or个人微信自动化方案).

---

## Self-Check

After generating a report, verify against this checklist:

```
[ ] Pipeline Health Indicator is set (GREEN / YELLOW / RED)
[ ] All 6 daily sections are present
[ ] Weekly reports include sections 7 and 8
[ ] Tables use consistent column formatting
[ ] No stale data (dates match the report date)
[ ] New leads are cross-referenced with the Top 10 tracker
[ ] Follow-up calendar shows actionable items
[ ] Pipeline movements reference previous state
[ ] Industry monitoring captures recent events
[ ] Delivery channel is noted (file path at minimum)
[ ] If baseline snapshot was created, user is informed
```

---

## Output Format

After generation, present the report in this structure:

---

### Daily Report: {date}

**Type:** Daily | **Pipeline Health:** {GREEN/YELLOW/RED} | **Data Source:** Top 10 Leads Tracker

Report written to: `$PROJECT_ROOT/optional-skills/daily-report/{date}-report.md`

**Summary:**
- Active leads: {count}
- Hot leads requiring action: {count}
- Follow-ups today: {count}
- New leads: {count}

**Key Action Items:**
1. {company_name} — {action}
2. {company_name} — {action}
3. {company_name} — {action}

---

## Pipeline Health Indicator Logic

The health indicator is computed as follows:

```python
def pipeline_health(active_leads, hot_leads, days_since_last_touch, new_leads_this_week):
    if hot_leads >= 3 and days_since_last_touch <= 2 and new_leads_this_week >= 1:
        return "GREEN"
    elif hot_leads >= 1 and days_since_last_touch <= 7:
        return "YELLOW"
    else:
        return "RED"
```

- **GREEN**: Pipeline is active and healthy. Maintain cadence.
- **YELLOW**: Warning signs present. Review lead gen and outreach activity.
- **RED**: Pipeline is stalled. Immediate action needed to revive touches or source new leads.

---

## Pipeline State File Format

The optional pipeline state file (`pipeline-state.json`) stores the last known status of each lead for movement tracking. Format:

```json
{
  "last_report_date": "2026-07-23",
  "leads": {
    "灵境AI": {
      "status": "TOUCHED",
      "priority": "HOT",
      "last_updated": "2026-07-22"
    },
    "星迹互动": {
      "status": "NEW",
      "priority": "HOT",
      "last_updated": "2026-07-23"
    }
  }
}
```

This file is created automatically on the first report run and updated on each subsequent run. It lives at:

```
$PROJECT_ROOT/optional-skills/daily-report/pipeline-state.json
```

---

## Example Report (Daily)

```markdown
# Daily Pipeline Report — 2026-07-23

## Executive Summary

**Pipeline Health:** GREEN

- **Active leads in pipeline:** 10
- **Requiring action today:** 4
- **Highlight:** 灵境AI三轮累计近1亿 — prime time for outreach
- **Risk:** 灵漫快创已绑定万兴科技，需确认是否有独立采购需求

## New Leads (since 2026-07-22)

*No new leads since last report.*

## Hot Leads — Requires Action

### 9.5/10 — 灵境AI（杭州）
**Stage:** NEW | **Last Touch:** None | **Next Action:** Send initial outreach via 脉脉

| Field | Value |
|---|---|
| Founder/Contact | 许金城（二仙）, CEO |
| Funding | 三轮累计近1亿元，国科投资/柏睿资本/零以创投 |
| Pain Point | 月产300部，产能需求极大；出海需本地化工具 |
| Next Touch | 脉脉: 从"产能瓶颈"和"出海本地化"切入 |

### 9.5/10 — 星迹互动（北京）
**Stage:** NEW | **Last Touch:** None | **Next Action:** Send initial outreach via 脉脉

| Field | Value |
|---|---|
| Founder/Contact | 张文广, CEO |
| Funding | 天使轮数千万元，正大集团/大融传媒/禹牧智能 |
| Pain Point | 年底120人急速扩张；出海需多语言适配 |
| Next Touch | 脉脉: 从"仿真人剧产能"和"东南亚出海"切入 |

## Follow-up Calendar — 2026-07-23

*No follow-ups scheduled for today. Initial outreach planned for top 3 HOT leads this week.*

## Pipeline Movement

### Status Changes

| Lead | From | To | Date | Notes |
|---|---|---|---|---|
| 灵境AI | — | NEW | 2026-07-23 | Added via Top 10 tracker update |
| 星迹互动 | — | NEW | 2026-07-23 | Added via Top 10 tracker update |
| 国芯智造 | — | NEW | 2026-07-23 | Added via Top 10 tracker update |
| 星兴万物 | — | NEW | 2026-07-23 | Added via Top 10 tracker update |
| 奥睿森 | — | NEW | 2026-07-23 | Added via Top 10 tracker update |

*Baseline snapshot created — movement tracking begins with next report.*

## Industry Monitoring

### Funding & Investment News

| Company | Round | Amount | Investors | Date | Implication |
|---|---|---|---|---|---|
| 八点八数字(AniShort) | Series Unknown | 近亿元 | 北京泰中合领投 | 2026.6 | Tool平台集成合作机会 |
| 星迹互动 | Angel | 数千万元 | 正大集团/大融传媒 | 2026.4 | 正大东南亚渠道=出海合作机会 |

### Competitor Moves

| Competitor | Move | Date | Our Response |
|---|---|---|---|
| 万兴科技 | 发布"万兴剧厂"，投资灵漫快创 | 2026.1 | 关注万兴剧厂的功能覆盖范围 |

### Viral Works & Market Trends

| Work | Platform | Views | Trend Signal |
|---|---|---|---|
| 《我在末世开超市》 | 抖音/快手 | 1.8亿 | 灵境AI作品，AI漫剧爆款潜力已验证 |
| 《别惹那个僵尸，他末世无敌》 | 抖音/快手 | 1.5亿 | 灵漫快创作品，已验证商业化能力 |
```

## Example Report (Weekly)

For weekly reports, append sections 7 and 8 after section 6. See the weekly section templates above for the exact format. The weekly report title becomes:

```markdown
# Weekly Pipeline Report — Week of {start_date} to {end_date}
```

---

## Relationship to Other Skills

This skill is part of the AI漫剧获客 toolchain:

- **`outreach-generator`** — Generates personalized outreach copy for individual leads. Consumed by this skill to track outreach status.
- **`daily-report`** (this skill)** — Generates pipeline reports. Consumes lead data and outreach status.
- **Top 10 Leads Tracker** (`../../references/AI漫剧获客-Top10线索表.md`) — Central lead research file. Updated by research skills, consumed by this report.

Workflow: `Research → Top 10 Tracker → Outreach Generator → Daily Report → Action`
