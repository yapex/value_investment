"""Free Cash Flow to Debt Calculator

FCF to Debt = Free Cash Flow to Firm / Interest Bearing Debt

Where:
- Free Cash Flow to Firm (FCFF) = 企业自由现金流
- Interest Bearing Debt = 有息负债

This ratio measures the company's ability to pay off its debt using free cash flow.
Higher values indicate better debt coverage capability.

Formula: free_cash_flow_to_firm / interest_bearing_debt

Reference: CustomFields.FREE_CASH_FLOW_TO_FIRM, CustomFields.INTEREST_BEARING_DEBT
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "free_cash_flow_to_debt"

# 依赖字段
required_fields = ["free_cash_flow_to_firm", "interest_bearing_debt"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate Free Cash Flow to Debt ratio

    Args:
        results: {field: {year: value}}
            - free_cash_flow_to_firm: FCFF values by year
            - interest_bearing_debt: Interest bearing debt values by year

    Returns:
        {year: free_cash_flow_to_debt ratio or None if interest_bearing_debt is 0}
    """
    fcf = results.get("free_cash_flow_to_firm", {})
    debt = results.get("interest_bearing_debt", {})

    ratio = {}
    for year in fcf:
        interest_bearing_debt = debt.get(year, 0)

        # Avoid division by zero
        if interest_bearing_debt == 0:
            ratio[year] = None
        else:
            ratio[year] = fcf.get(year, 0) / interest_bearing_debt

    return ratio
