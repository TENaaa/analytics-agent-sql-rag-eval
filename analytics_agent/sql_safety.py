from __future__ import annotations

import re


FORBIDDEN = {
    "drop",
    "delete",
    "update",
    "insert",
    "alter",
    "create",
    "replace",
    "attach",
    "detach",
    "pragma",
    "vacuum",
}


def validate_readonly_sql(sql: str) -> None:
    cleaned = _strip_comments(sql).strip().lower()
    if not cleaned.startswith("select") and not cleaned.startswith("with"):
        raise ValueError("Only SELECT/WITH statements are allowed.")
    tokens = set(re.findall(r"[a-z_]+", cleaned))
    blocked = sorted(tokens & FORBIDDEN)
    if blocked:
        raise ValueError(f"Forbidden SQL token: {', '.join(blocked)}")
    statements = [part.strip() for part in cleaned.split(";") if part.strip()]
    if len(statements) > 1:
        raise ValueError("Multiple SQL statements are not allowed.")


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"--.*?$", "", sql, flags=re.MULTILINE)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql
