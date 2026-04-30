from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from .config import DEFAULT_SOURCES


@dataclass(frozen=True)
class DataSource:
    source_id: str
    title: str
    db_path: Path
    description: str

    @property
    def available(self) -> bool:
        return self.db_path.exists()


def load_sources() -> dict[str, DataSource]:
    return {
        key: DataSource(key, value["title"], Path(value["db_path"]), value["description"])
        for key, value in DEFAULT_SOURCES.items()
    }


def inspect_schema(source: DataSource) -> dict[str, list[str]]:
    if not source.available:
        return {}
    with sqlite3.connect(source.db_path) as conn:
        tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {table: [col[1] for col in conn.execute(f"PRAGMA table_info({table})")] for table in tables}


def source_status() -> list[dict[str, object]]:
    rows = []
    for source in load_sources().values():
        rows.append(
            {
                "source_id": source.source_id,
                "title": source.title,
                "db_path": str(source.db_path),
                "available": source.available,
                "tables": list(inspect_schema(source).keys()) if source.available else [],
            }
        )
    return rows
