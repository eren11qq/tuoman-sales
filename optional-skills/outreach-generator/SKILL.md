---
name: outreach-generator
description: Personalized outreach for AI漫剧 industry leads
platforms: [win32, linux]
argument-hint: "<lead profile JSON or structured description>"
triggers:
  - "outreach"
  - "outreach-generator"
  - "拓客"
  - "获客"
  - "话术"
  - "触达文案"
handoff: outreach-{lead_slug}.md
---

<Purpose>
Given a lead profile (company, founder, funding, pain points, hiring signals, etc.), generate personalized outreach copy for that specific lead. Every message must be channel-appropriate, variable-substituted, and grounded in the recipient's actual situation — never generic.

This skill encodes the outreach methodology from the comprehensive template library at:
`../../references/AI漫剧获客-行业话术模板库.md`

That file contains the full 70+ variable reference, all 12 templates (A-L), and deep industry context. This skill references it but is self-contained for lead-to-copy generation.
</Purpose>

<Use_When>
- User provides a lead profile and asks for outreach copy
- User says "outreach", "拓客", "获客", "话术", "触达文案"
- User needs a personalized message for a specific AI漫剧 / content production / AI short drama company
- User needs to select the right channel and template for a given lead type
</Use_When>

<Do_Not_Use_When>
- User needs a general marketing文案 for social media posting (use a content skill instead)
- User needs to analyze a company without generating outreach (use a research skill)
- User asks for bulk/cold email spam — this skill generates personalized, researched messages per lead
</Do_Not_Use_When>

---

## Input: Lead Profile

The skill expects a lead profile containing at minimum:

| Field | Required | Description |
|---|---|---|
| `company_name` | Yes | Target company name |
| `founder_name` | Yes (if known) | Founder/decision-maker name |
| `contact_title` | Yes | Their title |
| `industry_segment` | Yes | e.g. "内容制作公司", "技术平台", "国有企业" |
| `funding_status` | Yes | e.g. "天使轮500万", "A轮2000万", "未融资" |
| `hiring_signals` | Recommended | Positions and counts being hired |
| `recent_news` | Recommended | Recent product launches, achievements, news |
| `pain_points` | Recommended | Known or inferred pain points |
| `preferred_channel` | Optional | 脉脉/LinkedIn/邮件/微信 |
| `reference_customer` | Optional | Similar customer for case reference |

If fields are missing, ask the user before generating.

---

## Step 1: Lead Classification

Classify the lead into one of three customer types and derive their core pain hierarchy:

### Type A: Content Production Companies (内容制作公司)
**Examples**: 灵境AI, 星迹互动, 灵漫快创
**Signals**: funded, high monthly output (月产数百部), growing team
**Decision-maker**: Founder/CEO or Tech VP
**Pain hierarchy**: 产能 > 质量一致性 > 出海 > 成本

### Type B: Platform/Tool Companies (技术平台/工具公司)
**Examples**: 八点八数字, 巨日禄
**Signals**: own product, user base, incomplete workflow coverage
**Decision-maker**: Product VP / Ecosystem Partnerships
**Pain hierarchy**: 用户留存 > 功能完善度 > 差异化 > 商业化

### Type C: State-Owned Enterprises (国有企业/国资控股)
**Examples**: 国芯智造
**Signals**: state-controlled, long decision cycles, large budgets
**Decision-maker**: Tech Department Head / IT Department
**Pain hierarchy**: 信创合规 > 数据安全 > 成本 > 效率

---

## Step 2: Channel Routing

Select channel based on lead profile:

| Lead Signal | Channel | Template |
|---|---|---|
| Just raised funding (HOT lead) | 脉脉 / LinkedIn DM | Template A (融资型企业) |
| Hiring aggressively (WARM lead) | 脉脉 / LinkedIn DM | Template B (招聘扩张型企业) |
| Platform/tool company, partnership angle | 脉脉 / LinkedIn DM | Template C (生态合作型) |
| SOE / large enterprise / formal | 商务邮件 | Template E (正式邮件) or F (短邮件) |
| Warm intro via mutual contact | 微信 | Template G (共同联系人引荐) |
| Cold, no obvious signal | 微信 / 脉脉 | Template H (冷触达) |
| 内容制作公司, capacity angle | 脉脉 / LinkedIn DM | Template I (产能切入) |
| 内容制作公司, quality/replication angle | 脉脉 / LinkedIn DM | Template J (质量一致性与爆款复制) |
| Tool platform, integration partnership | 脉脉 / LinkedIn DM | Template K (生态集成合作) |
| SOE, compliance/security angle | 商务邮件 | Template L (信创合规) |

**Channel characteristics:**
- **脉脉/LinkedIn**: limited characters, profile visible, first 30 characters decide open rate. Best for funded HOT leads and hiring WARM leads.
- **Email**: no character limit, supports attachments, may be forwarded. Best for SOE/formal scenarios. Subject line is critical.
- **WeChat**: private, instant, must be short. Best for warm intros and cold reach via existing connections.

---

## Step 3: Generate Outreach Copy

### 5 Core Principles (Mandatory)

Apply these five principles to every generated message:

1. **First sentence must reference the recipient's specific work/funding/hiring dynamic**
   - Proves you researched them. Never use generic openings.
   - Example: "恭喜{company_name}完成{funding_amount}{funding_round}." not "您好，我有一个合作想聊聊。"

2. **Pain point must be concrete and specific, never vague**
   - "角色一致性差" is weak. "第3集和第5集主角脸都不一样了" is strong.
   - Use numbers: "效率提升" -> "从{old_time}压缩到{new_time}"

3. **One message, one value proposition**
   - Each template targets exactly one pain point. Do not list features.
   - If the lead has multiple pain points, generate separate messages or choose the highest-priority one.

4. **End with a low-friction call to action**
   - Not "安排正式演示" but "方便聊15分钟吗"
   - Every CTA should be easy to say yes to.

5. **Every follow-up must carry new information**
   - Never send "checking in". Every follow-up must bring a new case, new data, or new angle.

### Template Selection

Based on the channel and lead classification from Steps 1-2, select the appropriate template from the library. The canonical templates are in `../../references/AI漫剧获客-行业话术模板库.md` (Templates A-L).

**IMPORTANT — Variable Rule**: Pain point descriptions and solution descriptions MUST use custom variables (`{specific_pain_point}`, `{solution_brief}`, `{one_sentence_how}`, `{core_capability}`), never hard-coded technical specifics like "ComfyUI workflow node" or "SDXL pipeline". Different products have different capabilities — the user will fill in their product's actual approach.

### Variable Substitution

Map the lead profile fields to template variables. Use the full variable reference at the template library file for all 70+ variables. Brief reference for the most common variables:

**Your info** (must be filled by user before generation):
- `{your_name}`, `{your_product}`, `{your_role}`, `{your_contact}`, `{your_phone}`, `{your_email}`, `{your_website}`, `{your_price}`

**Lead info** (from profile):
- `{founder_name}`, `{contact_name}`, `{contact_title}`, `{company_name}`, `{department}`, `{company_characteristic}`
- `{work_title}`, `{hit_work}`, `{view_count}`, `{monthly_output}`, `{team_size}`
- `{funding_amount}`, `{funding_round}`, `{funding_detail}`
- `{hiring_position}`, `{hiring_count}`, `{expansion_goal}`
- `{current_output}`, `{target_output}`
- `{platform_name}`, `{user_count}`, `{output_volume}`

**Pain/solution variables** (must be customized by user per product):
- `{specific_pain_point}`, `{key_problem}`, `{niche_scenario}`, `{relevant_process}`
- `{solution_brief}`, `{one_sentence_how}`, `{core_capability}`
- `{capability_1}`, `{evidence_1}`, `{capability_2}`, `{evidence_2}`, `{capability_3}`, `{evidence_3}`

**Evidence variables** (from user's track record):
- `{reference_customer}`, `{reference_count}`, `{reference_scenario}`, `{reference_output}`
- `{timeframe}`, `{metric}`, `{before}`, `{after}`, `{improvement}`, `{gain}`
- `{old_period}`, `{new_period}`, `{old_time}`, `{new_time}`

**Follow-up variables**:
- `{days_since_last}`, `{new_insight_or_data}`, `{why_relevant}`, `{follow_up_period}`

> For the complete variable list (70+ entries), refer to Section 六 of the template library file.

---

## Step 4: Anti-Rejection Response Routing

When a lead responds with an objection, route to the appropriate counter:

| Lead Response | Counter Template | Strategy |
|---|---|---|
| "我们已经有工具了" | Scenario 1 | Acknowledge, then position as complementary for the niche gap. Use the kitchen knife analogy. |
| "太忙了，没时间" | Scenario 2 | Acknowledge their pace, ask ONE specific question. If worth answering, continue. |
| "我们自己能做" | Scenario 3 | Acknowledge their capability, then raise the hidden cost of self-build (maintenance > initial build). |
| "预算不够" | Scenario 4 | Reframe as ROI: cost of not having the solution vs. price. Give a graceful exit timeline. |
| "要跟团队商量" | Scenario 5 | Provide a ready-to-forward summary. Offer to do an internal demo/share. |
| No response (2nd touch) | Scenario 6 | Bring new data/insight. Give them an easy out. |
| No response (3rd touch) | See Day 7 below | Graceful retreat. |

Each counter-scenario is detailed in Section 四 of the template library file.

---

## Step 5: Follow-Up Cadence (7-Day Sequence)

When generating a full outreach sequence, structure as:

```
Day 1 (Tuesday 10:00):
  First message — template from Step 3.
  Must open with a specific reference to the lead's situation.

Day 3 (Thursday 14:30):
  Second touch — use Scenario 2 callback ("忙" angle) or Scenario 6 (no reply).
  Must carry NEW information (new case, new data, new industry angle).

Day 7 (next Tuesday 10:00):
  Final active touch — use Scenario 6 with graceful exit.
  "不是您优先方向也完全理解" — leaves the door open without pressure.

Day 14+:
  Move to nurture.
  Send industry insight briefing every 2 weeks (not product pitch).
  Reactivate when lead has new funding/hiring/product news.
```

---

## Self-Check

After generating outreach copy, verify against this checklist:

```
[ ] First sentence mentions specific lead info (work/funding/hiring — never generic)
[ ] Only one pain point addressed (not a feature list)
[ ] Contains specific numbers ("3x" not "显著提升")
[ ] Low-friction CTA ("15分钟聊聊" not "安排演示")
[ ] Passes the "group-send test" — ask: "Could this message be sent to anyone?"
[ ] Gives the recipient an easy graceful-out option
[ ] Pain/solution descriptions use variables, not hard-coded technical specifics
```

---

## Output Format

After generating, present the result in this structure:

---

### Lead: {company_name}

**Classification**: {Type A/B/C} | **Channel**: {脉脉/邮件/微信} | **Template**: {Template Letter}

**Generated Copy:**

```
[full message with variables substituted]
```

**Follow-up Plan:**
- Day 1: {what and when}
- Day 3: {what and when}
- Day 7: {what and when}
- Day 14+: {nurture strategy}

**Variables used:** {list of substituted variables}

---

## Template Reference

The canonical templates (A-L) and all 6 anti-rejection scenarios live in:
`../../references/AI漫剧获客-行业话术模板库.md`

This skill is a routing and generation layer on top of that library — always refer to it for exact template text and full variable definitions.
