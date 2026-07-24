#!/usr/bin/env python3
"""
拓漫 TouMan — 每日获客管线入口（兼容层，委托给 tuoman CLI）

用法:
    python scripts/daily.py              # 完整管线
    python scripts/daily.py --headful    # 调试
    python scripts/daily.py --stage finder  # 单 stage
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from tuoman.cli import main

if __name__ == "__main__":
    # 把脚本参数转发给 CLI
    sys.argv[0] = "tuoman"
    # 默认加 run 子命令（和 tuoman run 一样）
    if len(sys.argv) == 1 or sys.argv[1].startswith("-"):
        sys.argv.insert(1, "run")
    main()
