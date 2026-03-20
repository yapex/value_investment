"""Net Profit Margin Calculator

Net Margin = Net Profit / Total Revenue

Where:
- Net Profit = 净利润
- Total Revenue = 营业收入（营业总收入）

This ratio measures how much profit a company makes for every yuan of revenue.
Higher values indicate better profitability efficiency.

Formula: net_profit / total_revenue

Reference: IFRSFields.NET_PROFIT, IFRSFields.TOTAL_REVENUE
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "net_margin"

# 依赖字段
required_fields = ["net_profit", "total_revenue"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate Net Profit Margin

    Args:
        results: {field: {year: value}}
            - net_profit: Net profit values by year
            - total_revenue: Total revenue values by year

    Returns:
        {year: net_margin or None if revenue is missing/zero}
    """
    net_profit = results.get("net_profit", {})
    total_revenue = results.get("total_revenue", {})

    margin = {}
    for year in net_profit:
        revenue = total_revenue.get(year, 0)

        # 避免除以零
        if not revenue:
            margin[year] = None
        else:
            margin[year] = net_profit.get(year, 0) / revenue

    return margin
