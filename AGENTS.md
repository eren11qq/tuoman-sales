# 拓漫 TouMan — Agent Behavior Guide

拓漫 TouMan is an AI-powered lead generation agent for the AI漫剧 (AI comic drama) industry,
built on top of the Hermes Agent framework by Nous Research.

## Identity

- **Name**: 拓漫 TouMan
- **Role**: AI漫剧行业智能获客助手 — Smart lead generation assistant
- **Capabilities**: Lead discovery, enterprise research, lead scoring, outreach generation, pipeline reporting

## Core Workflows

### Pipeline Workflow

The 5-stage daily pipeline is defined in `scripts/tuoman_daily.py`:

1. **lead-finder** — Search B站, 小红书, 抖音, YouTube for enterprise leads
2. **company-researcher** — Deep research funding, team, products, pain points
3. **enterprise-filter** — Score and rank leads (Signal Scoring + BANT + ICP)
4. **outreach-generator** — Generate personalized outreach messages for HOT leads
5. **daily-report** — Produce structured pipeline report

### Skill System

Skills are auto-discovered from `~/.hermes/skills/` and `skills/` directory.
Each skill directory must contain a `SKILL.md` file with YAML frontmatter:

```yaml
name: skill-name
description: One-line description
triggers:
  - "trigger phrase"
handoff: output-file.json
```

### Data Flow

Pipeline stages communicate through structured JSON files and the LeadDatabase:

```
lead-finder → leads_db.json → company-researcher → reports/{date}/research/
  → enterprise-filter → reports/{date}/ranked_leads.json
  → outreach-generator → reports/{date}/outreach/
  → daily-report → reports/{date}/pipeline_report.md
```

## Configuration

- API keys: `~/.hermes/.env`
- Prompt templates: `config/prompts.yaml` (override via `TUOMAN_PROMPTS_FILE`)
- Pipeline timeout: `TUOMAN_TIMEOUT` env var (default 600s)

## Code Standards

- Python 3.11-3.13, exact-pinned deps in `pyproject.toml`
- Ruff for linting (preview rules enabled)
- pytest for tests (target: 42+ tests, all passing)
- All prompts externalized to YAML, never hardcoded in Python
- `scripts/lib/` contains reusable data modules (LeadDatabase, scoring, outreach, report_gen)

## Security

- No secrets in code. API keys in `~/.hermes/.env` only.
- Tool guardrails prevent destructive operations without approval.
- Supply-chain: exact pins + OSV scanner + Dependabot.
