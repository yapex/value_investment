"""Accounts Receivable Growth Rate Calculator

Growth Rate = (Current AR - Previous AR) / Previous AR

Measures how quickly accounts receivable are changing year-over-year.
Positive values may indicate easing credit policies or collection issues.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "accounts_receivable_growth_rate"

# 依赖字段
required_fields = ["accounts_receivable"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate accounts receivable year-over-year growth rate

    Args:
        results: {field: {year: value}}
            - accounts_receivable: AR values by year

    Returns:
        {year: growth_rate or None if previous year is missing/zero}
    """
    ar = results.get("accounts_receivable", {})

    rates = {}
    for year in ar:
        prev = ar.get(year - 1)
        curr = ar.get(year)

        if prev is None or prev == 0:
            continue
        rates[year] = (curr - prev) / prev

    return rates
