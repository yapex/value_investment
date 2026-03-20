"""Interest Income Rate Calculator

Rate = Interest Income / Cash and Equivalents

Measures the return on cash holdings through interest income.
Higher values indicate better cash utilization efficiency.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "interest_income_rate"

# 依赖字段
required_fields = ["interest_income", "cash_and_equivalents"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate interest income rate

    Args:
        results: {field: {year: value}}
            - interest_income: Interest income by year
            - cash_and_equivalents: Cash and equivalents by year

    Returns:
        {year: rate or None if cash is missing/zero}
    """
    interest_income = results.get("interest_income", {})
    cash = results.get("cash_and_equivalents", {})

    rates = {}
    for year in interest_income:
        cash_val = cash.get(year)
        income_val = interest_income.get(year)

        # Need both interest income and cash data
        if cash_val is None or cash_val == 0:
            continue
        rates[year] = income_val / cash_val

    return rates
