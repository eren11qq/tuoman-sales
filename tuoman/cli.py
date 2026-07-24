"""
拓漫 TouMan — AI漫剧行业智能获客助手

无参数启动进入交互式对话界面，像 Claude 一样聊天。
子命令保留用于脚本化操作。

用法:
    tuoman                       # 交互式对话
    tuoman run                   # 运行完整管线
    tuoman run --stage finder    # 只搜索线索
    tuoman list hot              # 查看 HOT 线索
    tuoman stats                 # 统计
    tuoman search 关键词         # 搜索
    tuoman init                  # 初始化
"""

import argparse
import logging
import sys
from pathlib import Path

# Windows GBK 兼容
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from tuoman.pipeline.runner import PipelineRunner
from tuoman.models.lead import LeadDatabase
from tuoman.llm.client import LLMClient

logger = logging.getLogger("tuoman")


def setup_logging(verbose: bool = False):
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "tuoman.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def cmd_run(args):
    """运行管线"""
    runner = PipelineRunner(
        headless=not args.headful,
        model=args.model,
        platforms=args.platforms.split(",") if args.platforms else None,
    )

    if args.stage:
        result = runner.run_stage(args.stage)
        status = "✅" if result["status"] == "ok" else "❌"
        print(f"\n{status} Stage '{args.stage}': {result['status']}")
    else:
        result = runner.run()
        print(f"\n✅ 管线完成! 报告: reports/{result['date']}/pipeline_report.md")


def cmd_list(args):
    """查看线索"""
    db = LeadDatabase()
    if args.type == "hot":
        rows = db.list_hot(args.limit)
        if not rows:
            print("暂无 HOT 线索")
            return
        print(f"\n{'=' * 60}")
        print(f"HOT 线索 ({len(rows)} 条)")
        print(f"{'=' * 60}")
        for r in rows:
            print(f"  [{r['id']}] {r['company_name'] or r['author_name']} | "
                  f"ICP:{r.get('icp_score', 0):.0f}% | "
                  f"平台:{r['platform']} | "
                  f"状态:{r.get('outreach_status', '待触达')}")
            if r.get('author_url'):
                print(f"       {r['author_url']}")

    elif args.type == "pending":
        rows = db.list_pending_outreach(args.limit)
        if not rows:
            print("暂无待触达线索")
            return
        print(f"\n{'=' * 60}")
        print(f"待触达线索 ({len(rows)} 条)")
        print(f"{'=' * 60}")
        for r in rows:
            print(f"  [{r['id']}] {r['company_name'] or r['author_name']} | "
                  f"{r['priority']} | {r['platform']}")

    else:  # all
        rows = db.export_json()
        print(f"\n总计 {len(rows)} 条线索:")
        for r in rows[:args.limit]:
            status_mark = {
                "": "○", "draft": "✎", "sent": "✉", "replied": "✓"
            }.get(r.get("outreach_status", ""), "○")
            print(f"  {status_mark} [{r['id']}] {r['company_name'] or r['author_name']} | "
                  f"{r['priority']:5s} | {r['platform']}")


def cmd_stats(args):
    """查看统计"""
    db = LeadDatabase()
    s = db.get_stats()
    print(f"""
{'=' * 40}
  拓漫 TouMan — 线索数据库统计
{'=' * 40}

  总计:        {s['total']} 条
  HOT:         {s['hot']} 条
  WARM:        {s['warm']} 条
  COLD:        {s['cold']} 条

  触达状态:
    草稿:      {s['outreach_draft']} 条
    已发送:    {s['outreach_sent']} 条
    已回复:    {s['outreach_replied']} 条

  今日新增:    {s['new_today']} 条
""")


def cmd_search(args):
    """搜索线索"""
    db = LeadDatabase()
    rows = db.search(args.query)
    if not rows:
        print(f"未找到包含 '{args.query}' 的线索")
        return
    print(f"\n找到 {len(rows)} 条线索:")
    for r in rows:
        print(f"  [{r['id']}] {r['company_name'] or r['author_name']} | {r['platform']} | {r['priority']}")


def cmd_init(args):
    """初始化数据库"""
    db_path = Path(__file__).parent.parent / "data" / "leads.db"
    db = LeadDatabase(db_path)
    # 验证数据库是否正常
    stats = db.get_stats()
    print(f"✅ 数据库初始化完成: {db_path}")
    print(f"   当前 {stats['total']} 条线索")


# ── 交互式对话 ─────────────────────────────────────


WELCOME = """
╔══════════════════════════════════════════════╗
║       拓漫 TouMan — AI漫剧获客助手          ║
╚══════════════════════════════════════════════╝

你可以这样跟我聊:
  • "帮我找漫剧公司"     — 运行线索发现
  • "查看今天的结果"     — 查看管线报告
  • "有哪些 HOT 线索"    — 查看高优先级线索
  • "搜索 灵境AI"        — 搜索特定公司
  • "统计"               — 数据库统计
  • "help"               — 帮助
  • "exit" 或 Ctrl+C     — 退出

"""  # noqa: W291

REPL_PROMPT = "\n╭─ 拓漫 ──────────────────────────────────────────────╮\n│  "


def cmd_chat(args=None):
    """交互式对话模式"""
    print(WELCOME)
    db = LeadDatabase()

    try:
        llm = LLMClient(model="gpt-4o")
    except ValueError as e:
        llm = None
        print(f"  ⚠ {e}")
        print("  仍可使用 list/stats/search 等命令\n")

    while True:
        try:
            user_input = input("\n  ❯ ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  再见！")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        # ── 退出 ──
        if cmd in ("exit", "quit", "退出", "再见"):
            print("  再见！")
            break

        # ── 帮助 ──
        if cmd in ("help", "?", "帮助", "h"):
            print("""  可用命令:
    run             运行完整获客管线
    find            只运行线索发现
    hot             查看 HOT 线索
    stats           查看统计
    search <关键词>  搜索线索
    help            显示帮助
    exit            退出
  """)
            continue

        # ── run ──
        if cmd in ("run", "运行", "全流程", "跑一遍"):
            if not llm:
                print("  需要配置 API Key 才能运行")
                continue
            print("  正在运行获客管线（B站+小红书→分析→触达→日报）...")
            runner = PipelineRunner(model="gpt-4o")
            result = runner.run()
            s = result.get("stats", {})
            print(f"  ✅ 完成! HOT={s.get('hot', 0)} WARM={s.get('warm', 0)} 总计={s.get('total', 0)}")
            continue

        # ── find ──
        if cmd in ("find", "finder", "搜索", "找客户", "找线索", "发现"):
            if not llm:
                print("  需要配置 API Key 才能运行")
                continue
            print("  正在搜索各平台 AI漫剧线索...")
            runner = PipelineRunner(model="gpt-4o")
            result = runner.run_stage("finder")
            rc = result.get("count", 0)
            print(f"  ✅ 发现 {rc} 条新线索")
            continue

        # ── hot ──
        if cmd in ("hot", "h", "热点", "线索", "leads"):
            rows = db.list_hot(10)
            if not rows:
                print("  暂无 HOT 线索")
                continue
            print(f"\n  HOT 线索 ({len(rows)} 条):")
            for r in rows:
                name = r.get("company_name") or r.get("author_name", "?")
                icp = r.get("icp_score", 0)
                plat = r.get("platform", "?")
                status = r.get("outreach_status", "") or "待触达"
                print(f"    🔥 {name} | ICP:{icp:.0f}% | {plat} | {status}")
            continue

        # ── stats ──
        if cmd in ("stats", "统计", "状态"):
            s = db.get_stats()
            print(f"""
    总计:        {s['total']} 条
    HOT:         {s['hot']} 条
    WARM:        {s['warm']} 条
    COLD:        {s['cold']} 条
    今日新增:    {s['new_today']} 条
    已触达:      {s['outreach_sent']} 条
    已回复:      {s['outreach_replied']} 条
    """)
            continue

        # ── search ──
        if cmd.startswith("search ") or cmd.startswith("搜索 "):
            keyword = cmd.split(" ", 1)[1] if " " in cmd else ""
            if not keyword:
                print("  用法: search <关键词>")
                continue
            rows = db.search(keyword)
            if not rows:
                print(f"  未找到 '{keyword}' 相关线索")
                continue
            print(f"  找到 {len(rows)} 条:")
            for r in rows[:10]:
                name = r.get("company_name") or r.get("author_name", "?")
                print(f"    [{r['id']}] {name} | {r['platform']} | {r.get('priority', '?')}")
            continue

        # ── 其他 → LLM 理解 ──
        if llm:
            print("  思考中...")
            system = "你是拓漫TouMan——AI漫剧行业获客助手。用户说了句话，判断他想做什么。只输出以下命令之一，不要解释：run, find, hot, stats, search:<关键词>, help, unknown"
            try:
                resp = llm.chat(system, f"用户说: {user_input}")
                resp = resp.strip().lower()
                # 模拟 dispatch
                if resp == "run":
                    print("  好的，运行全流程管线")
                    runner = PipelineRunner(model="gpt-4o")
                    result = runner.run()
                    s = result.get("stats", {})
                    print(f"  ✅ 完成! HOT={s.get('hot', 0)} WARM={s.get('warm', 0)} 总计={s.get('total', 0)}")
                elif resp == "find":
                    print("  好的，搜索新线索")
                    runner = PipelineRunner(model="gpt-4o")
                    result = runner.run_stage("finder")
                    print(f"  ✅ 发现 {result.get('count', 0)} 条新线索")
                elif resp == "hot":
                    rows = db.list_hot(10)
                    if rows:
                        for r in rows:
                            name = r.get("company_name") or r.get("author_name", "?")
                            print(f"    🔥 {name}")
                    else:
                        print("  暂无 HOT 线索")
                elif resp.startswith("search:"):
                    kw = resp.split(":", 1)[1].strip()
                    rows = db.search(kw)
                    if rows:
                        for r in rows[:5]:
                            print(f"    {r.get('company_name', '?')} | {r['platform']}")
                    else:
                        print(f"  未找到 '{kw}'")
                else:
                    print("  不太明白，试试: 找客户、统计、hot、help")
            except Exception as e:
                print(f"  ⚠ {e}")
        else:
            print("  试试: run, hot, stats, search <关键词>, help")


def main():
    parser = argparse.ArgumentParser(
        description="拓漫 TouMan — AI漫剧行业智能获客助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="详细日志")

    sub = parser.add_subparsers(dest="command", help="可用命令")

    # run
    p_run = sub.add_parser("run", help="运行获客管线")
    p_run.add_argument("--stage", choices=["finder", "analyzer", "outreach", "reporter"],
                       help="只运行单个 stage")
    p_run.add_argument("--headful", action="store_true", help="有头模式（调试用）")
    p_run.add_argument("--model", default="gpt-4o", help="LLM 模型 (默认: gpt-4o)")
    p_run.add_argument("--platforms", help="平台列表，逗号分隔 (bilibili,xiaohongshu)")

    # list
    p_list = sub.add_parser("list", help="查看线索")
    p_list.add_argument("type", nargs="?", default="hot",
                        choices=["hot", "pending", "all"],
                        help="线索类型 (默认: hot)")
    p_list.add_argument("--limit", "-n", type=int, default=20, help="数量限制")

    # stats
    sub.add_parser("stats", help="查看数据库统计")

    # search
    p_search = sub.add_parser("search", help="搜索线索")
    p_search.add_argument("query", help="搜索关键词")

    # init
    sub.add_parser("init", help="初始化数据库")

    args = parser.parse_args()

    setup_logging(verbose=args.verbose if hasattr(args, 'verbose') else False)

    # 无子命令 → 交互式对话
    if not args.command:
        cmd_chat(args)
        return

    if args.command == "run":
        cmd_run(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "init":
        cmd_init(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
