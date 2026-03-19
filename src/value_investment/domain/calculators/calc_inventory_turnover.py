"""Inventory Turnover Calculator

Inventory Turnover = Operating Cost / Average Inventory
Average Inventory = (Beginning Inventory + Ending Inventory) / 2
"""
from typing import Any

# 依赖字段
required_fields = ["operating_cost", "inventory"]


def calculate(results: dict[str, dict[int, Any]]) -> dict[int, float]:
    """Calculate inventory turnover from cost and inventory

    Args:
        results: {field: {year: value}}

    Returns:
        {year: inventory_turnover_value}
    """
    cost = results.get("operating_cost", {})
    inventory = results.get("inventory", {})

    turnover = {}
    # 计算所有年份的 turnover
    all_years = set(cost.keys()) | set(inventory.keys())
    for year in all_years:
        curr_inv = inventory.get(year, 0)
        prev_inv = inventory.get(year - 1, 0)
        avg_inv = (curr_inv + prev_inv) / 2
        if avg_inv != 0:
            turnover[year] = cost.get(year, 0) / avg_inv
    return turnover
