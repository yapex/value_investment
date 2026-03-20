"""Prepayment Ratio Calculator

Ratio = Prepayment / Total Assets

Measures the proportion of prepaid expenses in total assets.
High values may indicate strong supplier bargaining power or fund occupation.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "prepayment_ratio"

# 依赖字段
required_fields = ["prepayment", "total_assets"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate prepayment ratio

    Args:
        results: {field: {year: value}}
            - prepayment: Prepayment by year
            - total_assets: Total assets by year

    Returns:
        {year: ratio or None if total_assets is missing/zero}
    """
    prepayment = results.get("prepayment", {})
    total_assets = results.get("total_assets", {})

    ratios = {}
    for year in prepayment:
        assets_val = total_assets.get(year)
        prepay_val = prepayment.get(year)

        # Need both prepayment and total assets data
        if assets_val is None or assets_val == 0:
            continue
        ratios[year] = prepay_val / assets_val

    return ratios
