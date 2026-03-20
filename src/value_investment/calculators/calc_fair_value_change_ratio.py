"""Fair Value Change Ratio Calculator

Fair Value Change Ratio = Fair Value Change / Total Profit

Measures the proportion of profit from fair value changes.
High ratio indicates significant non-recurring gains/losses.
Used as a risk screening indicator (排雷指标).
"""
from typing import Any

# 依赖字段
required_fields = ["fair_value_change", "net_profit"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate fair value change ratio

    Args:
        results: {field: {year: value}}
            - fair_value_change: Fair value change by year
            - net_profit: Net profit by year

    Returns:
        {year: ratio or None if net_profit is 0 or missing}
    """
    fair_value = results.get("fair_value_change", {})
    net_profit = results.get("net_profit", {})

    # Union of all years
    all_years = set(fair_value.keys()) | set(net_profit.keys())
    
    ratios = {}
    for year in sorted(all_years):
        fv = fair_value.get(year)
        np = net_profit.get(year)

        # Only calculate if we have fair_value data
        if fv is None:
            continue
        
        # Handle missing or zero net_profit
        if np is None or np == 0:
            ratios[year] = None
        else:
            ratios[year] = fv / np

    return ratios
