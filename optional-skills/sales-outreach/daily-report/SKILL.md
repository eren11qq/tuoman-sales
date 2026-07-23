---
name: daily-report
description: >
  生成 AI 漫画客户获取日报，汇总当日管道指标、热门线索、温暖线索和行动项，并通过飞书 / Slack / 邮件推送给销售团队。
platforms: [linux, macos, windows]
version: 1.0.0
author: AI Comic Sales Agent
license: MIT
category: sales-outreach
metadata:
  hermes:
    tags: [sales, customer-acquisition, ai-comic, china, daily-report]
---

# 每日客户获取报告 (Daily Report)

## When to Use

- Hermes 定时任务在每天上午 9:00 自动触发。
- 销售团队需要一份汇总过去 24 小时管道活动的结构化日报。
- 需要将报告推送到飞书群、邮件或 Slack 等渠道。
- 销售总监需要查看每日热门线索和后续行动项。

## When NOT to Use

- 实时管道查询 —— 应直接查询 CordysCRM。
- 单条线索的详细分析 —— 使用 `company-researcher` 或 `lead-finder` 技能。
- 周报或月报 —— 这些需要不同的聚合逻辑和数据范围。
- 非销售用途的数据导出 —— 使用 CordysCRM 自带导出功能。
- Hermes cron 未配置或渠道凭证缺失时，不要强行执行。

## Tools Required

### MCP 工具
| 工具 | 用途 |
|------|------|
| `hermes-cron` | 定时调度，配置 `0 9 * * *` 每天上午 9:00 触发 |
| `hermes-gateway` | 消息推送网关，支持飞书 / Slack / Email |
| `lark-retro` | 飞书原生报告生成与推送 |
| `cordyscrm-lead-query` | 从 CordysCRM 拉取管道数据、联系人历史 |
| `cordyscrm-report-archive` | 将生成的报告存档到 CordysCRM |

### CLI 工具
| 命令 | 用途 |
|------|------|
| `hermes memory list --since "24h"` | 获取过去 24 小时管道中间状态 |
| `hermes skill run lead-finder --summary` | 获取今日新发现的线索摘要 |
| `hermes skill run company-researcher --summary` | 获取今日已完成的公司研报摘要 |
| `hermes skill run outreach-generator --summary` | 获取今日已发送的外展消息摘要 |
| `date +%Y-%m-%d` | 生成当天日期戳 |

## Procedure

1. **检查前置条件**
   - 确认 Hermes cron 服务正在运行：`hermes cron status`
   - 确认目标渠道凭证已配置：`hermes gateway status --channels feishu,email`
   - 确认 CordysCRM 连接正常：`hermes gateway health cordyscrm`

2. **收集数据源**
   - 从 CordysCRM 拉取管道指标：
     ```
     hermes gateway call cordyscrm-lead-query --metrics new,contacted,replied --since "24h"
     ```
   - 从 Hermes 内存读取今日中间状态：
     ```
     hermes memory list --since "24h" --tags pipeline,sales
     ```
   - 获取子技能输出摘要：
     ```
     hermes skill run lead-finder --summary --since "today"
     hermes skill run company-researcher --summary --since "today"
     hermes skill run outreach-generator --summary --since "today"
     ```

3. **计算指标**
   - 新线索数 = `lead-finder` 输出中今日新增条目数
   - 已研报数 = `company-researcher` 输出中今日完成条目数
   - 热门线索数 = CordysCRM 中标记为 "hot" 且今日有活动的线索数
   - 已联系数 = `outreach-generator` 输出中今日发送条目数
   - 回复数 = CordysCRM 中今日收到的回复数
   - 回复率 = 回复数 / 已联系数（若已联系数为 0 则显示 "-"）
   - 与昨日对比：查询昨日报告存档或重新计算昨日指标

4. **构建报告**
   - 按规范模板填充 Markdown 报告（见输出格式）。
   - 热门线索按评分降序排列，每条包含：
     - 痛点描述
     - 决策人及联系状态
     - 下一步建议
     - 联系历史（最近 3 条）
   - 温暖线索以表格形式列出，包含公司名、触点、下次联系时间。
   - 行动项从热门线索的 "建议" 字段和 CordysCRM 待办中提取。

5. **推送报告**
   - 主推送到飞书群（销售团队）：
     ```
     hermes gateway send feishu --group "ai-comic-sales" --content report.md
     ```
     或使用飞书原生方式：
     ```
     lark-retro send --chat-id "oc_xxx" --markdown report.md
     ```
   - 邮件抄送销售总监：
     ```
     hermes gateway send email --to "director@company.com" --subject "AI 漫画日报 [DATE]" --body report.md
     ```
   - 可选 Slack（远程团队）：
     ```
     hermes gateway send slack --channel "#sales-daily" --content report.md
     ```

6. **存档报告**
   - 将生成的报告存档至 CordysCRM：
     ```
     hermes gateway call cordyscrm-report-archive --type daily --file report.md
     ```
   - 记录执行日志：
     ```
     hermes log --skill daily-report --status success --date [DATE]
     ```

## Output Format

```markdown
# 📊 AI 漫画客户获取日报 — [DATE]

## 📈 今日指标
| 指标 | 数值 | 较昨日 |
|------|------|--------|
| 新发现线索 | 15 | +3 |
| 已完成研报 | 12 | - |
| 热门线索 | 4 | +2 |
| 已联系 | 6 | - |
| 收到回复 | 2 | 回复率 33% |

## 🔥 热门线索（今日跟进）

### 1. XX AI 漫画工作室 ⭐⭐⭐⭐⭐
- 痛点：产能瓶颈（3 集/天 → 目标 10 集/天）
- 决策人：张三（CEO）— LinkedIn 私信已读，未回复
- 建议：今天下午电话跟进
- 联系历史：
  - 07/20 LinkedIn 私信 ✓
  - 07/21 邮件 ✓（未打开）
  - **07/22 → 电话跟进** ⬅️

### 2. YY AI 视频公司 ⭐⭐⭐⭐
- 痛点：后期制作人工量过大
- 决策人：李四（技术负责人）
- 建议：今日发送案例对比

## 💡 温暖线索（本周培育）
| 公司 | 触点 | 下次联系 |
|------|------|----------|
| ZZ 动画 | 已加微信 | 07/25 发送白皮书 |
| WW 工作室 | Bilibili 关注中 | 新内容发布后 |

## 📋 行动项
- [ ] 10:00 致电 XX 公司张三
- [ ] 14:00 向 YY 公司发送案例对比
- [ ] 16:00 第二轮搜索（更换关键词）
- [ ] 17:00 汇总本周热门线索给销售总监
```

## Verification

- 报告已成功生成且包含所有五个部分（指标、热门线索、温暖线索、行动项、联系历史）。
- 指标数值与 CordysCRM 查询结果一致。
- 至少有一个推送渠道返回 HTTP 2xx 成功状态。
- 报告已成功存档至 CordysCRM。
- Hermes 日志中记录了 `skill: daily-report, status: success`。
- 若任一渠道推送失败，记录警告日志但不中断流程，继续推送其余渠道。
- 若所有渠道均失败，标记 `status: failed` 并触发告警。

验证命令：
```
hermes log last --skill daily-report
hermes gateway call cordyscrm-report-archive --check --date [DATE]
```

## Example

以下是一次完整的执行示例（2026-07-23 上午 9:00 自动触发）：

```bash
# 1. Cron 触发
# hermes-cron 按 "0 9 * * *" 调度自动启动

# 2. 前置检查
$ hermes cron status
Cron service: running
Next daily-report fire: 2026-07-23 09:00 CST

$ hermes gateway status --channels feishu,email
feishu: connected (group: ai-comic-sales)
email: connected (smtp configured)

$ hermes gateway health cordyscrm
cordyscrm: healthy (latency 45ms)

# 3. 收集数据
$ hermes gateway call cordyscrm-lead-query --metrics new,contacted,replied --since "24h"
{"new": 15, "contacted": 6, "replied": 2, "hot": 4, "researched": 12}

$ hermes memory list --since "24h" --tags pipeline,sales
[{"company": "XX AI Comic Studio", "status": "hot", "decision_maker": "Zhang San", ...}, ...]

$ hermes skill run lead-finder --summary --since "today"
New leads today: 15 (keyword: AI comic studio, AI animation company)

$ hermes skill run company-researcher --summary --since "today"
Researched today: 12 companies

$ hermes skill run outreach-generator --summary --since "today"
Messages sent: 6 (LinkedIn: 3, Email: 2, WeChat: 1)

# 4. 推送报告
$ hermes gateway send feishu --group "ai-comic-sales" --content report.md
Feishu message sent: msg_abc123

$ hermes gateway send email --to "director@company.com" --subject "AI 漫画日报 2026-07-23" --body report.md
Email sent: eml_def456

# 5. 存档
$ hermes gateway call cordyscrm-report-archive --type daily --file report.md
Report archived: arc_20260723_daily

$ hermes log --skill daily-report --status success --date 2026-07-23
Logged: daily-report | 2026-07-23 | success | channels: feishu, email
```

### Cron 配置参考

```yaml
cron:
  daily_report:
    schedule: "0 9 * * *"
    skill: daily-report
    platforms: [feishu, email]
    timezone: Asia/Shanghai
    weekday_only: true
```

### 常见问题处理

**飞书推送失败：**
```bash
# 检查飞书 token 是否过期
hermes gateway refresh feishu
# 重新推送
hermes gateway send feishu --group "ai-comic-sales" --content report.md
```

**CordysCRM 数据为空：**
```bash
# 确认管道是否有今天的数据
hermes gateway call cordyscrm-lead-query --metrics all --since "24h"
# 若无数据，在报告中标注 "今日暂无新数据" 并正常推送
```

**非工作日静默跳过：**
```bash
# cron 配置中 weekday_only: true 时自动跳过周末
# 手动检查当天是否为工作日
date +%u  # 1=周一, 5=周五, 6/7=周末
```
