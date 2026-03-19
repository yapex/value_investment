"""Operating Profit Margin Calculator

Operating Profit Margin = Operating Profit / Total Revenue * 100
"""
from typing import Any

# 依赖字段
required_fields = ["operating_profit", "total_revenue"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float]:
    """Calculate operating profit margin

    Args:
        results: {field: {year: value}}

    Returns:
        {year: operating_profit_margin_percentage}
    """
    operating_profit = results.get("operating_profit", {})
    revenue = results.get("total_revenue", {})

    # Calculate margin for each year
    margin = {}
    for year in operating_profit:
        op = operating_profit.get(year, 0)
        rev = revenue.get(year, 0)

        # Avoid division by zero
        if rev > 0:
            margin[year] = (op / rev) * 100

    return margin
