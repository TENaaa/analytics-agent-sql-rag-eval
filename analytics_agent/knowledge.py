from __future__ import annotations


KNOWLEDGE_BASE = [
    {
        "id": "benefit_channel_roi",
        "source_id": "benefit_ltv",
        "keywords": ["渠道", "roas", "毛利", "cac", "cpa", "权益"],
        "metric": "毛利 ROAS = 归因毛利 / 触点成本；适合比较不同权益触点的预算效率。",
    },
    {
        "id": "benefit_solution_priority",
        "source_id": "benefit_ltv",
        "keywords": ["优先", "根因", "方案", "p0", "权益"],
        "metric": "方案优先级综合收益、难度、预算、风险和预期增量，输出 P0/P1/P2。",
    },
    {
        "id": "search_tail_experiment",
        "source_id": "search_rank",
        "keywords": ["搜索", "排序", "treatment", "长尾", "query", "gmv"],
        "metric": "长尾 query 需要单独监控 treatment 与 control 的下单率和 GMV/session。",
    },
    {
        "id": "connected_experiment",
        "source_id": "connected_vehicle",
        "keywords": ["车主", "生命周期", "个性化", "实验", "control", "treatment", "续约"],
        "metric": "车主 App 实验通过 holdout/control/treatment 比较购买率、毛利和活跃行为。",
    },
]


def retrieve(question: str, top_k: int = 3) -> list[dict[str, str]]:
    q = question.lower()
    scored = []
    for item in KNOWLEDGE_BASE:
        score = sum(1 for kw in item["keywords"] if kw.lower() in q)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored[:top_k]] or [KNOWLEDGE_BASE[0]]
