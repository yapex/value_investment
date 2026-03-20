"""Free Cash Flow to Debt Calculator

FCF to Debt = Free Cash Flow to Firm / Total Debt

Where:
- Free Cash Flow to Firm (FCFF) = 企业自由现金流
- Total Debt = 总债务 = 有息负债（interest_bearing_debt）

This ratio measures the company's ability to pay off its debt using free cash flow.
Higher values indicate better debt coverage capability.

Formula: free_cash_flow_to_firm / total_debt

Reference: CustomFields.FREE_CASH_FLOW_TO_FIRM, CustomFields.TOTAL_DEBT
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "free_cash_flow_to_debt"

# 依赖字段
required_fields = ["free_cash_flow_to_firm", "total_debt"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate Free Cash Flow to Debt ratio

    Args:
        results: {field: {year: value}}
            - free_cash_flow_to_firm: FCFF values by year
            - total_debt: Total debt values by year

    Returns:
        {year: free_cash_flow_to_debt ratio or None if total_debt is 0}
    """
    fcf = results.get("free_cash_flow_to_firm", {})
    debt = results.get("total_debt", {})

    ratio = {}
    for year in fcf:
        total_debt = debt.get(year, 0)

        # Avoid division by zero
        if total_debt == 0:
            ratio[year] = None
        else:
            ratio[year] = fcf.get(year, 0) / total_debt

    return ratio
