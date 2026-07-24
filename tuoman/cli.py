"""
拓漫 CLI 入口 — 给 pip install -e . 注册的 tuoman 命令
"""

import argparse
import logging
import sys
from pathlib import Path

# 确保能 import
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
    parser = argparse.ArgumentParser(description="拓漫 TouMan — AI漫剧获客管线")
    parser.add_argument("--headful", action="store_true", help="非无头模式（调试用）")
    parser.add_argument("--model", default="gpt-4o", help="LLM模型")
    args = parser.parse_args()

    setup_logging()
    logger = logging.getLogger("tuoman")
    logger.info("拓漫 TouMan 启动 (model=%s)", args.model)

    runner = PipelineRunner(headless=not args.headful, model=args.model)
    result = runner.run()

    report_path = Path.cwd() / "reports" / result["date"] / "pipeline_report.md"
    print(f"\n✅ 完成! 报告: {report_path}")


if __name__ == "__main__":
    main()
