---
name: company-researcher
description: Deep enterprise research for AI漫剧 industry leads
platforms: [win32, linux]
argument-hint: "<company_name> [optional: founder_name or website]"
triggers:
  - "调研"
  - "company-researcher"
  - "深度调研"
  - "企业调研"
  - "查一下这家公司"
  - "research"
handoff: research-{company_slug}.md
---

<Purpose>
Given a company name (and optionally a founder name or website), produce a comprehensive research dossier covering funding, team, products, pain points, purchase signals, and actionable outreach strategy. This skill is the second stage of the AI漫剧获客 pipeline — after lead-finder discovers leads, company-researcher deep-dives each one before they enter the outreach pipeline.

The output dossier feeds directly into the `outreach-generator` skill for personalized message generation.
</Purpose>

<Use_When>
- User provides a company name and asks for deep research
- User says "调研", "深度调研", "企业调研", "查一下这家公司", "research", "company-researcher"
- A lead has been discovered (via lead-finder or any other channel) and needs profiling before outreach
- User needs a structured dossier for pipeline review or CRM entry
- User needs to score a lead as HOT/WARM/COLD for prioritization
</Use_When>

<Do_Not_Use_When>
- User needs a general competitive landscape report covering multiple companies (use a market research skill instead)
- User asks for lead discovery / prospecting (use lead-finder first)
- User already has a complete dossier and only needs outreach copy (use outreach-generator)
- User asks for real-time data that requires live API calls (this skill uses public sources and inference)
</Do_Not_Use_When>

---

## Input

The skill expects at minimum a company name. Optional additional fields improve research depth:

| Field | Required | Description |
|---|---|---|
| `company_name` | Yes | Target company full legal name or brand name |
| `founder_name` | Optional | Founder/CEO name if known, aids verification |
| `website` | Optional | Company website URL, speeds up basic verification |
| `industry_hint` | Optional | e.g. "内容制作", "工具平台", "国有企业" — helps with classification |
| `funding_status` | Optional | If already known from lead-finder, e.g. "天使轮" |

If only a company name is provided, begin research immediately. If the name is ambiguous (common brand name), ask for clarification.

---

## Step 1: Research Dimensions (All 8 Required)

For every company, research across all eight dimensions below. Not every dimension will yield verified data for every company — mark unknown items as ❓ unknown and move on.

### 1a. Company Basics (企业基本信息)

Verify the full legal name, registration location, establishment date, enterprise type, and registered capital.

**Sources**: 企查查 / 天眼查 / 国家企业信用信息公示系统 / ENScan_GO (if available) / company website "关于我们"

**Output**:
- 全称: {full legal name}
- 注册地: {registration location with confidence}
- 成立时间: {establishment date}
- 企业类型: {private / SOE / foreign / joint venture}
- 注册资本: {registered capital, verified}

### 1b. Funding & Financial (融资与财务)

Track total funding raised, individual rounds (dates + amounts + investors), revenue estimates if public, and burn rate indicators.

**Sources**: 36氪 / 投资界 / 企查查 (shareholder changes) / 天眼查 (融资历程) / IT桔子 / 官方PR稿 / 工商变更记录 (资本变更 = 融资信号)

**Output**:
- 融资轮次: {list of rounds with dates, amounts, investors}
- 累计融资额: {total}
- 估值: {if disclosed}
- 收入预估: {if public or strongly inferable}
- 关键信号: {e.g. 连续融资 / 资本变更活跃 / 首次融资}

**Where to look first**: Search `"{company_name}" 融资` on 36氪. Cross-reference with 企查查 shareholding changes. A capital increase often indicates a new round that hasn't been PR'd yet.

### 1c. Team & Hiring (团队与招聘)

Investigate founder background (previous ventures, education, public persona), team size, hiring velocity (new positions in last 30 days), and key executives.

**Sources**: 招聘平台 (Boss直聘 / 猎聘 / 拉勾 / 鱼泡直聘) / 脉脉 / LinkedIn / 企查查 (高管名录) / 百度百科 / 媒体报道

**Output**:
- 创始人: {name, background, previous ventures, education}
- 核心团队: {CTO/COO/联创 with backgrounds}
- 团队规模: {current size, growth trajectory}
- 招聘动态: {new positions in last 30 days, total open positions, hiring velocity trend}
- 关键信号: {e.g. 新设部门 / 批量校招 / 高管新加入}

**Hiring velocity as a signal**: Count open positions. If >5 new postings in 30 days, that is a clear expansion signal. If the company is hiring for specific AI/tech roles (MJ/SD/可灵/Runway/Seedance operators), they are building in-house AI production capacity — a strong purchase signal.

### 1d. Products & Tech Stack (产品与技术栈)

Describe core product(s), tech stack (if discoverable), monthly output volume, representative works (with view counts), and cost structure claims.

**Sources**: 公司官网 / 微信公众号 / 媒体报道 / 技术博客 / GitHub (if open-source projects) / 招聘JD (技术栈描述) / B站/抖音 (作品发布频道)

**Output**:
- 核心产品: {description}
- 技术栈: {if discoverable: e.g. ComfyUI/SDXL/可灵/自研DIT架构}
- 月产量: {monthly output if known}
- 代表作品: {works with view counts and platforms}
- 成本结构: {claimed or inferred costs}
- 技术路线: {e.g. 全自研 / 工具组合 / 平台集成}

### 1e. Pain Points (痛点判断)

Infer pain points from public signals. Not every company will have clear pain points visible from the outside — use the inference framework below.

**Inference framework per company type**:

| Company Type | Default Pain Hierarchy |
|---|---|
| 内容制作公司 (Content Production) | 产能 > 质量一致性 > 出海本地化 > 成本控制 > 团队管理 |
| 技术平台/工具公司 (Platform/Tool) | 用户留存 > 功能完善度 > 差异化 > 商业化 > 生态扩展 |
| 国有/国资控股 (SOE) | 信创合规 > 数据安全 > 预算流程 > 效率提升 > 合作伙伴筛选 |

**How to infer (specific signals to look for)**:
- **产能 bottleneck**: 月产量快速增长 + 招聘密集 → likely need more efficient tools
- **质量一致性**: 强调"角色一致性" / "风格统一" in PR → they struggle with this
- **出海本地化**: 布局海外 + 招聘多语言人才 → need localization tooling
- **工具链 gaps**: 招聘JD列出多种工具 (MJ/SD/可灵/Runway) → they are still evaluating, no locked-in toolchain
- **管理痛点**: 供应商团队多 (e.g. 118家供应商) → need management/collaboration platform
- **成本压力**: 自报成本数据 + 强调"降本" → cost-sensitive buyer

**Output**:
- 痛点1: {pain point} — 证据: {evidence from sources} (confidence: ✅/🔶)
- 痛点2: {pain point} — 证据: {evidence from sources} (confidence: ✅/🔶)
- 痛点3: {pain point} — 证据: {evidence from sources} (confidence: ✅/🔶)
- 综合判断: {summary of primary pain driver}

### 1f. Purchase Signals (采购信号)

Identify signals that indicate the company is in an active buying window. Combine signals from multiple dimensions to determine urgency.

**Strong signals (weight: HIGH)**:
- Closed a funding round within the last 6 months (money available)
- Hiring velocity >5 positions in 30 days (expanding, needs tools)
- New department created (e.g. "AI项目组") (fresh budget, evaluating tools)
- Mentioned technical challenges in public interviews/PR (awareness of gap)
- Transitioning from traditional CG to AI pipeline (infrastructure rebuild = buying window)
- 25x+ output target increase (e.g. 6部/月 → 400集/年) (cannot be met without tools)

**Medium signals (weight: MEDIUM)**:
- Competitor just raised / launched (urgency)
- New office / geographic expansion
- Issuing RFP or public partnership call
- Executives with a track record of adopting external tools

**Weak signals (weight: LOW)**:
- General industry growth / market tailwind
- Company age <2 years (still building, but budget may be tight)

**Output**:
- 信号1: {signal} — 强度: 高/中/低 — 来源: {source}
- 信号2: {signal} — 强度: 高/中/低 — 来源: {source}
- 信号3: {signal} — 强度: 高/中/低 — 来源: {source}
- 综合判断: {open buying window? / what triggers immediate outreach}

### 1g. Decision Makers (决策者识别)

Identify who makes purchasing decisions, their roles, and the best outreach channel.

**Sources**: 企查查 / 天眼查 (高管名单) / 脉脉 / LinkedIn / 百度百科 / 媒体报道 (采访/报道提及) / 公司官网 (团队页面) / 行业会议 speaker lists

**Output**:
- 创始人/CEO: {name, 脉脉/LinkedIn profile hint, public contact if available}
- CTO/技术负责人: {name, background, outreach angle}
- 其他决策者: {COO/产品VP/市场负责人 as applicable}
- 最佳触达渠道: {脉脉 / LinkedIn / 邮件 / 微信 / 电话 — with reasoning}
- 联系方式: {email/phone if publicly available, ❓ otherwise}
- 联系人获取策略: {e.g. 通过脉脉搜索 / 公司官网联系表单 / 行业会议接触}

**Contact hints**: If no direct contact is found, note the best way to get introduced (mutual connection, conference appearance, cold email to info@ forwarded etc.).

### 1h. Competitive Context (竞争格局)

Understand the company's competitors, their unique position in the market, and industry trends affecting them.

**Sources**: 媒体报道 (对比分析) / 行业分析报告 / 公司自身PR (对标声明) / 招聘JD (提及技术路线=竞争方向) / 投资方 portfolio (同一投资方投了哪些相关公司)

**Output**:
- 主要竞品: {competitor names and why}
- 差异化定位: {what makes them unique}
- 行业趋势: {trends affecting their business}
- 竞争压力: {e.g. 万兴科技入局 pressure / 头部平台挤压 / 价格战}
- 对我们的意义: {competition or partner? / how their competitive pressure creates our opportunity}

---

## Step 2: Lead Scoring (HOT / WARM / COLD)

Score each company on a 10-point scale based on five weighted dimensions.

### Scoring Weights

| Dimension | Weight | What to Evaluate |
|---|---|---|
| Funding | 25% | Recency, amount, investor quality |
| Hiring | 20% | Velocity, roles, team expansion signals |
| Pain Point Match | 25% | How well our product addresses their primary pain |
| Contact Accessibility | 15% | Can we reach a decision maker? How easily? |
| Competition/Urgency | 15% | Competitor pressure, stated urgency, timing window |

### Scoring Rubric

| Score | Classification | Meaning | Action |
|---|---|---|---|
| 8-10 | **HOT** (本周触达) | Funded within 6 months + hiring + clear pain point match | Contact this week. Route directly to outreach-generator. |
| 5-7 | **WARM** (2周内培育) | Recent hiring OR funding signal. Clear need but no urgency trigger. | Nurture within 2 weeks. Add to follow-up queue. Monitor for trigger events. |
| 1-4 | **COLD** (长期跟进) | No recent signals. Interesting company but no active buying window. | Add to long-term watchlist. Check back monthly or on trigger events. |

### Scoring Procedure

1. Evaluate each dimension independently (1-10 sub-score)
2. Multiply each sub-score by its weight
3. Sum to get total score (0-10)
4. Map to classification

```
Example:
  Funding      8/10 × 25% = 2.0
  Hiring       9/10 × 20% = 1.8
  Pain Match   9/10 × 25% = 2.25
  Contact      6/10 × 15% = 0.9
  Urgency      7/10 × 15% = 1.05
  ──────────────────────────────
  TOTAL:                   8.0 → HOT
```

### Tiebreaker Rules

When scores border between categories (e.g. 7.5 — between WARM and HOT):

- If funding recency + hiring velocity both point HOT → round up
- If no direct contact found → round down
- If the company has a competitor relationship (tool platforms like AniShort/巨日禄) → classify as "生态合作" instead of HOT/WARM/COLD, flag for partnership exploration

---

## Step 3: Output Format

For each company researched, produce a structured dossier in this format:

```markdown
## {company_name} — 企业调研档案

| 维度 | 详情 |
|------|------|
| 优先级 | {HOT/WARM/COLD} — 总分 {X/10} |
| 融资 | {summary: rounds, amounts, investors, dates} |
| 创始人 | {name, background, previous ventures} |
| 团队规模 | {current size, hiring velocity, trend} |
| 核心产品 | {product description, tech stack} |
| 代表作品 | {works with metrics: titles, view counts, platforms} |
| 痛点判断 | {inferred pain points with evidence and confidence markers} |
| 采购信号 | {specific signals with strength ratings} |
| 触达策略 | {recommended approach, channel, angle, timing} |
| 信息来源 | {URLs of all sources used} |
| 联系方式 | {email/phone/脉脉 if found, or contact acquisition strategy} |
```

Place the completed dossier in a research handoff file: `research-{company_slug}.md` (where slug is the company name in Latin-alphabet lowercase-hyphenated form, e.g. `research-lingjing-ai.md`).

---

## Step 4: Research Methodology

### Source Hierarchy

1. **Primary sources** (highest confidence): 公司官网 / 招聘JD / 企查查/天眼查 / GitHub / 公众号
2. **Secondary sources** (medium confidence): 36氪 / 投资界 / IT桔子 / 百度百科 / 媒体报道
3. **Tertiary sources** (lowest confidence): 社交媒体讨论 / 行业论坛 / 匿名评论

### Cross-Verification Rule

Every finding used in the final dossier must be cross-verified between at least 2 independent sources — or explicitly marked as unverified.

### Confidence Markers

| Marker | Meaning |
|---|---|
| **✅ verified** | Confirmed by 2+ independent primary sources |
| **🔶 inferred** | Logical inference from available evidence, not directly stated |
| **❓ unknown** | Could not be determined; explicitly note as gap |

### If ENScan_GO Is Available

If the ENScan_GO enterprise verification tool is installed, run it at the start of research for every Chinese-registered company:

```
enscan_go --company "{full_company_name}"
```

This provides verified registration data (legal name, registration number, capital, date, status) that serves as ground truth for Company Basics. If ENScan_GO is not available, use 企查查/天眼查 or the national enterprise credit system as fallback.

### Contradiction Handling

When sources disagree:

1. Note both versions in the dossier with sources
2. Flag the contradiction explicitly: "⚠️ 来源不一致: [{source A} vs {source B}]"
3. Give preference to primary sources and more recent data
4. If unresolvable, mark as ❓ and explain the discrepancy

### Privacy & Ethics

- Only collect information that is publicly available
- Do not attempt to access private data or use paid subscription services without authorization
- Do not generate speculative contact information (email guessing)
- Clearly distinguish between verified information and inference

---

## Step 5: Pipeline Integration

This skill is Stage 2 of the AI漫剧获客 pipeline:

```
lead-finder (Stage 1) → company-researcher (Stage 2) → outreach-generator (Stage 3)
```

### Input from lead-finder

If a lead was discovered by lead-finder, the following may already exist:
- Company name, website (basic identity)
- Initial funding signal (if found)
- Initial hiring signal (if found)

Use these as starting points. The company-researcher's job is to deepen and verify.

### Output to outreach-generator

After completing the dossier, route to `outreach-generator` by providing:
- `company_name`: for template variable substitution
- `founder_name` / `decision_maker`: for personalization
- `funding_status`: for template selection (Template A for funded)
- `hiring_signals`: for template selection (Template B for hiring)
- `pain_points`: for message content
- `preferred_channel`: from decision maker analysis
- `scoring_classification`: HOT → immediate outreach, WARM → nurture sequence, COLD → monitor

The research handoff file (`research-{company_slug}.md`) serves as the bridge between stages.

---

## Self-Check

After completing a company research dossier, verify against this checklist:

```
[ ] All 8 research dimensions covered (Company Basics / Funding / Team / Products / Pain Points / Purchase Signals / Decision Makers / Competitive Context)
[ ] Each finding cross-verified by 2+ sources or explicitly marked as inferred
[ ] Confidence markers applied: ✅ verified / 🔶 inferred / ❓ unknown
[ ] Contradictions flagged if sources disagree
[ ] Lead scored by the 5-dimension weighted rubric
[ ] Score mapped to HOT/WARM/COLD with justification
[ ] Actionable outreach strategy recommended (channel, angle, timing)
[ ] Decision maker identified (or explicit "not found" with acquisition strategy)
[ ] Handoff file ready: research-{company_slug}.md
[ ] Sources listed with URLs
```

---

## Reference Files

| File | Purpose |
|---|---|
| `../../references/AI漫剧获客-Top10线索表.md` | Example output showing expected quality and detail level |
| `../../references/AI漫剧获客-行业话术模板库.md` | Outreach templates that consume research output |
| `../lead-finder/` | Stage 1 pipeline — lead discovery |
| `../../outreach-generator/` | Stage 3 pipeline — personalized outreach message generation |

The Top 10 线索表 at the reference path shows the expected depth: per-company dossiers with verified funding data, representative works with view counts, founder backgrounds, inferred pain points with source evidence, and clear prioritization by scoring.
