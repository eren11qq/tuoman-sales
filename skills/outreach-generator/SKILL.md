---
name: outreach-generator
description: Personalized outreach message generation for AI漫剧 leads
platforms: [win32, linux]
argument-hint: "<company_name> [lead JSON]"
triggers:
  - "话术"
  - "outreach-generator"
  - "生成话术"
  - "触达文案"
  - "写触达"
  - "外联文案"
handoff: outreach-{company_slug}.md
---

<Purpose>
Given a lead dossier (from company-researcher or manual input), produce personalized, channel-appropriate outreach messages. Supports multiple channels (email, 脉脉, LinkedIn, 微信) and multiple templates based on lead signals.
</Purpose>

<Use_When>
- User has a researched lead and needs outreach copy
- User says "话术", "生成话术", "触达文案", "写触达", "outreach-generator"
- User needs channel-appropriate messaging (email vs 脉脉 vs LinkedIn)
- User needs multiple template variants to A/B test
</Use_When>

---

## Template Selection

Select template based on lead signals:

### Template A: Funded + Hiring (最热线索)
For leads with recent funding AND active hiring. Emphasize scalability, efficiency, and speed.

**Email subject**: `[公司]AI内容产能升级方案交流`
**Angle**: "看到贵司正在扩张AI内容团队，我们在AI漫剧生产流程优化方面有成熟方案..."

### Template B: Funded Only (融资型)
For leads with recent funding but no visible hiring surge.

**Email subject**: `祝贺[公司]新一轮融资 — AI内容生产合作`
**Angle**: "祝贺融资。我们在AI漫剧领域服务了X家同类公司，产能提升Y%..."

### Template C: Hiring Only (扩张型)
For leads actively hiring but no public funding.

**脉脉 angle**: "注意到贵司正在招聘AI相关岗位，我们在AI漫剧生产管线方面..."

### Template D: Research/Exploratory (培育型)
For cold/WARM leads with no strong signals.

**LinkedIn angle**: "对贵司在AI漫剧领域的探索印象深刻，我们在技术上有一些积累..."

---

## Channel Selection

| Channel | Best For | Template A | Template B | Template C | Template D |
|---|---|---|---|---|---|
| Email | Formal outreach,附件资料 | ✅ Best | ✅ Best | ✅ | ✅ |
| 脉脉 | Tech decision makers | ✅ | ✅ | ✅ Best | ✅ |
| LinkedIn | International/SE Asia | ✅ | ✅ | ✅ | ✅ Best |
| 微信 | Warm intro / existing connection | ✅ | ✅ | ✅ | ✅ |

---

## Variable Substitution

Every message must substitute:
- `{company_name}` — target company
- `{founder_name}` or `{decision_maker}` — personalization
- `{pain_point_match}` — specific pain point from research
- `{our_value_prop}` — tailored value proposition
- `{similar_company}` — reference customer (anonymized)

---

## Output Format

```
## {company_name} — 触达方案

### 推荐渠道: {channel}

### 触达文案:

{personalized message body}

### 备选渠道: {alternative channel}

{alternative message}

### 最佳发送时间: {recommended timing}
```
