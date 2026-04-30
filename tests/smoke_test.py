from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from analytics_agent.agent import answer_question  # noqa: E402
from analytics_agent.app import app  # noqa: E402
from analytics_agent.evaluation import run_eval  # noqa: E402
from analytics_agent.sql_safety import validate_readonly_sql  # noqa: E402


def main() -> None:
    for sql in ["DROP TABLE users", "DELETE FROM users", "UPDATE users SET x=1", "INSERT INTO users VALUES (1)", "ALTER TABLE users ADD x TEXT"]:
        try:
            validate_readonly_sql(sql)
            raise AssertionError(f"Unsafe SQL allowed: {sql}")
        except ValueError:
            pass

    answer = answer_question("哪个渠道毛利ROAS最高？")
    assert answer.source_id == "benefit_ltv"
    assert answer.sql.lower().strip().startswith("with")
    assert answer.success
    assert answer.rows

    result = run_eval()
    assert result["safety_reject_rate"] == 1.0
    assert result["source_accuracy"] >= 0.85
    assert result["sql_executable_rate"] >= 0.85

    client = TestClient(app)
    assert client.get("/").status_code == 200
    resp = client.post("/api/ask", json={"question": "搜索排序 treatment 对长尾 query 有提升吗？"})
    assert resp.status_code == 200
    assert resp.json()["source_id"] == "search_rank"
    print("smoke_test passed")


if __name__ == "__main__":
    main()
