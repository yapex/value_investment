"""Financing Cost Rate Calculator

Financing Cost Rate = Finance Expense Ratio / Interest Bearing Debt

Where:
- Finance Expense Ratio = 财务费用率 = 财务费用 / 营业收入
- Interest Bearing Debt = 有息负债

This ratio measures the average financing cost.
Lower values indicate cheaper borrowing.

Formula: finance_expense_ratio / interest_bearing_debt
"""
from typing import Any

OUTPUT_FIELD = "financing_cost_rate"
required_fields = ["finance_expense_ratio", "interest_bearing_debt"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate Financing Cost Rate

    Args:
        results: {field: {year: value}}

    Returns:
        {year: financing cost rate or None if interest_bearing_debt is 0}
    """
    fe_ratio = results.get("finance_expense_ratio", {})
    debt = results.get("interest_bearing_debt", {})

    ratio = {}
    for year in fe_ratio:
        debt_val = debt.get(year, 0)
        if debt_val == 0:
            ratio[year] = None
        else:
            ratio[year] = fe_ratio.get(year, 0) / debt_val

    return ratio
