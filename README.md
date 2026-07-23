<p align="center">
  <img src="assets/banner.png" alt="拓漫 TouMan" width="100%">
</p>

# 拓漫 TouMan ☤
<p align="center">
  AI漫剧行业智能获客助手
</p>
<p align="center">
  <a href="https://github.com/eren11qq/hermes-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/Lang-中文-red?style=for-the-badge" alt="中文"></a>
</p>

**拓漫 TouMan — AI漫剧行业智能获客Agent。** 基于 Hermes Agent 深度定制，专门为 AI 漫剧创作者和工作室设计的自动化获客工具。自动搜索创作者、分类线索、每日输出报告，帮助你把精力放在创作上。

---

## 核心功能

| 功能 | 说明 |
|------|------|
| **线索发现** | 自动搜索 AI 漫剧创作者，覆盖小红书、B站、抖音等平台 |
| **企业/个人分类** | 自动区分企业客户和个人创作者，标记优先级 |
| **每日报告** | 每天自动生成线索报告，按优先级排列 |
| **定时任务** | 配置 Cron 后每天自动运行，无需手动操作 |
| **多模型支持** | 支持 DeepSeek、OpenAI、OpenRouter 等多种模型 |

## 快速开始

### Windows（原生 PowerShell）

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

### Linux / macOS / WSL2

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### 安装后

```bash
hermes              # 启动交互式对话
hermes model        # 选择 AI 模型
```

---

## 内置 Skill

| Skill | 说明 |
|-------|------|
| **lead-finder** | 线索发现 — 自动搜索 AI 漫剧创作者 |
| **company-researcher** | 企业调研 — 深入分析目标客户 |
| **enterprise-filter** | 企业筛选 — 区分个人/企业客户 |
| **outreach-generator** | 触达文案生成 — 个性化沟通 |
| **sales-outreach** | 销售触达 — 自动化跟进 |
| **daily-report** | 每日报告 — 汇总线索和进度 |

---

## 技术栈

- **底层引擎**: Hermes Agent（MIT 协议）
- **语言**: Python
- **模型支持**: OpenAI, DeepSeek, OpenRouter, Anthropic 等
- **消息平台**: Telegram, Discord, Slack, 微信（社区版）
- **调度**: 内置 Cron 定时任务

---

## License

MIT — see [LICENSE](LICENSE).

Based on [Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research.
