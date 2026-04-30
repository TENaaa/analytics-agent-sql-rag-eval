from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import uvicorn

from .agent import answer_question
from .config import REPORT_DIR
from .evaluation import run_eval


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="指标字典驱动的数据分析 Agent 与评测框架")
    sub = parser.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask")
    ask.add_argument("question")
    web = sub.add_parser("run-web")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8008)
    sub.add_parser("eval")
    export = sub.add_parser("export-report")
    export.add_argument("--out", type=Path, default=REPORT_DIR / "agent_eval_report.md")
    args = parser.parse_args(argv)
    if args.command == "ask":
        answer = answer_question(args.question)
        print(json.dumps(answer.__dict__, ensure_ascii=False, indent=2))
    elif args.command == "run-web":
        uvicorn.run("analytics_agent.app:app", host=args.host, port=args.port, reload=False)
    elif args.command == "eval":
        print(json.dumps(run_eval(), ensure_ascii=False, indent=2))
    elif args.command == "export-report":
        result = run_eval(report_path=args.out)
        print(f"Report exported: {args.out} ({result['success_rate']:.1%} success)")


if __name__ == "__main__":
    main()
