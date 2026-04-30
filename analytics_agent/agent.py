from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

from .catalog import DataSource, load_sources
from .knowledge import retrieve
from .tools import execute_sql, save_chart


@dataclass(frozen=True)
class AgentAnswer:
    question: str
    source_id: str
    sql: str
    rows: list[dict[str, object]]
    summary: str
    chart_path: Optional[str]
    retrieved_context: list[dict[str, str]]
    success: bool
    error: Optional[str] = None


def answer_question(question: str) -> AgentAnswer:
    contexts = retrieve(question)
    source_id = _route(question, contexts)
    sources = load_sources()
    source = sources[source_id]
    sql = _sql_for_question(question, source_id)
    if not source.available:
        return AgentAnswer(question, source_id, sql, [], f"数据源 `{source.title}` 暂不可用，请先运行对应项目的一键命令生成 SQLite。", None, contexts, False, "missing_db")
    try:
        df = execute_sql(source.db_path, sql)
        chart = save_chart(df, f"{source.title} - Agent Query", _safe_name(question))
        summary = _summarize(question, source, df)
        return AgentAnswer(question, source_id, sql, df.head(30).to_dict(orient="records"), summary, str(chart) if chart else None, contexts, True)
    except Exception as exc:
        return AgentAnswer(question, source_id, sql, [], f"查询失败：{exc}", None, contexts, False, str(exc))


def _route(question: str, contexts: list[dict[str, str]]) -> str:
    q = question.lower()
    if any(word in q for word in ["搜索", "排序", "query", "长尾", "ndcg"]):
        return "search_rank"
    if any(word in q for word in ["权益", "roas", "渠道", "根因", "方案"]):
        return "benefit_ltv"
    if any(word in q for word in ["车主", "生命周期", "续约", "个性化"]):
        return "connected_vehicle"
    return contexts[0]["source_id"]


def _sql_for_question(question: str, source_id: str) -> str:
    q = question.lower()
    if source_id == "benefit_ltv" and any(word in q for word in ["优先", "根因", "方案", "p0"]):
        return """
        SELECT priority, root_cause, solution_name, priority_score, expected_lift_pp
        FROM solution_scores
        ORDER BY CASE priority WHEN 'P0' THEN 1 WHEN 'P1' THEN 2 ELSE 3 END, priority_score DESC
        LIMIT 8
        """
    if source_id == "benefit_ltv":
        return """
        WITH spend AS (
            SELECT placement_id, SUM(spend) AS spend
            FROM daily_spend_inventory
            GROUP BY placement_id
        ),
        revenue AS (
            SELECT te.placement_id,
                   COUNT(DISTINCT re.user_id) AS buyers,
                   SUM(CASE WHEN re.refunded_flag = 0 THEN re.gross_margin ELSE 0 END) AS gross_margin
            FROM revenue_events re
            JOIN touch_events te ON te.touch_event_id = re.attributed_touch_event_id
            GROUP BY te.placement_id
        )
        SELECT p.placement_name,
               ROUND(COALESCE(r.gross_margin, 0), 2) AS gross_margin,
               ROUND(COALESCE(s.spend, 0), 2) AS spend,
               ROUND(COALESCE(r.gross_margin, 0) / NULLIF(s.spend, 0), 2) AS margin_roas,
               COALESCE(r.buyers, 0) AS buyers
        FROM placements p
        LEFT JOIN spend s ON s.placement_id = p.placement_id
        LEFT JOIN revenue r ON r.placement_id = p.placement_id
        ORDER BY margin_roas DESC
        LIMIT 8
        """
    if source_id == "search_rank":
        return """
        WITH outcome AS (
            SELECT e.variant,
                   q.tail_type,
                   s.session_id,
                   MAX(i.ordered) AS ordered,
                   SUM(i.gross_revenue) AS gmv
            FROM search_sessions s
            JOIN experiments e ON e.session_id = s.session_id
            JOIN queries q ON q.query_id = s.query_id
            JOIN impressions i ON i.session_id = s.session_id
            GROUP BY e.variant, q.tail_type, s.session_id
        )
        SELECT variant,
               tail_type,
               COUNT(*) AS sessions,
               ROUND(AVG(ordered), 4) AS order_rate,
               ROUND(SUM(gmv) / COUNT(*), 2) AS gmv_per_session
        FROM outcome
        GROUP BY variant, tail_type
        ORDER BY tail_type, CASE variant WHEN 'holdout' THEN 1 WHEN 'control' THEN 2 WHEN 'treatment' THEN 3 ELSE 4 END
        """
    return """
    WITH user_outcome AS (
        SELECT ea.variant,
               u.user_id,
               COUNT(DISTINCT o.order_id) AS orders,
               COALESCE(SUM(o.gross_margin), 0) AS gross_margin
        FROM users u
        JOIN experiment_assignments ea ON ea.user_id = u.user_id
        LEFT JOIN orders o ON o.user_id = u.user_id AND o.order_status = 'completed'
        GROUP BY ea.variant, u.user_id
    )
    SELECT variant,
           COUNT(*) AS users,
           ROUND(AVG(CASE WHEN orders > 0 THEN 1 ELSE 0 END), 4) AS buyer_rate,
           ROUND(AVG(gross_margin), 2) AS avg_margin
    FROM user_outcome
    GROUP BY variant
    ORDER BY CASE variant WHEN 'holdout' THEN 1 WHEN 'control' THEN 2 WHEN 'treatment' THEN 3 ELSE 4 END
    """


def _summarize(question: str, source: DataSource, df: pd.DataFrame) -> str:
    if df.empty:
        return "查询成功，但没有返回数据。建议检查筛选条件或数据源是否已生成。"
    first = df.iloc[0].to_dict()
    if "margin_roas" in df.columns:
        return f"从 `{source.title}` 查询看，毛利 ROAS 最高的是 `{first.get('placement_name')}`，margin_roas={first.get('margin_roas')}。建议结合 holdout 增量实验确认预算是否真的带来新增毛利。"
    if "priority" in df.columns:
        return f"优先级最高方案是 `{first.get('solution_name')}`，对应根因 `{first.get('root_cause')}`，优先级为 {first.get('priority')}。"
    if "tail_type" in df.columns:
        treatment = df.loc[df["variant"] == "treatment"]
        if not treatment.empty:
            best = treatment.sort_values("gmv_per_session", ascending=False).iloc[0]
            return f"搜索排序 treatment 在 `{best['tail_type']}` query 上 GMV/session 最高，为 {best['gmv_per_session']}。下一步应对比 control 的同分层表现。"
    if "buyer_rate" in df.columns:
        best = df.sort_values("buyer_rate", ascending=False).iloc[0]
        return f"车主 App 实验中 `{best['variant']}` 购买率最高，为 {best['buyer_rate']:.2%}，需要同时查看毛利和触达压力 guardrail。"
    return f"已在 `{source.title}` 上完成查询，返回 {len(df)} 行结果。"


def _safe_name(question: str) -> str:
    digest = hashlib.md5(question.encode("utf-8")).hexdigest()[:10]
    return f"agent_chart_{digest}"


def llm_mode() -> str:
    return "openai_optional" if os.environ.get("OPENAI_API_KEY") else "deterministic_mock"
