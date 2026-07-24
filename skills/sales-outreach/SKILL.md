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
</Purpose>

<Use_When>
- User needs to run the complete lead gen → outreach cycle
- User says "全流程", "跑一遍", "获客全流程", "一条龙", "完整管线"
- User wants to execute only one stage of the pipeline
</Use_When>

---

## Usage

### Mode: `full` (default)
Run the entire 5-stage pipeline.

```
1. lead-finder — scan platforms for new leads
2. company-researcher — research each new lead
3. enterprise-filter — score and rank all leads
4. outreach-generator — draft copy for HOT leads
5. daily-report — write today's report
```

### Mode: `discover`
Run only stages 1-3 (discover → research → score).

### Mode: `report`
Run only stage 5 (daily-report).

## Pipeline Architecture

```
lead-finder → company-researcher → enterprise-filter → outreach-generator → daily-report
```

## Handoff

Output is written to `pipeline-{date}-result.md`, containing:
- Summary of each stage's output
- Links to individual stage handoff files
- HOT leads requiring immediate action
- Pipeline health status
