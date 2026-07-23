---
name: lead-finder
description: Multi-platform lead discovery for AI漫剧 enterprises
platforms: [win32, linux]
argument-hint: "[platform] [keyword]"
triggers:
  - "找客户"
  - "lead-finder"
  - "线索发现"
  - "搜索客户"
  - "找线索"
  - "获客搜索"
handoff: leads-{batch}.json
---

<Purpose>
Discover enterprise leads who produce AI-generated comics/short dramas (AI漫剧/AI短剧) across multiple Chinese platforms. Output structured lead profiles for downstream filtering and outreach.

This skill targets companies, studios, and teams — NOT individual creators or tutorial accounts. Every lead must pass a clear enterprise-vs-individual filter before being output.

Reference files for industry context and known leads:
- `../../references/AI漫剧获客-Top10线索表.md` — example leads and their quality signals
- `../../references/AI漫剧获客-关键词库.md` — keyword library with all tested search terms
</Purpose>

<Use_When>
- User says "找客户", "lead-finder", "线索发现", "搜索客户", "找线索", "获客搜索"
- User needs to find companies producing AI漫剧/AI short dramas on a specific platform
- User needs to batch-discover leads across B站, 小红书, 抖音, YouTube, GitHub
- User needs structured lead data for the downstream outreach pipeline
</Use_When>

<Do_Not_Use_When>
- User needs to generate outreach messages (use outreach-generator skill instead)
- User needs to research a specific known company in depth (use deep-research skill instead)
- User is looking for individual creators or tutorial accounts
- User needs to verify company registration details (use ENScan_GO instead)
</Do_Not_Use_When>

---

## Platform Search Strategies

### B站 (Bilibili)

B站 is the primary content platform for AI漫剧. Most content producers publish serialized work here.

**Keywords to search**:
- `AI漫剧` (baseline — high noise)
- `AI短剧` (broader, some noise)
- `AI漫画` (overlaps with static AI comics)
- `AI动漫` (animation-focused)
- `AIGC短剧` (more professional label)
- `AI动画制作` (full animation pipeline)
- `AI漫剧 第` (targets serialized content — filters out tutorials effectively)
- `AI动态漫 工作室` (studio keyword filters individuals naturally)
- `AI漫剧 商务合作` (commercial intent — low volume, high quality)
- `AI漫剧 原创` (original content tag)
- `AI漫剧 IP` (IP development = business operation)

**Enterprise signals to check on B站**:
- Profile description mentions 工作室/团队/公司
- Has 企业认证 badge
- Posts 商务合作 contact in bio or in video descriptions
- Posts content at scale (multiple series running simultaneously)
- Content is serialized with episode numbers (proves production pipeline)
- Profile includes company name, team size, or hiring info

**How to distinguish enterprise vs individual**:
```
Checklist (must pass >=3 for enterprise classification):
[ ] Profile description mentions company name or 工作室/团队
[ ] Has 企业认证 or confirmed team behind it
[ ] Posts commercial contact info (商务/合作/商务合作)
[ ] Multiple series running concurrently
[ ] Batch updates (not sporadic posting)
[ ] Team size mentioned anywhere
```

**Search strategy**:
1. Search `AI漫剧 第` first — serialized content = production pipeline
2. For each promising result, open UP主 profile page
3. Check bio for: company name, team mentions, contact info
4. Check发布内容 for: multiple series, episode numbering, branded style
5. Use `enterprise-filter` on the profile text if available
6. Record lead only if enterprise-passing signals >= 3

---

### 小红书 (Xiaohongshu / XHS)

XHS has a higher density of business-oriented content than B站. Many small studios use XHS for team recruitment and partnership posts.

**Keywords to search**:
- `AI漫剧工作室` (best — "工作室" naturally filters individuals)
- `AI短剧制作` (production-focused)
- `AI漫画团队` (team keyword)
- `AI动画公司` (company keyword)
- `AI漫剧 招聘` (hiring = business operation)
- `AI动画团队 招聘` (recruitment = enterprise)
- `AI视频创业` (startup tag)
- `AI短剧接单` (order-taking = commercial operation)
- `AI绘画工作室 招聘` (adjacent industry, may cross over)
- `AI漫剧 找团队` (partnership seeking)

**Enterprise signals on XHS**:
- 招聘信息 (recruitment posts = clearest enterprise signal)
- 融资报道 (funding news: search "AI漫剧 融资")
- 商务合作 posts or tags
- 工作室日常 (studio vlog = real team)
- Account follows business patterns (consistent posting, brand voice)
- Profile has company introduction

**Key difference from B站**: XHS has fewer pure tutorial accounts. A post about "AI漫剧工作室" is much more likely to be from an actual studio than an individual.

---

### 抖音 (Douyin)

Douyin has massive content volume but lower enterprise density. Requires careful filtering.

**Keywords to search**:
- `AI漫剧` (high volume, filter required)
- `AI短剧` (overlaps with live-action short dramas)
- `AIGC动画` (AIGC label)
- `AI漫画` (may include static content)
- `AI漫剧工作室` (better precision)
- `AI短剧制作` (production-oriented)

**Enterprise signals on Douyin**:
- 企业认证 badge (verified company account)
- Large follower count with consistent branded content
- Commercial inquiries visible in comments or bio
- Multiple series published under same brand
- bio includes 商务合作/商务VX/联系方式

**Notes**: Douyin has the highest noise level. Focus on accounts that clearly label themselves as production studios or have enterprise verification. Skip accounts that only post clips without original production credit.

---

### YouTube

YouTube is relevant for companies operating overseas or targeting international audiences. Especially useful for discovering Chinese AI漫剧 companies expanding to global markets.

**Keywords to search**:
- `AI comic Chinese` (Chinese studios on YouTube)
- `AI animation studio China` (Chinese AI animation companies)
- `AIGC short drama` (English keyword, global reach)
- `AI 漫剧 English` (hybrid content)
- `AI anime China` (animation-focused)

**Enterprise signals on YouTube**:
- Channel has company name in About section
- Multiple series with consistent style
- Branded channel art and consistent posting schedule
- Business email in About section
- Mention of "studio" or "production company"

---

### GitHub / 技术社区

GitHub discovers companies via their open-source tools and repositories. A company building or using AI comic/animation pipelines often has a technical footprint here.

**Keywords to search**:
- `AI comic generation` → repos → look at contributors' organizations
- `AI animation` → repos → organizational affiliations
- `AIGC pipeline` → workflow tools → usage by companies
- `comic generation AI` → tool users → company names
- `AI manga generation` → Japan/domestic comic angle
- `AI 漫画 生成` (Chinese tool projects)
- `AI 短剧 生成` (Chinese short drama tools)

**Enterprise signals on GitHub**:
- Repository owned by an organization (not personal account)
- Organization profile has company website and description
- Repo README mentions commercial product/company
- Active commercial documentation in repo
- Contributors from known companies

**Other tech communities**: Product Hunt (`AI comic` / `AI animation` search) can reveal new tools and the companies behind them.

---

## Lead Quality Signals

Ranked by importance (1 = most reliable indicator of a qualified enterprise lead):

| Rank | Signal | Why It Matters | Confidence Boost |
|------|--------|----------------|------------------|
| 1 | Company name or registration visible | Proven business entity | HIGH |
| 2 | Hiring posts (especially AI/tech positions) | Active expansion, budget available | HIGH |
| 3 | Funding news/mentions | Capital to purchase tools | HIGH |
| 4 | Multiple series running concurrently | Production capacity, need for pipeline tools | MEDIUM-HIGH |
| 5 | Commercial contact info publicly posted | Open to vendor outreach | MEDIUM-HIGH |
| 6 | Consistent branded content style | Professional operation, quality standards | MEDIUM |
| 7 | Team size mentioned | Larger team = more complex tooling needs | MEDIUM |
| 8 | B2B service offerings | They sell services — understand vendor value | LOW-MEDIUM |

**Confidence classification**:
- **HIGH**: >=3 strong signals from top 4 (company name OR hiring OR funding OR multiple series)
- **MEDIUM**: 2 strong signals, or 1 strong + 2 medium signals
- **LOW**: 1 strong signal but insufficient verification

---

## Output Schema

Every discovered lead must be structured as a pipe-delimited row:

```
company_name | platform_source | signals_found | confidence | contact_available | notes
```

**Field specifications**:

| Field | Example | Rules |
|-------|---------|-------|
| `company_name` | 灵境AI | Use the name as found on the platform. If multiple, pick most complete. |
| `platform_source` | B站 | One of: B站 / 小红书 / 抖音 / YouTube / GitHub / 招聘平台 / 融资新闻 |
| `signals_found` | 企业认证;商务合作;3部连载 | List all signals found, semicolon-separated |
| `confidence` | HIGH | HIGH / MEDIUM / LOW — based on signal rules above |
| `contact_available` | YES | YES if any public contact info found, NO if none |
| `notes` | 商务联系微信:xxx;月产50部 | Free-text: contacts, production volume estimates, team size, dates observed |

**Batch output format**:

```csv
company_name | platform_source | signals_found | confidence | contact_available | notes
--------------------------------------------------------------
灵境AI | 融资新闻 | 3轮融资1亿元;300人团队;月产300部 | HIGH | NO | 融资信息来自36氪;创始人许金城
星迹互动 | 融资新闻 | 天使轮数千万;120人扩招;正大集团投资 | HIGH | NO | 融资信息来自36氪;创始人张文广
浙江乐播动漫 | 招聘平台 | 招AIGC内容创作;目标月产400集 | HIGH | YES | 联系方式:747572429@qq.com
```

---

## Anti-Patterns (Must Filter Out)

The following types must be excluded from lead output:

| Type | How to Identify | Why Exclude |
|------|----------------|-------------|
| Individual hobbyist creators (个人爱好者) | No company/studio/team mention; personal naming; casual posting frequency | Not a B2B target |
| Tutorial/content creator accounts (教程类账号) | Profile keywords: 教程/教学/入门/学习; content is how-to, not original production | They teach, not produce |
| Non-AI traditional animation studios | Content description lacks AI-related keywords; uses traditional animation pipeline language | Wrong segment |
| Companies clearly out of business | No posts in >6 months, website dead, funding news is old with no follow-up | Wasted effort |
| Aggregator/curation accounts | Content is reposted from multiple sources without original production credit | Not producers |
| Off-topic results from broad keywords | E.g., live-action short dramas from "AI短剧" search | Wrong segment |

**Filtering workflow**:
1. Apply the enterprise checklist (>=3 signals needed)
2. Check against anti-pattern list above
3. If unclear, mark as LOW confidence and flag for manual review rather than discarding
4. Duplicate the lead against the known leads database before adding

---

## Daily Workflow

```
Daily Lead Discovery Cycle
===========================
Step 1: Platform rotation
  Day A — B站 + 小红书
  Day B — 抖音 + YouTube
  Day C — GitHub + 招聘平台 review
  Day D — Cross-platform dedup + audit
  (Repeat)

Step 2: For each platform, use rotated keywords
  - Don't use the same keyword twice in a row — reduces result overlap
  - Prioritize Tier 1 keywords from the keyword library first
  - Then Tier 2 for fill
  - See keywords library per platform above

Step 3: Apply enterprise filter
  - For each result, run through the enterprise checklist
  - Pass >=3 signals → keep
  - Fail → discard or mark LOW CONFIDENCE

Step 4: Deduplicate
  - Check against known leads database (leads-*.json files)
  - Check against current batch — don't list the same lead twice

Step 5: Output new leads only
  - Format: pipe-delimited CSV, one lead per row
  - Append to new leads-{batch}.json file (where {batch} = YYYY-MM-DD)
  - Only new leads (not previously discovered)

Step 6: Append to leads database
  - Add new leads to the master leads database file
  - Dedup again on append

Step 7 (weekly): Refresh platform context
  - Scan融资新闻 for new funding rounds in existing leads
  - Update confidence for leads with stale timestamps
  - Check for dead/alumni accounts and mark inactive
```

---

## Self-Check

After completing a lead-finder session, verify against this checklist:

```
[ ] No individual hobbyists in output (all pass >=3 enterprise signals)
[ ] No tutorial/teaching accounts included
[ ] Each lead has all 6 schema fields filled
[ ] Confidence level matches the signal rules (not inflated)
[ ] Dupes removed — no lead appears twice in same batch
[ ] New leads only — cross-checked against existing database
[ ] Contact availability accurately noted (YES only if actually visible)
[ ] Platform source is honest (not misattributed)
[ ] Notes field captures actionable information (contacts, signals, estimates)
```

---

## Integration

**Input from user**: User provides optional `[platform]` and `[keyword]` arguments. If omitted, the skill runs the full daily rotation across all platforms.

**Output to**: `leads-{batch}.json` in the working directory, where `{batch}` is the discovery date (YYYY-MM-DD) or batch identifier.

**Downstream**: Output feeds into the `outreach-generator` skill for personalized message generation. Each lead row in the output maps to a lead profile for outreach generation.

**Related files**:
- `../../references/AI漫剧获客-关键词库.md` — full keyword library with effectiveness rankings
- `../../references/AI漫剧获客-Top10线索表.md` — example high-quality lead profiles
- `../../references/AI漫剧获客-行业话术模板库.md` — outreach templates for downstream use
