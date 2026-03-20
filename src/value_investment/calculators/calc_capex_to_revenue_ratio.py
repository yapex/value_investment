"""CAPEX to Revenue Ratio Calculator

Ratio = Capital Expenditure / Total Revenue

Measures the proportion of capital expenditure relative to revenue.
High values (>0.3) indicate capital-intensive operations.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "capex_to_revenue_ratio"

# 依赖字段
required_fields = ["capital_expenditure", "total_revenue"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate CAPEX to revenue ratio

    Args:
        results: {field: {year: value}}
            - capital_expenditure: CAPEX by year
            - total_revenue: Total revenue by year

    Returns:
        {year: ratio or None if revenue is missing/zero}
    """
    capex = results.get("capital_expenditure", {})
    revenue = results.get("total_revenue", {})

    ratios = {}
    for year in capex:
        revenue_val = revenue.get(year)
        capex_val = capex.get(year)

        # Need both CAPEX and revenue data
        if revenue_val is None or revenue_val == 0:
            continue
        ratios[year] = capex_val / revenue_val

    return ratios
