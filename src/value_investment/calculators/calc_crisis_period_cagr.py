"""Crisis Period CAGR Calculator

Crisis Period CAGR = (End Value / Start Value) ^ (1 / Years) - 1

Measures the compound annual growth rate during a crisis period.
Used to assess company resilience during economic downturns.

Note: This calculator requires pre-defined crisis periods or uses
a default window of 3 years for calculation.
"""
import statistics
from typing import Any

# 输出字段名
OUTPUT_FIELD = "crisis_period_cagr"

# 依赖字段
required_fields = ["revenue_yoy"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate crisis period CAGR

    Args:
        results: {field: {year: value}}
            - revenue_yoy: Revenue year-over-year growth rate by year

    Returns:
        {year: CAGR for crisis period starting 3 years prior}
    """
    revenue_yoy = results.get("revenue_yoy", {})

    if len(revenue_yoy) < 3:
        return {}

    sorted_years = sorted(revenue_yoy.keys())
    cagrs = {}

    # Calculate CAGR for each year with 3-year lookback
    for i in range(2, len(sorted_years)):
        end_year = sorted_years[i]
        start_year = sorted_years[i - 2]

        # Get YoY values for the period
        values = []
        for y in sorted_years[i - 2 : i + 1]:
            val = revenue_yoy.get(y)
            if val is None:
                values = []
                break
            values.append(val)

        if len(values) != 3:
            continue

        # Calculate compound growth from start to end
        # Convert YoY rates to growth factors
        growth_factors = [1 + v for v in values]

        # Product of growth factors gives total growth
        total_growth = 1.0
        for gf in growth_factors:
            total_growth *= gf

        # CAGR = total_growth^(1/3) - 1
        years = 3
        cagr = total_growth ** (1 / years) - 1

        cagrs[end_year] = cagr

    return cagrs
