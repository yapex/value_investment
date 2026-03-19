"""Gross Profit Calculator

Gross Profit = Total Revenue - Operating Cost
"""
from typing import Any

# 依赖字段（使用字符串字段名）
required_fields = ["total_revenue", "operating_cost"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float]:
    """Calculate gross profit from revenue and cost

    Args:
        results: {field: {year: value}}

    Returns:
        {year: gross_profit_value}
    """
    revenue = results.get("total_revenue", {})
    cost = results.get("operating_cost", {})

    return {
        year: revenue.get(year, 0) - cost.get(year, 0)
        for year in revenue
    }
