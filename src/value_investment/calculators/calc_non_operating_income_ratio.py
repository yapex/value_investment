"""Non-Operating Income Ratio Calculator

Formula: ratio = non_operating_income / total_profit

Measures the proportion of non-operating income in total profit.
Used as a risk screening indicator (排雷指标).
High ratio indicates poor earnings quality.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "non_operating_income_ratio"

# 依赖字段
required_fields = ["non_operating_income", "operating_profit"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate non-operating income ratio

    Args:
        results: {field: {year: value}}
            - non_operating_income: Non-operating income by year
            - operating_profit: Operating profit by year (proxy for total profit)

    Returns:
        {year: ratio or None if missing data}
    """
    non_op_income = results.get("non_operating_income", {})
    operate_profit = results.get("operating_profit", {})

    ratios = {}
    for year in non_op_income:
        noi_val = non_op_income.get(year)
        op_val = operate_profit.get(year)

        if noi_val is None or op_val is None or op_val == 0:
            continue

        ratios[year] = noi_val / op_val

    return ratios
