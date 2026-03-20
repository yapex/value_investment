"""Core Business Ratio Calculator

Core Business Ratio = Main Business Income / Total Revenue

Measures how focused the company is on its core business activities.
- Close to 1.0: Company is highly focused on main business
- Clearly < 1.0: Significant other business income exists

Formula: main_business_income / total_revenue

Note: If main_business_income is not available (A-share market),
use total_revenue as main business income (ratio = 1.0)
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "core_business_ratio"

# 依赖字段
required_fields = ["main_business_income", "total_revenue"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate core business ratio

    Args:
        results: {field: {year: value}}
            - main_business_income: Main business income by year
            - total_revenue: Total revenue by year

    Returns:
        {year: core_business_ratio or None if total_revenue is 0 or missing}
    """
    main = results.get("main_business_income", {})
    total = results.get("total_revenue", {})

    ratio = {}
    # 获取所有年份
    years = set(main.keys()) | set(total.keys())

    for year in years:
        total_rev = total.get(year)
        main_inc = main.get(year)

        # 如果 main_business_income 不可用，使用 total_revenue（假设全是主营业务）
        if main_inc is None or main_inc == 0:
            if total_rev and total_rev > 0:
                # A 股市场：营业收入 ≈ 主营业务收入
                ratio[year] = 1.0
            continue

        if total_rev is None or total_rev == 0:
            continue

        ratio[year] = main_inc / total_rev

    return ratio
