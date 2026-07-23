---
name: outreach-generator
description: >
  基于深度研究为合格潜在客户生成个性化多渠道外展消息：邮件、企业微信、钉钉、飞书和短信，支持按客户温度分级模板。
platforms: [linux, macos, windows]
version: 1.0.0
author: AI Comic Sales Agent
license: MIT
category: sales-outreach
metadata:
  hermes:
    tags: [sales, customer-acquisition, ai-comic, china, outreach-generator]
---

# 外展消息生成器 (Outreach Generator)

## When to Use

- 当研究代理完成对某个潜在客户的深度分析并返回"合格"状态时自动激活。
- 需要为 AI 漫画/视频行业的潜在客户生成个性化外展消息时。
- 需要进行多渠道触达（邮件、企业微信、钉钉、飞书、短信）时。
- 需要根据客户温度（HOT/WARM/COLD）采用不同外展策略时。
- 需要制定后续跟进计划和跟踪方案时。

## When NOT to Use

- 潜在客户尚未经过研究代理验证，仍处于 SCRAPE 或 ANALYZE 阶段。
- 潜在客户状态为 REJECTED 或 INELIGIBLE。
- 客户已明确要求不接收营销消息（取消订阅或列入拒绝联络名单）。
- 夜间黑名单时段（默认 22:00-08:00 北京时间），除非客户明确标记为紧急。
- 同一客户在上次触达后 72 小时内不允许重复发送，除非是计划中的跟进节点。

## Tools Required

### MCP 工具

| 工具 | 用途 |
|------|------|
| **Austin** | 统一消息发送网关，支持邮件、企业微信、钉钉、飞书、短信，内置夜间黑名单保护 |
| **BillionMail** | 批量邮件发送，支持 AI 模板渲染和投递追踪 |
| **Message-Pusher** | 轻量级单文件通知推送，适合快速短信/即时消息 |
| **Hermes Gateway** | 飞书/Slack Webhook 集成，用于内部通知和日志记录 |
| **CordysCRM** | 客户关系管理，记录所有外展活动日志 |

### 前置依赖

- 研究代理输出物：每个客户的 `research_report.json`（包含痛点分析、联系人信息、公司背景、客户温度评级）
- 客户画像数据库：联系人的姓名、职位、行业、公司名称

## Procedure

### 第 1 步：读取研究数据

从研究代理的输出目录加载目标客户的 `research_report.json`：

```bash
cat ./research-outputs/{customer-slug}/research_report.json
```

验证必填字段：
- `lead_temperature`：必须为 `HOT`、`WARM` 或 `COLD`
- `contact_name`：联系人姓名
- `contact_email`：邮箱地址
- `pain_points`：至少包含 1 个痛点
- `company_name`：公司名称

### 第 2 步：确定外展策略

根据 `lead_temperature` 选择策略：

**HOT 客户**（明确痛点 + 预算 + 主动寻找解决方案）：
- 渠道优先级：邮件 + 企业微信 + 电话（三管齐下）
- 时间窗口：24 小时内触达，48 小时后无回复则跟进
- 内容基调：直接点出痛点，用具体数据证明你理解他们

**WARM 客户**（痛点存在但不紧急）：
- 渠道优先级：邮件 + 内容营销
- 时间窗口：先建立关系，2 周后再试探
- 内容基调：提供有价值的行业洞察，而非推销

**COLD 客户**（需求不明确）：
- 不主动触达，仅关注其社交媒体动态
- 触发条件：当他们公开发帖抱怨痛点 / 发布招聘 / 披露融资新闻时自动触发外展

### 第 3 步：选择行业模板

根据客户所在细分领域选择模板：

- **AI 漫画工作室**（产能瓶颈）：使用 Template 1 — 直击产能不足的痛点
- **AI 视频公司**（效率瓶颈）：使用 Template 2 — 强调生成效率和速度
- **MCN/内容机构**（规模化瓶颈）：使用 Template 3 — 聚焦批量生产和成本控制

### 第 4 步：生成个性化外展消息

调用 Austin MCP 工具的 `draft_message` 方法，传入以下参数：

```
draft_message(
  template_type: "ai_comic_studio" | "ai_video_company" | "mcn_agency",
  contact_name: "张三",
  company_name: "某科技",
  pain_points: ["渲染速度慢", "人力成本高"],
  custom_praise: "您最近在 Bilibili 发布的漫画系列色彩处理非常出色",
  channel: "email" | "wecom" | "dingtalk" | "feishu" | "sms"
)
```

关键规则：
- 每条消息必须引用研究报告中至少一个具体发现（不可使用完全相同的内容）
- 邮件必须包含退订选项
- 企业微信/钉钉/飞书版本应比邮件更短、更口语化（通常为邮件长度的 30-40%）
- 短信版本限制在 70 个字符以内（中文）

### 第 5 步：多渠道适配

对每条生成的消息执行渠道适配：

```bash
# 示例：将邮件模板转换为企业微信风格
# 1. 长度缩减至原文 30%
# 2. 去掉正式问候语，改为口语化开头
# 3. 保留核心价值主张和行动号召
```

各渠道输出清单：
1. 邮件正文（HTML + 纯文本双版本）
2. 企业微信/钉钉消息（简短版，含 @ 提及格式）
3. 飞书消息（支持富文本格式）
4. 短信（70 字符以内）

### 第 6 步：制定跟进计划

为每条外展生成跟进时间表：

```
HOT:   T+0h → 初始触达（邮件+企微+电话）
       T+48h → 如无回复，发送案例研究
       T+7d → 如仍无回复，发送最后提醒

WARM:  T+0h → 发送行业洞察邮件
       T+14d → 试探性询问需求
       T+28d → 分享客户成功案例

COLD:  被动监测 → 触发条件满足时自动外展
```

### 第 7 步：记录到 CRM

调用 CordysCRM 记录所有外展活动：

```bash
hermes crm log-outreach \
  --customer-id {id} \
  --channels "email,wecom" \
  --message-ids "msg_001,msg_002" \
  --followup-date "2026-07-30"
```

### 第 8 步：发送消息

使用 Austin 统一网关发送：

```bash
hermes austin send \
  --customer-id {id} \
  --channel email \
  --template outreach \
  --body-file ./outputs/{customer-slug}/email_draft.txt \
  --tracking yes \
  --no-blackout-check false
```

对于批量发送，使用 BillionMail：

```bash
hermes billionmail batch-send \
  --campaign "AI-Comic-Q3-Outreach" \
  --recipients-file ./outputs/batch-recipients.csv \
  --template outreach \
  --schedule "2026-07-24T09:00:00+08:00"
```

## Output Format

为每个客户生成一个目录，包含以下文件：

```
outputs/{customer-slug}/
├── email_draft.md          # 邮件草稿（Markdown，含 HTML 和纯文本）
├── email_draft.txt         # 纯文本邮件
├── wecom_message.txt       # 企业微信消息
├── dingtalk_message.txt    # 钉钉消息
├── feishu_message.json     # 飞书富文本消息（JSON 格式）
├── sms.txt                 # 短信内容（≤70 字符）
├── channel_priority.json   # 推荐渠道优先级
├── followup_schedule.json  # 跟进时间表
├── tracking_plan.json      # 追踪方案
└── outreach_log.json       # 外展活动摘要（供 CRM 系统使用）
```

### channel_priority.json 示例

```json
{
  "customer_slug": "ai-comic-studio-sz",
  "lead_temperature": "HOT",
  "channels": [
    {"channel": "email", "priority": 1, "reason": "正式商务沟通首选"},
    {"channel": "wecom", "priority": 2, "reason": "中国团队常用即时通讯工具"},
    {"channel": "phone", "priority": 3, "reason": "HOT 客户需电话确认意向"}
  ],
  "followup_schedule": [
    {"day": 0, "action": "初始三渠道触达"},
    {"day": 2, "action": "如未回复，发送案例研究"},
    {"day": 7, "action": "如仍无回复，发送最后提醒"}
  ]
}
```

### tracking_plan.json 示例

```json
{
  "customer_slug": "ai-comic-studio-sz",
  "tracking_method": "billionmail+pixel",
  "metrics": ["open_rate", "click_rate", "reply_rate", "wecom_read"],
  "success_criteria": {
    "open_rate": ">40%",
    "reply_rate": ">10%",
    "response_time": "<48h"
  },
  "escalation": "If no open within 72h, switch channel to SMS"
}
```

## Verification

1. **必填字段检查**：确认每个输出文件存在且非空
2. **个性化检查**：用 grep 确认邮件中引用了研究报告中至少一个具体事实
   ```bash
   grep -q "{specific_fact}" ./outputs/{customer-slug}/email_draft.md || echo "缺少个性化引用"
   ```
3. **退订选项检查**：确保邮件中包含退订链接或说明
   ```bash
   grep -qi "退订\|unsubscribe" ./outputs/{customer-slug}/email_draft.md || echo "缺少退订选项"
   ```
4. **短信长度检查**：确认短信内容不超过 70 个中文字符
   ```bash
   sms_length=$(wc -m < ./outputs/{customer-slug}/sms.txt)
   [ "$sms_length" -le 70 ] || echo "短信超长: ${sms_length} 字符"
   ```
5. **黑名单时段检查**：确认计划发送时间不在 22:00-08:00 范围内（Austin 内置保护，此为二次确认）
6. **CRM 日志验证**：确认 CordysCRM 中已记录该外展活动
   ```bash
   hermes crm verify-log --customer-id {id} --activity-type outreach
   ```

## Example

### 场景：AI 漫画工作室 HOT 客户外展

**输入 — research_report.json 摘要：**
```json
{
  "customer_slug": "comicwave-studio",
  "contact_name": "李明",
  "contact_email": "liming@comicwave.cn",
  "company_name": "漫波工作室",
  "lead_temperature": "HOT",
  "pain_points": ["漫画上色环节占用 60% 人力", "月产能瓶颈 120 话"],
  "recent_activity": "在即刻发帖抱怨 AI 上色工具效果不稳定",
  "industry": "AI 漫画工作室"
}
```

**生成的邮件草稿（email_draft.md）：**

```
主题：漫波工作室的上色瓶颈 — 我们或许能帮忙

李明，你好：

我最近一直在关注漫波工作室的作品，尤其是你们在腾讯动漫上的《星海》系列，
分镜和人物设计都非常出色。

我注意到你在即刻上提到 AI 上色工具效果不稳定的问题。这确实是很多 AI 漫画
团队都会遇到的瓶颈 — 工具要么输出质量不稳定，要么需要大量人工修正，
导致上色环节仍然占据团队 60% 的精力。

我们专门为漫画上色这个场景做了一个工具，核心思路是用风格锚定代替参数调优：
只需提供一张你满意的参考页，工具会自动将整话的对齐到同一风格，
在内部测试中帮助团队将上色环节的时间压缩了 70%。

你有兴趣了解一下吗？两个选择：
a) 我安排一个 5 分钟演示，直接给你看效果
b) 我发一份案例研究，介绍另一家漫画工作室是怎么用它的

如果你不感兴趣，回复"不"我就不会再打扰。

祝好，
[你的名字]
[公司名称]

—
如需退订此类邮件，请回复"退订"。
```

**执行命令：**

```bash
# 1. 生成所有渠道消息
hermes austin draft_message \
  --research-report ./research-outputs/comicwave-studio/research_report.json \
  --template ai_comic_studio \
  --output-dir ./outputs/comicwave-studio/

# 2. 发送邮件
hermes austin send \
  --customer-id comicwave-studio \
  --channel email \
  --body-file ./outputs/comicwave-studio/email_draft.txt \
  --tracking yes

# 3. 发送企业微信消息（延迟 30 分钟，避开同时触达的压迫感）
hermes austin send \
  --customer-id comicwave-studio \
  --channel wecom \
  --body-file ./outputs/comicwave-studio/wecom_message.txt \
  --delay 30m

# 4. 记录到 CRM
hermes crm log-outreach \
  --customer-id comicwave-studio \
  --channels "email,wecom" \
  --message-ids "msg_20260723_001,msg_20260723_002" \
  --followup-date "2026-07-25"

# 5. 设置 48 小时跟进提醒
hermes crm set-reminder \
  --customer-id comicwave-studio \
  --trigger "no_reply_48h" \
  --action "send_case_study"
```

**跟进时间表：**
- **D+0（今天）：** 发送邮件 + 企业微信
- **D+2（7月25日）：** 如无回复，发送案例研究
- **D+7（7月30日）：** 如仍无回复，发送最后提醒邮件