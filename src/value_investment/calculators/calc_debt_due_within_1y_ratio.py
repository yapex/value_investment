"""Debt Due Within 1 Year Ratio Calculator

Formula: (short_term_borrowings + non_current_liabilities_due_1y + bonds_payable) / total_liabilities

Measures the proportion of debt due within 1 year to total liabilities.
Higher ratio indicates greater short-term refinancing risk.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "debt_due_within_1y_ratio"

# 依赖字段
required_fields = [
    "short_term_borrowings",
    "non_current_liabilities_due_1y",
    "bond_payable",
    "total_liabilities",
]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate debt due within 1 year ratio

    Args:
        results: {field: {year: value}}
            - short_term_borrowings: Short-term borrowings by year
            - non_current_liabilities_due_1y: Non-current liabilities due within 1 year by year
            - bond_payable: Bonds payable by year
            - total_liabilities: Total liabilities by year

    Returns:
        {year: ratio or None if total_liabilities is missing/zero}
    """
    st_borrow = results.get("short_term_borrowings", {})
    non_cur_1y = results.get("non_current_liabilities_due_1y", {})
    bonds = results.get("bond_payable", {})
    total_liab = results.get("total_liabilities", {})

    ratios = {}
    # Use total_liabilities years as base
    for year in total_liab:
        total = total_liab.get(year)
        
        # Skip if total liabilities is missing or zero
        if total is None or total == 0:
            continue
        
        # Sum up all components (treat None as 0)
        due_1y = (st_borrow.get(year) or 0) + (non_cur_1y.get(year) or 0) + (bonds.get(year) or 0)
        
        ratios[year] = due_1y / total

    return ratios
