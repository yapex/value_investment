"""Inventory Growth Rate Calculator

Growth Rate = (Current Inventory - Previous Inventory) / Previous Inventory

Measures how quickly inventory levels are changing year-over-year.
Positive values indicate inventory accumulation.
"""
from typing import Any

# 输出字段名
OUTPUT_FIELD = "inventory_growth_rate"

# 依赖字段
required_fields = ["inventory"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float | None]:
    """Calculate inventory year-over-year growth rate

    Args:
        results: {field: {year: value}}
            - inventory: Inventory values by year

    Returns:
        {year: growth_rate or None if previous year is missing/zero}
    """
    inventory = results.get("inventory", {})

    rates = {}
    for year in inventory:
        prev = inventory.get(year - 1)
        curr = inventory.get(year)

        # Need both current and previous year data
        if prev is None or prev == 0:
            continue
        rates[year] = (curr - prev) / prev

    return rates
