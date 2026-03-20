"""Goodwill to Net Assets Ratio Calculator

Formula: ratio = goodwill / total_equity

Measures the proportion of goodwill in total equity.
Used as a risk screening indicator (排雷指标).
High goodwill may indicate impairment risk.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "goodwill_to_net_assets_ratio"

# 依赖字段
required_fields = ["goodwill", "total_equity"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate goodwill to net assets ratio

    Args:
        results: {field: {year: value}}
            - goodwill: Goodwill by year
            - total_equity: Total equity by year

    Returns:
        {year: ratio or None if missing data}
    """
    goodwill = results.get("goodwill", {})
    total_equity = results.get("total_equity", {})

    ratios = {}
    for year in goodwill:
        gw_val = goodwill.get(year)
        te_val = total_equity.get(year)

        if gw_val is None or te_val is None or te_val == 0:
            continue

        ratios[year] = gw_val / te_val

    return ratios
