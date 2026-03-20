"""Cash to Net Profit Ratio Calculator

Cash to Net Profit Ratio = Operating Cash Flow / Net Profit

Where:
- Operating Cash Flow = 经营活动现金流
- Net Profit = 净利润

This is a quality check indicator - verifies earnings quality.
Healthy companies typically have ratio > 1 (cash profit > accounting profit).
Rule of thumb: ratio should be > 0.8 for good quality earnings.

Formula: operating_cash_flow / net_profit
"""
from typing import Any

OUTPUT_FIELD = "cash_to_net_profit_ratio"
required_fields = ["operating_cash_flow", "net_profit"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate Cash to Net Profit Ratio

    Args:
        results: {field: {year: value}}

    Returns:
        {year: cash_to_net_profit ratio or None if net_profit is 0}
    """
    ocf = results.get("operating_cash_flow", {})
    net_profit = results.get("net_profit", {})

    ratio = {}
    for year in ocf:
        profit_val = net_profit.get(year, 0)
        if profit_val == 0:
            ratio[year] = None
        else:
            ratio[year] = ocf.get(year, 0) / profit_val

    return ratio
