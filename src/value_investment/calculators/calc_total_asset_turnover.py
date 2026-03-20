"""Total Asset Turnover Calculator

Total Asset Turnover = Total Revenue / Average Total Assets

Where:
- Total Revenue = 营业收入（营业总收入）
- Average Total Assets = (期初总资产 + 期末总资产) / 2

This ratio measures how efficiently a company uses its assets to generate revenue.
Higher values indicate more efficient asset utilization.

Formula: total_revenue / average_total_assets

Reference: IFRSFields.TOTAL_REVENUE, IFRSFields.TOTAL_ASSETS
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "total_asset_turnover"

# 依赖字段
required_fields = ["total_revenue", "total_assets"]


def _calculate_average(current: float, previous: float) -> float | None:
    """Calculate average, return None if any value is missing or zero"""
    if not current or not previous:
        return None
    return (current + previous) / 2


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate Total Asset Turnover

    Args:
        results: {field: {year: value}}
            - total_revenue: Total revenue values by year
            - total_assets: Total assets values by year

    Returns:
        {year: turnover or None if average_assets is missing/zero}
    """
    revenue = results.get("total_revenue", {})
    assets = results.get("total_assets", {})

    turnover = {}
    years = sorted(revenue.keys())

    for i, year in enumerate(years):
        rev = revenue.get(year, 0)

        # 获取当年和上一年总资产
        current_assets = assets.get(year, 0)
        previous_assets = assets.get(years[i - 1], 0) if i > 0 else 0

        # 计算平均总资产
        avg_assets = _calculate_average(current_assets, previous_assets)

        # 避免除以零
        if avg_assets is None or avg_assets == 0:
            turnover[year] = None
        else:
            turnover[year] = rev / avg_assets

    return turnover
