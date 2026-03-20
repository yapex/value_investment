"""Other Receivables Ratio Calculator

Formula: ratio = other_receivables / total_assets

Measures the proportion of other receivables in total assets.
Used as a risk screening indicator (排雷指标).
High ratio may indicate funds occupied by related parties.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "other_receivables_ratio"

# 依赖字段
required_fields = ["other_receivables", "total_assets"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate other receivables ratio

    Args:
        results: {field: {year: value}}
            - other_receivables: Other receivables by year
            - total_assets: Total assets by year

    Returns:
        {year: ratio or None if missing data}
    """
    other_recv = results.get("other_receivables", {})
    total_assets = results.get("total_assets", {})

    ratios = {}
    for year in other_recv:
        or_val = other_recv.get(year)
        ta_val = total_assets.get(year)

        if or_val is None or ta_val is None or ta_val == 0:
            continue

        ratios[year] = or_val / ta_val

    return ratios
