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
- `references/AI漫剧获客-Top10线索表.md` — example leads and their quality signals
- `references/AI漫剧获客-关键词库.md` — keyword library with all tested search terms
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
4. Use `enterprise-filter` on the profile text if available
5. Record lead only if enterprise-passing signals >= 3

---

### 小红书 (Xiaohongshu / XHS)

**Keywords to search**:
- `AI漫剧工作室` (best — "工作室" naturally filters individuals)
- `AI短剧制作` (production-focused)
- `AI漫画团队` (team keyword)
- `AI动画公司` (company keyword)
- `AI漫剧 招聘` (hiring = business operation)
- `AI动画团队 招聘` (recruitment = enterprise)
- `AI视频创业` (startup tag)
- `AI短剧接单` (order-taking = commercial operation)
- `AI漫剧 找团队` (partnership seeking)

**Enterprise signals on XHS**:
- 招聘信息 (recruitment posts = clearest enterprise signal)
- 融资报道 (funding news: search "AI漫剧 融资")
- 商务合作 posts or tags
- 工作室日常 (studio vlog = real team)
- Account follows business patterns (consistent posting, brand voice)

---

### 抖音 (Douyin)

**Keywords to search**:
- `AI漫剧` (high volume, filter required)
- `AI短剧` (overlaps with live-action short dramas)
- `AIGC动画` (AIGC label)
- `AI漫剧工作室` (better precision)
- `AI短剧制作` (production-oriented)

**Enterprise signals on Douyin**:
- 企业认证 badge (verified company account)
- Large follower count with consistent branded content
- Commercial inquiries visible in comments or bio
- Multiple series published under same brand

---

### YouTube

**Keywords to search**:
- `AI comic Chinese` (Chinese studios on YouTube)
- `AI animation studio China` (Chinese AI animation companies)
- `AIGC short drama` (English keyword, global reach)

**Enterprise signals on YouTube**:
- Channel has company name in About section
- Multiple series with consistent style
- Business email in About section
- Mention of "studio" or "production company"

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

**Confidence classification**:
- **HIGH**: >=3 strong signals from top 4
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
| `company_name` | 灵境AI | Use the name as found on the platform |
| `platform_source` | B站 | One of: B站 / 小红书 / 抖音 / YouTube / GitHub |
| `signals_found` | 企业认证;商务合作;3部连载 | List all signals found, semicolon-separated |
| `confidence` | HIGH | HIGH / MEDIUM / LOW |
| `contact_available` | YES | YES if any public contact info found |
| `notes` | 商务联系微信:xxx;月产50部 | Free-text contacts and estimates |

---

## Integration

**Output to**: `leads-{batch}.json` in the working directory.
**Downstream**: Output feeds into `outreach-generator` skill for personalized message generation.
