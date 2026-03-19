"""Inventory Turnover Calculator"""
from typing import Any

from value_investment.pipeline.calculators import calculator
from value_investment.pipeline.fields import IFRSFields


@calculator
class InventoryTurnover:
    """Inventory Turnover Calculator
    
    Inventory Turnover = Operating Cost / Average Inventory
    Average Inventory = (Beginning Inventory + Ending Inventory) / 2
    """

    name = IFRSFields.INVENTORY_TURNOVER

    required_fields = {
        IFRSFields.OPERATING_COST,
        IFRSFields.INVENTORY,
    }

    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        """Calculate inventory turnover from cost and inventory

        Args:
            results: {field: {year: value}}

        Returns:
            {year: inventory_turnover_value}
        """
        cost = results.get(IFRSFields.OPERATING_COST, {})
        inventory = results.get(IFRSFields.INVENTORY, {})

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
