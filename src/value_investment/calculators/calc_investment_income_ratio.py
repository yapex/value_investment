"""Investment Income Ratio Calculator

Investment Income Ratio = Investment Income / Total Profit

Measures the proportion of profit from investments.
High ratio indicates company relies on investment activities.
Used as a risk screening indicator (排雷指标).
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "investment_income_ratio"

# 依赖字段
required_fields = ["investment_income", "net_profit"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate investment income ratio

    Args:
        results: {field: {year: value}}
            - investment_income: Investment income by year
            - net_profit: Net profit by year

    Returns:
        {year: ratio or None if net_profit is 0 or missing}
    """
    invest_inc = results.get("investment_income", {})
    net_profit = results.get("net_profit", {})

    ratios = {}
    for year in invest_inc:
        ii = invest_inc.get(year)
        np = net_profit.get(year)

        if np is None or np == 0:
            ratios[year] = None
        else:
            ratios[year] = ii / np if ii is not None else None

    return ratios
