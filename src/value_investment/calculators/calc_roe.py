"""ROE (Return on Equity) Calculator

ROE = Net Profit / Average Total Equity

Where:
- Net Profit = 净利润
- Average Total Equity = (期初净资产 + 期末净资产) / 2

This ratio measures a company's profitability by revealing how much profit
a company generates with the money shareholders have invested.
Higher values (>15%) indicate strong profitability.

Formula: net_profit / average_total_equity

Reference: IFRSFields.NET_PROFIT, IFRSFields.TOTAL_EQUITY
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "roe"

# 依赖字段
required_fields = ["net_profit", "total_equity"]


def _calculate_average(current: float, previous: float) -> float | None:
    """Calculate average, return None if any value is missing or zero"""
    if not current or not previous:
        return None
    return (current + previous) / 2


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate ROE

    Args:
        results: {field: {year: value}}
            - net_profit: Net profit values by year
            - total_equity: Total equity values by year

    Returns:
        {year: roe or None if average_equity is missing/zero}
    """
    net_profit = results.get("net_profit", {})
    total_equity = results.get("total_equity", {})

    roe = {}
    years = sorted(net_profit.keys())

    for i, year in enumerate(years):
        profit = net_profit.get(year, 0)

        # 获取当年和上一年净资产
        current_equity = total_equity.get(year, 0)
        previous_equity = total_equity.get(years[i - 1], 0) if i > 0 else 0

        # 计算平均净资产
        avg_equity = _calculate_average(current_equity, previous_equity)

        # 避免除以零
        if avg_equity is None or avg_equity == 0:
            roe[year] = None
        else:
            roe[year] = profit / avg_equity

    return roe
