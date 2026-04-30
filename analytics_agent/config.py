from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = PROJECT_ROOT.parent
REPORT_DIR = PROJECT_ROOT / "reports"
FIGURE_DIR = REPORT_DIR / "figures"
EVAL_PATH = PROJECT_ROOT / "eval" / "questions.json"

DEFAULT_SOURCES = {
    "connected_vehicle": {
        "title": "车主 App 生命周期增长",
        "db_path": PORTFOLIO_ROOT / "connected-vehicle-app-growth-analytics" / "output" / "analytics.sqlite",
        "description": "车主生命周期、多触点触达、续约/购买意向和运营质量。",
    },
    "benefit_ltv": {
        "title": "用车权益 LTV 与归因",
        "db_path": PORTFOLIO_ROOT / "growth-incrementality-ltv-attribution" / "output" / "analytics.sqlite",
        "description": "用车权益商城、渠道 ROI、VOC 根因、产品 LTV 和方案优先级。",
    },
    "search_rank": {
        "title": "本地生活搜索排序 ML",
        "db_path": PORTFOLIO_ROOT / "local-life-search-ranking-ml-lab" / "output" / "search_ranking.sqlite",
        "description": "搜索排序、长尾 query、实验 lift 和反事实评估。",
    },
}
