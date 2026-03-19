"""Calculators module

All calculators must be decorated with @calculator to be discovered.

Usage:
    from value_investment.pipeline.calculators import calculator
    
    @calculator
    class ROICCalculator:
        name = "roic"
        required_fields = {...}
        def calculate(self, results): ...
"""
from value_investment.pipeline.calculators.registry import (
    calculator,
    get_registered_calculators,
    instantiate_calculators,
)
from value_investment.pipeline.validator import validate_calculators, get_validation_summary, assert_all_valid
from value_investment.pipeline.fields import ALL_FIELDS

# Explicit imports for IDE support
from value_investment.pipeline.calculators.gross_profit import GrossProfit
from value_investment.pipeline.calculators.implied_growth import ImpliedGrowth
from value_investment.pipeline.calculators.inventory_turnover import InventoryTurnover
from value_investment.pipeline.calculators.operating_profit_margin import OperatingProfitMargin


def _validate_fields(calc) -> None:
    """Validate calculator's required_fields are valid"""
    invalid = set(calc.required_fields) - ALL_FIELDS
    if invalid:
        raise ValueError(f"Calculator '{calc.name}' has invalid fields: {invalid}")


# Instantiate all registered calculators
ALL_CALCULATORS = instantiate_calculators()

# Validate fields
for calc in ALL_CALCULATORS:
    _validate_fields(calc)

# Build name -> calculator map
CALCULATOR_MAP = {calc.name: calc for calc in ALL_CALCULATORS}

__all__ = [
    "calculator",  # Required decorator
    "GrossProfit",
    "ImpliedGrowth",
    "InventoryTurnover",
    "OperatingProfitMargin",
    "ALL_CALCULATORS",
    "CALCULATOR_MAP",
    "validate_calculators",
    "get_validation_summary",
    "assert_all_valid",
]
