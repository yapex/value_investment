"""Receivables Turnover Calculator

Receivables Turnover = Total Revenue / Average Accounts Receivable

Where:
- Total Revenue = 营业收入（营业总收入）
- Average Accounts Receivable = (期初应收账款 + 期末应收账款) / 2

This ratio measures how efficiently a company collects its receivables.
Higher values indicate faster collection and better cash flow management.

Formula: total_revenue / average_accounts_receivable

Reference: IFRSFields.TOTAL_REVENUE, IFRSFields.ACCOUNTS_RECEIVABLE
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "receivables_turnover"

# 依赖字段
required_fields = ["total_revenue", "accounts_receivable"]


def _calculate_average(current: float, previous: float) -> float | None:
    """Calculate average, return None if any value is missing or zero"""
    if not current or not previous:
        return None
    return (current + previous) / 2


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate Receivables Turnover

    Args:
        results: {field: {year: value}}
            - total_revenue: Total revenue values by year
            - accounts_receivable: Accounts receivable values by year

    Returns:
        {year: turnover or None if average_receivable is missing/zero}
    """
    revenue = results.get("total_revenue", {})
    receivables = results.get("accounts_receivable", {})

    turnover = {}
    years = sorted(revenue.keys())

    for i, year in enumerate(years):
        rev = revenue.get(year, 0)

        # 获取当年和上一年应收账款
        current_ar = receivables.get(year, 0)
        previous_ar = receivables.get(years[i - 1], 0) if i > 0 else 0

        # 计算平均应收账款
        avg_ar = _calculate_average(current_ar, previous_ar)

        # 避免除以零
        if avg_ar is None or avg_ar == 0:
            turnover[year] = None
        else:
            turnover[year] = rev / avg_ar

    return turnover
