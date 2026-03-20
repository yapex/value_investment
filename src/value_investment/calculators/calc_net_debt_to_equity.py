"""Net Debt to Equity Calculator

Net Debt to Equity = Net Debt / Total Equity

Where:
- Net Debt = Interest Bearing Debt - Cash and Equivalents
- Total Equity = Total Equity

This ratio measures a company's financial leverage. Higher values indicate 
more leverage (more debt relative to equity).

Formula: net_debt / total_equity

Reference: CustomFields.NET_DEBT, IFRSFields.TOTAL_EQUITY
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "net_debt_to_equity"

# 依赖字段
required_fields = ["net_debt", "total_equity"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate Net Debt to Equity ratio

    Args:
        results: {field: {year: value}}
            - net_debt: Net debt values by year
            - total_equity: Total equity values by year

    Returns:
        {year: net_debt_to_equity_ratio or None if total_equity is 0}
    """
    net_debt = results.get("net_debt", {})
    total_equity = results.get("total_equity", {})

    ratio = {}
    for year in net_debt:
        equity = total_equity.get(year, 0)
        
        # Avoid division by zero
        if equity == 0:
            ratio[year] = None
        else:
            ratio[year] = net_debt.get(year, 0) / equity

    return ratio
