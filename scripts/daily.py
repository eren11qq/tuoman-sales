#!/usr/bin/env python3
"""
拓漫 TouMan — 每日获客管线入口

用法:
    python scripts/daily.py              # 完整管线
    python scripts/daily.py --headful    # 非无头模式(调试用)
    python scripts/daily.py --model gpt-4o-mini  # 指定模型
"""

import argparse
import logging
import sys
from pathlib import Path

# 确保能 import tuoman
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from tuoman.pipeline.runner import PipelineRunner


def setup_logging():
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "pipeline.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main():
    parser = argparse.ArgumentParser(description="拓漫TouMan 每日获客管线")
    parser.add_argument(
        "--headful",
        action="store_true",
        help="非无头模式（可以看到浏览器操作，用于调试）",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="LLM模型 (默认: gpt-4o)",
    )
    parser.add_argument(
        "--stage",
        choices=["finder", "analyzer", "outreach", "reporter"],
        help="只运行单个stage（跳过其他）",
    )
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger("tuoman")
    logger.info("拓漫 TouMan v0.20.0 启动")

    runner = PipelineRunner(
        headless=not args.headful,
        model=args.model,
    )

    # 如果是单stage模式，直接调对应方法
    if args.stage:
        logger.info("单stage模式: %s", args.stage)
        # TODO: 支持单stage执行
        logger.warning("单stage模式暂未实现，运行完整管线")
    else:
        result = runner.run()
        print(f"\n✅ 管线完成! 报告路径: reports/{result['date']}/pipeline_report.md")


if __name__ == "__main__":
    main()
