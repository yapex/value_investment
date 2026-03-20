"""Inventory Revenue Growth Gap Calculator

Gap = Inventory Growth Rate - Revenue YoY Growth Rate

Positive gap: inventory grows faster than revenue -> potential accumulation risk
Negative gap: inventory grows slower than revenue -> healthy signal
Used as a risk screening indicator (排雷指标).
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "inventory_revenue_growth_gap"

# 依赖字段
required_fields = ["inventory", "revenue_yoy"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate inventory vs revenue growth gap

    Args:
        results: {field: {year: value}}
            - inventory: Inventory values by year
            - revenue_yoy: Revenue year-over-year growth rate (already in percentage form)

    Returns:
        {year: gap or None if inventory growth or revenue_yoy is missing}
    """
    inventory = results.get("inventory", {})
    revenue_yoy = results.get("revenue_yoy", {})

    gaps = {}
    for year in inventory:
        prev_inv = inventory.get(year - 1)
        curr_inv = inventory.get(year)
        rev_growth = revenue_yoy.get(year)

        # Calculate inventory growth rate
        if prev_inv is None or prev_inv == 0:
            inv_growth = None
        else:
            inv_growth = (curr_inv - prev_inv) / prev_inv

        # Gap = inv_growth - revenue_yoy
        if inv_growth is None or rev_growth is None:
            continue
        gaps[year] = inv_growth - rev_growth

    return gaps
