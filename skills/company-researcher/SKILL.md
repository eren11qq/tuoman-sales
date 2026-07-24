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
</Purpose>

<Use_When>
- User provides a company name and asks for deep research
- User says "调研", "深度调研", "企业调研", "查一下这家公司"
- A lead has been discovered and needs profiling before outreach
- User needs a structured dossier for pipeline review or CRM entry
</Use_When>

---

## Research Dimensions (All 8 Required)

### 1. Company Basics (企业基本信息)
Verify the full legal name, registration location, establishment date, enterprise type, and registered capital.
**Sources**: 企查查 / 天眼查 / 国家企业信用信息公示系统 / company website

### 2. Funding & Financial (融资与财务)
Track total funding raised, individual rounds (dates + amounts + investors), revenue estimates.
**Sources**: 36氪 / 投资界 / 企查查 / 天眼查 / IT桔子

### 3. Team & Hiring (团队与招聘)
Founder background, team size, hiring velocity, key executives.
**Sources**: Boss直聘 / 猎聘 / 脉脉 / LinkedIn / 企查查 / 百度百科

### 4. Products & Tech Stack (产品与技术栈)
Core product(s), tech stack, monthly output volume, representative works.
**Sources**: 公司官网 / 微信公众号 / 媒体报道 / 招聘JD

### 5. Pain Points (痛点判断)
Infer pain points from public signals using the framework below.

**Inference framework**:
| Company Type | Default Pain Hierarchy |
|---|---|
| 内容制作公司 | 产能 > 质量一致性 > 出海本地化 > 成本控制 |
| 技术平台/工具公司 | 用户留存 > 功能完善度 > 差异化 > 商业化 |
| 国有/国资控股 | 信创合规 > 数据安全 > 预算流程 > 效率提升 |

### 6. Purchase Signals (采购信号)
Identify signals that indicate active buying window.
**Strong signals**: Recent funding (<6mo), hiring velocity >5 positions/30d, transitioning from CG to AI pipeline.

### 7. Decision Makers (决策者识别)
Identify who makes purchasing decisions and best outreach channel.
**Sources**: 企查查 / 脉脉 / LinkedIn / 百度百科 / 媒体报道

### 8. Competitive Context (竞争格局)
Competitors, unique position, industry trends.
**Sources**: 媒体报道 / 行业分析 / 公司PR / 投资方portfolio

---

## Lead Scoring

Score each company on a 10-point scale:

| Dimension | Weight | Evaluate |
|---|---|---|
| Funding | 25% | Recency, amount, investor quality |
| Hiring | 20% | Velocity, roles, expansion signals |
| Product | 20% | Shipped products, output volume, hit works |
| Team | 15% | Team size, growth trajectory |
| Contact Accessibility | 10% | Can we reach a decision maker? |
| Pain Point Match | 10% | How well our product addresses their pain |

**Tiers**: 8-10 HOT (本周触达), 5-7 WARM (2周内培育), 1-4 COLD (长期跟进)

## Output Format

```markdown
## {company_name} — 企业调研档案

| 维度 | 详情 |
|------|------|
| 优先级 | {HOT/WARM/COLD} — 总分 {X/10} |
| 融资 | {summary} |
| 创始人 | {name, background} |
| 团队规模 | {current size, hiring velocity} |
| 核心产品 | {product description, tech stack} |
| 痛点判断 | {inferred pain points with evidence} |
| 采购信号 | {specific signals with strength ratings} |
| 触达策略 | {recommended approach, channel, angle} |
```

Place dossier in: `research-{company_slug}.md`
