"""Core Business Ratio Calculator

Core Business Ratio = Main Business Income / Total Revenue

Measures how focused the company is on its core business activities.
- Close to 1.0: Company is highly focused on main business
- Clearly < 1.0: Significant other business income exists

Formula: main_business_income / total_revenue
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "core_business_ratio"

# 依赖字段
required_fields = ["main_business_income", "total_revenue"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate core business ratio

    Args:
        results: {field: {year: value}}
            - main_business_income: Main business income by year
            - total_revenue: Total revenue by year

    Returns:
        {year: core_business_ratio or None if total_revenue is 0 or missing}
    """
    main = results.get("main_business_income", {})
    total = results.get("total_revenue", {})

    ratio = {}
    for year in main:
        total_rev = total.get(year)
        main_inc = main.get(year)

        if total_rev is None or total_rev == 0:
            continue
        ratio[year] = main_inc / total_rev

    return ratio
