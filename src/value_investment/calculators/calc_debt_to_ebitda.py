"""Debt to EBITDA Calculator

Debt to EBITDA = Interest Bearing Debt / EBITDA

Where:
- Interest Bearing Debt = 有息负债
- EBITDA = 息税折旧摊销前利润

This ratio measures the company's ability to repay its debt.
Lower values indicate better debt repayment capability.
Industry standard: < 3x is acceptable, > 4x is concerning.

Formula: interest_bearing_debt / ebitda
"""
from typing import Any

OUTPUT_FIELD = "debt_to_ebitda"
required_fields = ["interest_bearing_debt", "ebitda"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate Debt to EBITDA ratio

    Args:
        results: {field: {year: value}}

    Returns:
        {year: debt_to_ebitda ratio or None if ebitda is 0}
    """
    debt = results.get("interest_bearing_debt", {})
    ebitda = results.get("ebitda", {})

    ratio = {}
    for year in debt:
        ebitda_val = ebitda.get(year, 0)
        if ebitda_val == 0:
            ratio[year] = None
        else:
            ratio[year] = debt.get(year, 0) / ebitda_val

    return ratio
