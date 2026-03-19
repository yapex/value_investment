"""Calculators module

Auto-discovers all classes implementing the Calculator Protocol.
No manual registration needed.
"""
from value_investment.pipeline.validator import discover_calculators, validate_calculators, get_validation_summary, assert_all_valid
from value_investment.pipeline.fields import ALL_FIELDS

# Explicit imports for IDE support and core calculators
from value_investment.pipeline.calculators.gross_profit import GrossProfitCalculator
from value_investment.pipeline.calculators.implied_growth import ImpliedGrowthCalculator
from value_investment.pipeline.calculators.inventory_turnover import InventoryTurnoverCalculator


def _validate_fields(calc) -> None:
    """Validate calculator's required_fields are valid"""
    invalid = set(calc.required_fields) - ALL_FIELDS
    if invalid:
        raise ValueError(f"Calculator '{calc.name}' has invalid fields: {invalid}")


# Auto-discover all calculators
ALL_CALCULATORS = discover_calculators(__file__)

# Validate fields
for calc in ALL_CALCULATORS:
    _validate_fields(calc)

# Build name -> calculator map
CALCULATOR_MAP = {calc.name: calc for calc in ALL_CALCULATORS}

__all__ = [
    "GrossProfitCalculator",
    "ImpliedGrowthCalculator",
    "InventoryTurnoverCalculator",
    "ALL_CALCULATORS",
    "CALCULATOR_MAP",
]
