---
name: sales-outreach
description: Full-cycle pipeline orchestrator for AI漫剧获客
platforms: [win32, linux]
argument-hint: "<mode: full|discover|report>"
triggers:
  - "全流程"
  - "sales-outreach"
  - "获客全流程"
  - "跑一遍"
  - "完整管线"
  - "一条龙"
  - "pipeline"
handoff: pipeline-{date}-result.md
---

<Purpose>
Orchestrate the complete AI漫剧获客 pipeline end-to-end. This meta-skill chains 5 sub-skills in sequence to run a full sales development cycle:

1. **lead-finder** — discover new leads across B站, 小红书, 抖音, YouTube, GitHub
2. **company-researcher** — deep-dive each new lead (funding, team, products, pain points)
3. **enterprise-filter** — score and rank leads (Signal Scoring + BANT + ICP)
4. **outreach-generator** — generate personalized outreach copy for HOT leads
5. **daily-report** — produce daily pipeline report

Run the full pipeline with one command, or target a specific stage.
</Purpose>

<Use_When>
- User needs to run the complete lead gen → outreach cycle
- User says "全流程", "跑一遍", "获客全流程", "一条龙", "完整管线"
- User wants to execute only one stage of the pipeline (discovery, scoring, or reporting)
- User needs a status summary of the current pipeline
</Use_When>

<Do_Not_Use_When>
- User needs deep research on a single company (use company-researcher directly)
- User needs only outreach copy for known leads (use outreach-generator directly)
- User needs a standalone daily report without running discovery (use daily-report directly)
</Do_Not_Use_When>

---

## Pipeline Architecture

```
                        ┌─────────────┐
                        │ lead-finder  │  Stage 1: Multi-platform discovery
                        └──────┬──────┘
                               │ raw leads
                               ▼
                        ┌─────────────┐
                        │company-     │  Stage 2: Deep research on each new lead
                        │researcher   │  (funding, team, products, pain points)
                        └──────┬──────┘
                               │ dossiers
                               ▼
                        ┌─────────────┐
                        │enterprise-  │  Stage 3: Score + rank (Signal/BANT/ICP)
                        │filter       │  → HOT / WARM / COLD tiers
                        └──────┬──────┘
                               │ ranked list
                               ▼
                        ┌─────────────┐
                        │outreach-    │  Stage 4: Personalized copy for HOT leads
                        │generator    │  (channel-appropriate, variable-substituted)
                        └──────┬──────┘
                               │ outreach messages
                               ▼
                        ┌─────────────┐
                        │daily-report │  Stage 5: Pipeline snapshot + follow-up plan
                        └─────────────┘
```

---

## Usage Modes

### Mode: `full` (default)
Run the entire 5-stage pipeline. Best for daily morning execution.

```bash
# Inside Hermes:
/sales-outreach full

# What happens:
# 1. lead-finder — scan platforms for new leads
# 2. company-researcher — research each new lead
# 3. enterprise-filter — score and rank all leads
# 4. outreach-generator — draft copy for HOT leads
# 5. daily-report — write today's report
```

**Estimated duration**: 15-30 minutes depending on number of new leads.

### Mode: `discover`
Run only stages 1-3 (discover → research → score). Skips outreach generation and reporting. Useful for mid-day check or when you only need pipeline updates.

### Mode: `report`
Run only stage 5 (daily-report). Useful for pulling a status summary without running new discovery.

---

## Handoff

Output is written to `pipeline-{date}-result.md` in the working directory, containing:
- Summary of each stage's output
- Links to individual stage handoff files
- HOT leads requiring immediate action
- Pipeline health status

---

## Self-Check

```
[ ] All 5 stages complete or explicitly skipped
[ ] No duplicate leads across discovery batches
[ ] HOT leads have outreach copy generated
[ ] Daily report produced and deliverable
[ ] Handoff file written
```
