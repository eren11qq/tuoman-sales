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
Take raw or researched lead profiles and produce a ranked, prioritized list for outreach. Supports three evaluation modes — Signal Scoring for batch filtering, BANT for pre-outreach qualification, and ICP Matching for strategic pipeline building.
</Purpose>

<Use_When>
- User has a batch of lead profiles and needs them sorted by priority
- User says "打分", "筛选", "线索打分", "优先级排序"
- User needs BANT qualification before allocating sales time
- User needs to check leads against ICP (Ideal Customer Profile)
</Use_When>

---

## Mode 1: Signal Scoring (信号评分)

| Category | Weight | Description |
|---|---|---|
| Funding signals | 25% | Recent funding events, total amount raised |
| Hiring signals | 20% | Active job postings, AI-related roles |
| Product signals | 20% | Shipped products, output volume, hit works |
| Team signals | 15% | Team size, growth trajectory |
| Contact accessibility | 10% | Decision-maker contact availability |
| Pain point match | 10% | Documented or inferred pain point fit |

## Mode 2: BANT Qualification

| Criteria | Score 3 | Score 2 | Score 1 | Score 0 |
|---|---|---|---|---|
| Budget | Funded | Revenue-gen | Unknown | No signal |
| Authority | CEO contactable | Tech VP reachable | Partial path | No path |
| Need | Doc'd pain match | Inferred strong need | Generic need | None |
| Timeline | Hiring+Funding | Either hiring OR funding | No urgency | Stagnant |

**Tiers**: 10-12 HOT, 7-9 WARM, 0-6 COLD

## Mode 3: ICP Matching

**ICP for AI漫剧获客**:
| Dimension | Target |
|---|---|
| Industry | AI内容制作 / AI短剧平台 / AI动画公司 |
| Team size | 30-500 people |
| Stage | Seed to Series B |
| Geography | China, with expansion to SE Asia / Japan / Korea |
| Pain point fit | Has capacity / quality / consistency bottleneck |

## Combined Ranking

```
Final Priority Score = Signal Score (40%) + BANT Score (35%) + ICP Fit (25%)
```

| Score | Priority | Action |
|---|---|---|
| 8.0-10.0 | HOT | 本周触达 |
| 6.0-7.9 | WARM | 2周内培育 |
| 4.0-5.9 | COLD | 长期跟进 |
| 0-3.9 | ON HOLD | Re-evaluate later |

## Output Format

```
Rank | Company | Score | Mode | Priority | Key Signal | Next Action
1    | 灵境AI   | 9.5   | Combined | HOT | 3轮融资+月产300部 | 本周邮件触达
```
