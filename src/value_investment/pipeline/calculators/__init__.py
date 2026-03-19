"""Calculators module"""
from value_investment.pipeline.calculators.gross_profit import GrossProfitCalculator
from value_investment.pipeline.calculators.inventory_turnover import InventoryTurnoverCalculator

# 注册所有 Calculator
ALL_CALCULATORS = [
    GrossProfitCalculator(),
    InventoryTurnoverCalculator(),
]

# name -> calculator 映射
CALCULATOR_MAP = {calc.name: calc for calc in ALL_CALCULATORS}

__all__ = [
    "GrossProfitCalculator",
    "InventoryTurnoverCalculator",
    "ALL_CALCULATORS",
    "CALCULATOR_MAP",
]
