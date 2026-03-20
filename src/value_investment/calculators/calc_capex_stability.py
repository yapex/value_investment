"""CAPEX Stability Calculator

Formula: Stability = StdDev / Mean (coefficient of variation)

Measures the stability of capital expenditure as a percentage of revenue.
Lower volatility indicates more predictable investment behavior.
"""
import statistics
from typing import Any

# 依赖字段
required_fields = ["capital_expenditure", "total_revenue"]

# 时间窗口（年）
WINDOW_YEARS = 5


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate CAPEX stability (coefficient of variation)

    Args:
        results: {field: {year: value}}
            - capital_expenditure: CAPEX by year
            - total_revenue: Total revenue by year

    Returns:
        {year: volatility (std/mean) or None if insufficient data}
    """
    capex = results.get("capital_expenditure", {})
    revenue = results.get("total_revenue", {})

    # Union of all years
    all_years = set(capex.keys()) | set(revenue.keys())
    
    # Calculate ratio for each year
    ratios = {}
    for year in all_years:
        capex_val = capex.get(year)
        rev_val = revenue.get(year)

        if capex_val is not None and rev_val is not None and rev_val != 0:
            ratios[year] = abs(capex_val) / rev_val  # Use absolute value

    if len(ratios) < WINDOW_YEARS:
        return {}

    sorted_years = sorted(ratios.keys())
    stabilities = {}

    for i in range(WINDOW_YEARS - 1, len(sorted_years)):
        end_year = sorted_years[i]

        # Get window of values
        window_years = sorted_years[i - WINDOW_YEARS + 1 : i + 1]
        window_values = []

        for y in window_years:
            val = ratios.get(y)
            if val is None:
                window_values = []
                break
            window_values.append(val)

        # Skip if any value is missing or insufficient
        if len(window_values) < WINDOW_YEARS:
            continue

        mean_val = statistics.mean(window_values)

        # Skip if mean is zero or very small
        if mean_val < 0.001:
            continue

        # Calculate coefficient of variation (std / mean)
        stdev = statistics.stdev(window_values)
        cv = stdev / mean_val

        stabilities[end_year] = cv

    return stabilities
