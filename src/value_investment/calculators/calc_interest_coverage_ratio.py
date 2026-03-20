"""Interest Coverage Ratio Calculator

Interest Coverage Ratio = Operating Profit / Interest Expense

Where:
- Operating Profit = 营业利润
- Interest Expense = 利息支出

This ratio measures a company's ability to pay its interest obligations.
Higher values indicate better ability to cover interest payments.
Also known as "times interest earned".

Formula: operating_profit / interest_expense

Reference: IFRSFields.OPERATING_PROFIT, CustomFields.INTEREST_EXPENSE
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "interest_coverage_ratio"

# 依赖字段
required_fields = ["operating_profit", "interest_expense"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate Interest Coverage Ratio

    Args:
        results: {field: {year: value}}
            - operating_profit: Operating profit values by year
            - interest_expense: Interest expense values by year

    Returns:
        {year: interest_coverage_ratio or None if interest_expense is 0}
    """
    operating_profit = results.get("operating_profit", {})
    interest_expense = results.get("interest_expense", {})

    ratio = {}
    for year in operating_profit:
        interest = interest_expense.get(year, 0)

        # Avoid division by zero
        if interest == 0:
            ratio[year] = None
        else:
            ratio[year] = operating_profit.get(year, 0) / interest

    return ratio
