"""Long Term Investment Ratio Calculator

Formula: ratio = long_term_investment / total_assets

Measures the proportion of long-term investments in total assets.
Reflects the degree of diversification and external investment scale.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "long_term_investment_ratio"

# 依赖字段
required_fields = ["long_term_investment", "total_assets"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate long term investment ratio

    Args:
        results: {field: {year: value}}
            - long_term_investment: Long term investments by year
            - total_assets: Total assets by year

    Returns:
        {year: ratio or None if missing data}
    """
    lt_inv = results.get("long_term_investment", {})
    total_assets = results.get("total_assets", {})

    ratios = {}
    for year in lt_inv:
        lti_val = lt_inv.get(year)
        ta_val = total_assets.get(year)

        if lti_val is None or ta_val is None or ta_val == 0:
            continue

        ratios[year] = lti_val / ta_val

    return ratios
