from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .agent import answer_question
from .config import EVAL_PATH, REPORT_DIR
from .sql_safety import validate_readonly_sql


def run_eval(eval_path: Path = EVAL_PATH, report_path: Optional[Path] = None) -> dict[str, object]:
    questions = json.loads(eval_path.read_text(encoding="utf-8"))
    rows = []
    for item in questions:
        answer = answer_question(item["question"])
        source_ok = answer.source_id == item["expected_source"]
        sql_ok = answer.success and answer.sql.strip()
        context_ok = any(ctx["source_id"] == item["expected_source"] for ctx in answer.retrieved_context)
        rows.append(
            {
                "id": item["id"],
                "question": item["question"],
                "source_ok": source_ok,
                "sql_ok": bool(sql_ok),
                "context_ok": context_ok,
                "success": answer.success,
                "source_id": answer.source_id,
                "error": answer.error,
            }
        )
    safety_cases = ["DROP TABLE users", "DELETE FROM users", "UPDATE users SET x=1", "INSERT INTO users VALUES (1)", "ALTER TABLE users ADD x TEXT"]
    safety_pass = 0
    for sql in safety_cases:
        try:
            validate_readonly_sql(sql)
        except ValueError:
            safety_pass += 1
    result = {
        "total_questions": len(rows),
        "success_rate": sum(row["success"] for row in rows) / max(1, len(rows)),
        "source_accuracy": sum(row["source_ok"] for row in rows) / max(1, len(rows)),
        "context_hit_rate": sum(row["context_ok"] for row in rows) / max(1, len(rows)),
        "sql_executable_rate": sum(row["sql_ok"] for row in rows) / max(1, len(rows)),
        "safety_reject_rate": safety_pass / len(safety_cases),
        "rows": rows,
    }
    write_eval_report(result, report_path or REPORT_DIR / "agent_eval_report.md")
    return result


def write_eval_report(result: dict[str, object], report_path: Path) -> Path:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 数据分析 Agent 评测报告",
        "",
        f"- 问题数：{result['total_questions']}",
        f"- 成功率：{result['success_rate']:.1%}",
        f"- 数据源路由准确率：{result['source_accuracy']:.1%}",
        f"- 指标口径检索命中率：{result['context_hit_rate']:.1%}",
        f"- SQL 可执行率：{result['sql_executable_rate']:.1%}",
        f"- 危险 SQL 拒绝率：{result['safety_reject_rate']:.1%}",
        "",
        "| id | source | success | error |",
        "| --- | --- | --- | --- |",
    ]
    for row in result["rows"]:
        lines.append(f"| {row['id']} | {row['source_id']} | {row['success']} | {row['error'] or ''} |")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
