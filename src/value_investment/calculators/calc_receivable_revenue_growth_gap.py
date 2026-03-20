"""Receivable Revenue Growth Gap Calculator

Gap = Accounts Receivable Growth Rate - Revenue YoY Growth Rate

Positive gap: AR grows faster than revenue -> potential receivables accumulation risk
Negative gap: AR grows slower than revenue -> healthy signal
Used as a risk screening indicator (排雷指标).
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "receivable_revenue_growth_gap"

# 依赖字段
required_fields = ["accounts_receivable", "revenue_yoy"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate AR vs revenue growth gap

    Args:
        results: {field: {year: value}}
            - accounts_receivable: AR values by year
            - revenue_yoy: Revenue year-over-year growth rate

    Returns:
        {year: gap or None if AR growth or revenue_yoy is missing}
    """
    ar = results.get("accounts_receivable", {})
    revenue_yoy = results.get("revenue_yoy", {})

    gaps = {}
    for year in ar:
        prev_ar = ar.get(year - 1)
        curr_ar = ar.get(year)
        rev_growth = revenue_yoy.get(year)

        # Calculate AR growth rate
        if prev_ar is None or prev_ar == 0:
            ar_growth = None
        else:
            ar_growth = (curr_ar - prev_ar) / prev_ar

        # Gap = ar_growth - revenue_yoy
        if ar_growth is None or rev_growth is None:
            continue
        gaps[year] = ar_growth - rev_growth

    return gaps
