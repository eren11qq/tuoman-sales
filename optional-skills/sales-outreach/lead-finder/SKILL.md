---
name: lead-finder
description: >
  在多平台（B站、小红书、抖音、YouTube、GitHub）搜索和筛选企业级 AI 漫画/动画/视频制作公司，输出资格评分排名的潜在客户列表。
platforms: [linux, macos, windows]
version: 1.0.0
author: AI Comic Sales Agent
license: MIT
category: sales-outreach
metadata:
  hermes:
    tags: [sales, customer-acquisition, ai-comic, china, lead-finder]
---

# 潜在客户发现器 (Lead Finder)

## When to Use

- 需要在中国社交媒体和全球技术平台上发现新的 AI 漫画、AI 动画或 AI 视频制作企业客户时。
- 销售拓展 (sales outreach) 流程的第一步：构建潜在客户列表 (lead list)。
- 需要区分企业客户与个人创作者，只关注有付费能力的团队。
- 定期扫描市场，发现新成立的 AI 内容制作公司或获得融资的团队。

触发关键词：找客户、发现潜在客户、AI 漫画公司、AI 动画团队、lead generation、客户挖掘。

## When NOT to Use

- 目标客户不是 AI 内容制作领域（如传统影视制作、非 AI 驱动的动画公司）。
- 只需要个人创作者或 KOL 信息，而非企业客户。
- 已经拥有完整的、经过验证的潜在客户列表，无需增量发现。
- 需要的是客户联系人邮箱/电话等深度信息（那是后续 contact-enrichment 技能的职责）。

## Tools Required

### MCP 工具
- **MediaCrawler MCP** — 搜索 小红书、抖音、B站、快手、微博、知乎
  - `mediacrawler:search_xiaohongshu` — 小红书搜索
  - `mediacrawler:search_bilibili` — B站搜索
  - `mediacrawler:search_douyin` — 抖音搜索
  - `mediacrawler:search_kuaishou` — 快手搜索
  - `mediacrawler:search_weibo` — 微博搜索

- **douyin-mcp-node** — 抖音专项搜索，作为 MediaCrawler 的补充

### 外部 API / CLI 工具
- **Jina Reader** (`r.jina.ai`) — 将任意 URL 抓取为 Markdown，用于读取公司官网、招聘页面、36氪报道等
  - 用法：`curl -s "https://r.jina.ai/https://example.com" -H "Accept: text/markdown"`
- **Exa Search** — Web 搜索，覆盖 YouTube、GitHub、ProductHunt 等海外平台
  - 用法：`exa:search` MCP 工具

## Procedure

### 第一步：多平台并行搜索

在每个平台上使用对应的搜索关键词发起并行搜索。至少覆盖 3 个平台。

**国内平台搜索关键词：**
- B站 (MediaCrawler MCP): `mediacrawler:search_bilibili` 依次使用关键词：
  - `"AI 漫画"`、`"AI 动画"`、`"AI 视频制作"`、`"AI 漫剧"`、`"动态漫"`
- 小红书 (MediaCrawler MCP): `mediacrawler:search_xiaohongshu` 依次使用关键词：
  - `"AI 漫画工作室"`、`"AI 视频团队"`、`"AI 动画制作"`
- 抖音 (MediaCrawler MCP + douyin-mcp-node): 依次使用关键词：
  - `"AI 生成漫画"`、`"AI 动画制作"`、`"AI 漫剧"`

**海外平台搜索关键词：**
- YouTube (Exa Search): `exa:search` 使用关键词：
  - `"AI comic creation"`、`"AI animation studio"`、`"AI manga"`
- GitHub (Exa Search): `exa:search` 使用关键词：
  - `AI 漫画生成`、`AI comic generation`、`AI animation pipeline` — 查找 repo 背后的公司

**融资/行业新闻：**
- 36氪 / IT桔子 (Jina Reader): 抓取 AI 内容赛道融资新闻
  - `curl -s "https://r.jina.ai/https://36kr.com/search/articles/AI漫画" -H "Accept: text/markdown"`

### 第二步：收集原始结果并去重

将各平台返回的创作者/账号/公司信息汇总到一个中间列表。

去重规则：
1. 同一个 URL 出现多次 → 合并为一条，记录所有来源平台。
2. 同一公司名称出现在不同平台 → 合并，`found_at` 字段列出所有平台。

### 第三步：企业 vs 个人判定

对每条记录进行企业信号和个人信号的评估。

**企业信号（每一项 +15 至 +25 分）：**
- 有独立官网（+25）
- 在招聘平台上发布招聘信息（+25）
- 有公司注册信息可见（+20）
- 多人员工账号可见（+20）
- 团队规模估算超过 5 人（+20）
- 有办公室地址（+15）
- 使用企业级/付费工具（+15）

**个人信号（每一项 -15 至 -30 分）：**
- 单一人员账号，无团队信息（-30）
- 无公司介绍页面（-25）
- 联系方式仅为个人邮箱（-20）
- 无招聘信息（-20）
- 仅使用免费/开源工具（-15）
- 粉丝数不足 1 万且内容产出不稳定（-15）

**判定逻辑：**
- `qualification_score` 起始为 50 分。
- 累加所有企业信号分数，减去所有个人信号分数。
- 最终得分 >= 70 分 → `is_enterprise = true`
- 最终得分 < 70 分 → `is_enterprise = false`
- 对所有 `is_enterprise = false` 的记录自动标记为 `COLD` 优先级。

### 第四步：深度信息补充（仅针对企业候选）

对 `qualification_score >= 70` 的候选，使用 Jina Reader 抓取其官网或 B站/小红书主页，补充：
- `description` — 业务描述
- `team_size_estimate` — 团队规模推测
- `content_output` — 内容产出频率
- `tech_stack` — 推测的技术栈（从内容中推断使用了哪些 AI 工具）
- `decision_makers` — 如果页面提及创始人/CEO/制作人姓名

### 第五步：排序输出

按 `qualification_score` 降序排列，输出 Top 20。

## Output Format

每条潜在客户输出为如下 JSON 对象，整体输出为 JSON 数组：

```json
[
  {
    "company_name": "XX AI 漫剧工作室",
    "found_at": ["bilibili", "xiaohongshu"],
    "url": "https://space.bilibili.com/xxx",
    "description": "专注 AI 动态漫制作，日更 3 集，覆盖玄幻、都市题材",
    "team_size_estimate": "20-50人",
    "content_output": "日均 3 条 AI 漫剧",
    "followers": "50万",
    "is_enterprise": true,
    "enterprise_signals": ["有招聘信息", "官网有公司介绍", "多人员工账号", "企业认证"],
    "individual_signals": [],
    "decision_makers": [],
    "tech_stack": ["Stable Diffusion", "ComfyUI", "AnimateDiff"],
    "qualification_score": 85,
    "priority": "HOT"
  }
]
```

## Verification

技能执行完成后，验证以下条件：

1. **覆盖率** — 至少搜索了 3 个不同平台。
2. **去重确认** — 输出列表中没有重复的公司名称或 URL。
3. **企业判定准确** — 抽查 2-3 条 `is_enterprise = false` 的记录，确认确实为个人创作者。
4. **分数合理性** — `qualification_score` 在 0-100 范围内，且企业信号得分与 `enterprise_signals` 数组一致。
5. **输出格式** — 每个对象包含所有必填字段，JSON 合法可解析。
6. **数量** — 输出为 Top 20（如果符合条件的不足 20 条，则输出全部）。

## Example

以下是一次典型的执行过程：

```
用户: 帮我找一些国内做 AI 漫画的企业客户

Agent 执行:

1. 并行搜索三个平台:
   - mediacrawler:search_bilibili(keyword="AI 漫剧")
     → 返回: 星海AI漫剧 (50万粉), 次元引擎 (30万粉), 幻境工作室 (8万粉), ...

   - mediacrawler:search_xiaohongshu(keyword="AI 漫画工作室")
     → 返回: 轻舟AI漫画 (10万粉), 像素漫工场 (5万粉), ...

   - mediacrawler:search_douyin(keyword="AI 动画制作")
     → 返回: 星海AI漫剧 (重复), 新视界动画 (20万粉), ...

2. 去重: 星海AI漫剧 出现在 B站和抖音 → 合并

3. 对每个候选进行企业/个人判定:
   星海AI漫剧:
     + 有官网 company.site (+25)
     + 招聘平台上招 AI 画师 (+25)
     + 团队 30+ 人 (+20)
     + 使用 ComfyUI 企业版 (+15)
     得分: 50 + 85 = 135 → clip 到 100
     is_enterprise: true, priority: HOT

   幻境工作室 (8万粉):
     无官网 (-25)
     无招聘 (-20)
     单人运营 (-30)
     得分: 50 - 75 = -25 → clip 到 0
     is_enterprise: false, priority: COLD

4. 对 HOT 候选用 Jina Reader 补充信息:
   curl -s "https://r.jina.ai/https://company.site" -H "Accept: text/markdown"
   → 补充 team_size, tech_stack, description

5. 排序输出 Top 20

输出 (截取前两条):
[
  {
    "company_name": "星海AI漫剧",
    "found_at": ["bilibili", "douyin"],
    "url": "https://space.bilibili.com/123456",
    "description": "国内领先的 AI 动态漫制作公司，拥有自研 AI 管线，月产 100+ 集",
    "team_size_estimate": "30-50人",
    "content_output": "日均 4 条 AI 漫剧",
    "followers": "50万(B站) + 35万(抖音)",
    "is_enterprise": true,
    "enterprise_signals": ["官网", "招聘信息", "多人员工", "企业版工具"],
    "individual_signals": [],
    "decision_makers": [],
    "tech_stack": ["Stable Diffusion", "ComfyUI Enterprise", "AnimateDiff", "自研管线"],
    "qualification_score": 100,
    "priority": "HOT"
  },
  {
    "company_name": "幻境工作室",
    "found_at": ["bilibili"],
    "url": "https://space.bilibili.com/789012",
    "description": "个人 AI 漫剧创作者",
    "team_size_estimate": "1人",
    "content_output": "周更 2 条",
    "followers": "8万",
    "is_enterprise": false,
    "enterprise_signals": [],
    "individual_signals": ["单人运营", "无官网", "无招聘"],
    "decision_makers": [],
    "tech_stack": ["Stable Diffusion WebUI"],
    "qualification_score": 0,
    "priority": "COLD"
  }
]
```
