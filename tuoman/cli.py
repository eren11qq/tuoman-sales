"""
拓漫 CLI — 完整命令行工具

用法:
    tuoman run                   # 运行完整管线
    tuoman run --stage finder    # 只运行特定 stage
    tuoman run --no-browser      # 无头模式（默认）
    tuoman list hot              # 查看 HOT 线索
    tuoman list all              # 查看所有线索
    tuoman stats                 # 查看数据库统计
    tuoman search 关键词         # 搜索线索
    tuoman init                  # 初始化数据库
"""

import argparse
import logging
import sys
from pathlib import Path

# Windows GBK 兼容: 设置 stdout/stderr 为 UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 确保能 import tuoman
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from tuoman.pipeline.runner import PipelineRunner
from tuoman.models.lead import LeadDatabase

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


def main():
    parser = argparse.ArgumentParser(
        description="拓漫 TouMan — AI漫剧行业智能获客管线",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  tuoman run                          # 运行完整管线
  tuoman run --stage finder           # 只搜索线索
  tuoman run --headful                # 有头模式（看浏览器操作）
  tuoman list hot                     # 查看 HOT 线索
  tuoman stats                        # 查看统计
  tuoman search 工作室                # 搜索线索
  tuoman init                         # 初始化数据库
        """,
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
