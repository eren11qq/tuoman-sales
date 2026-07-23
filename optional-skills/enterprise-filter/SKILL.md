---
name: enterprise-filter
description: Three-mode lead scoring for AI漫剧 sales pipeline
platforms: [win32, linux]
argument-hint: "<mode: signal|bant|icp> <leads JSON or file path>"
triggers:
  - "打分"
  - "筛选"
  - "enterprise-filter"
  - "线索打分"
  - "线索筛选"
  - "优先级排序"
  - "filter"
handoff: filtered-leads-{timestamp}.json
---

<Purpose>
Take raw or researched lead profiles (output of company-researcher or manual input) and produce a ranked, prioritized list for outreach. Supports three evaluation modes — Signal Scoring for batch filtering, BANT for pre-outreach qualification, and ICP Matching for strategic pipeline building. Each mode scores leads on different dimensions; combining all three produces a final meta-score.

This skill sits in the pipeline after company-researcher (which produces lead dossiers) and before outreach-generator (which produces personalized copy). Its output drives the outreach priority order and informs which template/channel to use.

Reference: The Top 10 scored leads table at `../../references/AI漫剧获客-Top10线索表.md` shows the output format this skill produces.
</Purpose>

<Use_When>
- User has a batch of lead profiles and needs them sorted by priority
- User says "打分", "筛选", "线索打分", "线索筛选", "优先级排序", "filter"
- User needs to determine which leads are HOT (immediate outreach) vs WARM (nurture) vs COLD (long-term)
- User needs BANT qualification before allocating sales time
- User needs to check leads against ICP (Ideal Customer Profile)
- User has just finished company research and needs ranking before outreach generation
</Use_When>

<Do_Not_Use_When>
- User needs to research a company from scratch (use company-researcher first)
- User needs to generate outreach copy after ranking (use outreach-generator)
- User needs a general CRM or lead management tool — this is a one-shot scoring pass
- User has fewer than 3 leads (manual assessment is faster)
</Do_Not_Use_When>

---

## Mode 1: Signal Scoring (信号评分)

Use for **initial batch filtering** when you have 10+ raw or researched leads. Assigns scores based on 20+ weighted signals across six categories.

### Scoring Categories and Weights

| Category | Weight | Description |
|---|---|---|
| Funding signals | 25% | Recent funding events, total amount raised |
| Hiring signals | 20% | Active job postings, AI-related roles, hiring volume |
| Product signals | 20% | Shipped products, output volume, hit works, iteration pace |
| Team signals | 15% | Team size, growth trajectory, office expansion |
| Contact accessibility | 10% | Decision-maker contact availability |
| Pain point match | 10% | Documented or inferred pain point fit with product |

### Signal Score Table (each sub-signal scored 0-3)

**Funding signals (weight: 25%)**:
| Signal | Score |
|---|---|
| Recent funding (<3 months) | 3 |
| Recent funding (3-6 months) | 2 |
| Any funding history | 1 |
| No funding signals | 0 |
| Bonus: Funding amount >1000万 | +1 |

**Hiring signals (weight: 20%)**:
| Signal | Score |
|---|---|
| Currently hiring AI-related roles | 3 |
| Currently hiring any roles | 2 |
| No hiring signals detected | 0 |
| Bonus: Recent hiring posts (<30 days) | +1 |
| Bonus: Hiring 5+ positions simultaneously | +1 |

**Product signals (weight: 20%)**:
| Signal | Score |
|---|---|
| Has shipped AI comic/animation product | 3 |
| Monthly output >100 episodes | 2 |
| Has hit work (>1000万 views) | 1 |
| No public product signals | 0 |
| Bonus: Active iteration (updates in last 3 months) | +1 |

**Team signals (weight: 15%)**:
| Signal | Score |
|---|---|
| Team size >100 | 3 |
| Team size 30-100 | 2 |
| Team size <30 | 1 |
| Team size unknown | 0 |
| Bonus: Growing (hiring + new office) | +1 |

**Contact accessibility (weight: 10%)**:
| Signal | Score |
|---|---|
| Decision maker contact found | 3 |
| Company email/phone available | 2 |
| Only social media (脉脉/LinkedIn) | 1 |
| No contact path found | 0 |

**Pain point match (weight: 10%)**:
| Signal | Score |
|---|---|
| Clear, documented pain point matching product | 3 |
| Inferred pain point with supporting evidence | 2 |
| Generic industry pain point only | 1 |
| No pain point identified | 0 |

### Calculation

```
raw_total = sum(signal_scores) + sum(bonuses)
weighted_score = (
    (funding_score / max_funding * 25) +
    (hiring_score / max_hiring * 20) +
    (product_score / max_product * 20) +
    (team_score / max_team * 15) +
    (contact_score / max_contact * 10) +
    (pain_score / max_pain * 10)
)
final_score = normalize(weighted_score, 1-10)
```

---

## Mode 2: BANT Qualification

Use for **pre-outreach qualification** to decide sales resource allocation. Evaluates each lead on Budget, Authority, Need, and Timeline.

### Budget — Can they pay?

| Signal | Verdict | Score |
|---|---|---|
| Funded (any round) | YES | 3 |
| Revenue-generating (public revenue data) | YES | 3 |
| Hiring aggressively (implies budget) | LIKELY | 2 |
| Unknown / No signals | UNCLEAR | 0 |

### Authority — Can they decide?

| Signal | Verdict | Score |
|---|---|---|
| Founder/CEO contactable | YES | 3 |
| Tech VP / Department head reachable | YES | 2 |
| Can reach but not decision maker | PARTIAL | 1 |
| No decision path found | NO | 0 |

### Need — Do they need this?

| Signal | Verdict | Score |
|---|---|---|
| Documented pain point matching product | YES | 3 |
| Inferred strong need (hiring for related roles, expanding AI output) | LIKELY | 2 |
| Generic industry need only | WEAK | 1 |
| No need identified | NO | 0 |

### Timeline — When will they buy?

| Signal | Verdict | Score |
|---|---|---|
| Active hiring + recent funding | NOW | 3 |
| Either hiring OR funding confirmed | <3 MONTHS | 2 |
| No urgency signals (company mature, no expansion) | >3 MONTHS | 1 |
| Company seems stagnant (no hires, no news, no funding) | UNKNOWN | 0 |

### BANT Tiers

| BANT Total | Tier | Action |
|---|---|---|
| 10-12 | HOT | Allocate sales time immediately |
| 7-9 | WARM | Nurture within 2 weeks |
| 0-6 | COLD | Long-term pipeline or re-evaluate |

---

## Mode 3: ICP Matching (理想客户画像)

Use for **strategic pipeline building** when evaluating whether a lead fits the ideal customer profile for AI漫剧获客.

### ICP Definition for AI漫剧获客

| Dimension | Target |
|---|---|
| Industry | AI内容制作 / AI短剧平台 / AI动画公司 |
| Team size | 30-500 people |
| Stage | Seed to Series B |
| Geography | China (domestic), with expansion potential to SE Asia / Japan / Korea |
| Tech maturity | Using AI tools, likely self-built some pipeline |
| Pain point fit | Has capacity / quality / consistency bottleneck |
| Budget signal | Funded or revenue-generating |

### Scoring Rubric

Each dimension scored 0-3, then averaged to produce a percentage:

| Dimension | 3 (Perfect Match) | 2 (Good Match) | 1 (Partial) | 0 (Mismatch) |
|---|---|---|---|---|
| Industry | AI内容制作 | AI短剧平台 | AI动画公司 | Other / unrelated |
| Team size | 30-100 | 100-500 | 10-30 or 500+ | <10 |
| Stage | Angel to Series A | Seed or Series B | Series C+ / Pre-seed | No stage info / bootstrapped |
| Geography | China + SE Asia / Japan / Korea | China only | SE Asia / Japan / Korea only | Other regions |
| Tech maturity | Self-built pipeline + using AI tools | Using AI tools only | Self-built but no AI | No tech signals |
| Pain point fit | Clear documented bottleneck | Inferred bottleneck | Generic industry challenge | No bottleneck identified |
| Budget signal | Funded + revenue | Funded | Revenue-generating | No budget signal |

### ICP Fit Tiers

| ICP Fit % | Tier | Action |
|---|---|---|
| 80-100% | CORE ICP | Top priority for pipeline |
| 50-79% | ADJACENT ICP | Worth pursuing, may need tailored pitch |
| 0-49% | OUT OF SCOPE | Deprioritize or route to partnership track |

---

## Combined Ranking

When using all three modes together, the final priority score is a weighted combination:

```
Final Priority Score = Signal Score (40%) + BANT Score (35%) + ICP Fit (25%)
```

### Priority Tiers

| Final Score | Priority | Action Window |
|---|---|---|
| 8.0-10.0 | HOT | 本周触达 |
| 6.0-7.9 | WARM | 2周内培育 |
| 4.0-5.9 | COLD | 长期跟进 |
| 0-3.9 | ON HOLD | Re-evaluate later |

---

## Special Classification Rules

### Platform/Tool Companies (工具平台型)

Companies like **八点八数字 (AniShort)** and **杭州巨日禄** that build AI tools/platforms for others.

- **Classification**: 渠道合作 (Partnership track), not 直销客户
- **Signal Scoring**: Run normally but cap at WARM priority — they are potential channel partners, not direct buyers
- **BANT**: Skip BANT for these; use BANT on their *customers* instead
- **ICP**: Run ICP but flag as "渠道合作" in output
- **Output note**: Route suggested action to "生态合作 / 技术集成" not "销售触达"

### Competitor-Locked Companies (竞品绑定型)

Companies like **灵漫快创** (locked to 万兴科技/万兴剧厂) where a competitor relationship is confirmed.

- **Classification**: 竞品绑定
- **Signal Scoring**: Score normally but flag for verification
- **BANT**: Run fully — competing products rarely cover 100% of workflow needs
- **ICP**: Run normally
- **Output note**: Flag specific tooling gaps — what does the competitor product NOT cover? That is the entry point.

### No-Contact Companies (触达路径缺失)

Companies where no contact path (email, phone, 脉脉, LinkedIn) can be found.

- **Classification**: 触达路径缺失
- **Signal Scoring**: Run normally (score still useful for pipeline)
- **BANT**: Authority will be 0 (no decision path) — score capped at WARM max
- **ICP**: Run normally
- **Output note**: Assign a research task to find contact path before outreach

---

## Output Format

After scoring, present results as a ranked table:

```
Rank | Company | Score | Mode | Priority | Key Signal | Next Action
1    | 灵境AI   | 9.5   | Combined | HOT | 3轮融资+月产300部 | 本周邮件触达
2    | 星迹互动 | 9.5   | Combined | HOT | 天使轮+年底120人 | 本周脉脉触达
3    | 八点八数字 | 9.0 | Combined | HOT* | 近亿元+1万用户 | *渠道合作
4    | 国芯智造 | 8.5   | Combined | HOT | 3000万A轮+国企 | 商务邮件
5    | 星兴万物 | 8.5   | Combined | HOT | 2000万天使+118家供应商 | 脉脉触达
6    | 灵漫快创 | 8.0   | Combined | HOT* | 万兴投资+1.5亿播放 | *竞品绑定
7    | 奥睿森   | 7.5   | Combined | WARM | 200人+新设AI组 | 联系HR
8    | 浙江乐播 | 7.0   | Combined | WARM | 月产6→400部目标 | HR对接
9    | 巨日禄   | 7.5   | Combined | WARM* | AI漫画工具+A轮 | *渠道合作
10   | 西安启昱 | 6.5   | Combined | WARM | 新公司+招20人 | 联系HR房佳欣
```

### Detailed Lead Card

For each lead, provide a detailed scoring breakdown card:

```
### {Company Name}

**Signal Score**: X.X/10 | **BANT**: X/12 ({Tier}) | **ICP Fit**: XX%
**Combined Score**: X.X/10 | **Priority**: {HOT|WARM|COLD}

**Top 3 Signals**:
1. {strongest signal}
2. {second strongest}
3. {third strongest}

**Key Gap**: {weakest area / risk factor}

**Suggested Action**: {具体的下一步行动}

**Special Flags**: {渠道合作|竞品绑定|触达路径缺失} (if applicable)
```

---

## Self-Check

After producing a ranked lead list, verify against this checklist:

```
[ ] All scored leads have a numeric score and priority tier
[ ] Funding signals checked against verified sources (36氪/投资界/DoNews)
[ ] Hiring signals verified against active job postings
[ ] Platform/tool companies flagged as "渠道合作" not "直销客户"
[ ] Competitor-locked companies flagged as "竞品绑定" with gap analysis
[ ] No-contact companies flagged with research task assignment
[ ] HOT leads have a specific next action and timeline
[ ] BANT totals correctly categorized (HOT >=10, WARM 7-9, COLD <=6)
[ ] ICP fit percentage calculated correctly
[ ] Combined score uses correct weighting (40/35/25)
```

---

## Data Sources for Signal Verification

When scoring leads, prefer verified data from:

| Signal Type | Preferred Sources |
|---|---|
| Funding | 36氪, 投资界, DoNews, 企查查, 天眼查 |
| Hiring | BOSS直聘, 拉勾, LinkedIn, 脉脉, 鱼泡直聘 |
| Product | 36氪, company website, 抖音/B站 official accounts |
| Team | ENScan_GO (工商数据), 企查查, company LinkedIn |
| Contact | 脉脉, LinkedIn, company website "联系我们" page |
| Revenue | Public interviews, press releases, investor decks |

Cross-reference at least two independent sources per scored lead before assigning final scores.

---

## Integration Notes

This skill is the **second stage** in the AI漫剧获客 pipeline:

```
公司研究 (company-researcher) → 线索评分 (enterprise-filter) → 触达生成 (outreach-generator)
```

- **Input from**: company-researcher output (lead dossiers with funding, hiring, team, product data)
- **Output to**: outreach-generator (ranked priority list informs which leads to contact first)
- **Stock output file**: `filtered-leads-{timestamp}.json` in the working directory
