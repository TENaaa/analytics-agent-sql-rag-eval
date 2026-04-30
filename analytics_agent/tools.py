from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Optional

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib-analytics-agent")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/matplotlib-analytics-agent-cache")
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True, exist_ok=True)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .config import FIGURE_DIR
from .sql_safety import validate_readonly_sql

plt.rcParams.update(
    {
        "font.sans-serif": ["PingFang SC", "Arial Unicode MS", "Heiti TC", "SimHei", "DejaVu Sans"],
        "axes.unicode_minus": False,
    }
)


def execute_sql(db_path: Path, sql: str) -> pd.DataFrame:
    validate_readonly_sql(sql)
    with sqlite3.connect(db_path) as conn:
        return pd.read_sql_query(sql, conn)


def save_chart(df: pd.DataFrame, title: str, name: str) -> Optional[Path]:
    if df.empty or len(df.columns) < 2:
        return None
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    x_col = df.columns[0]
    numeric_cols = [col for col in df.columns[1:] if pd.api.types.is_numeric_dtype(df[col])]
    if not numeric_cols:
        return None
    y_col = numeric_cols[0]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    plot_df = df.head(10).copy()
    ax.bar(plot_df[x_col].astype(str), plot_df[y_col], color="#2f6f73")
    ax.set_title(title)
    ax.set_ylabel(y_col)
    ax.tick_params(axis="x", labelrotation=25)
    path = FIGURE_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path
