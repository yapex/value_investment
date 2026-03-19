"""Calculators for derived fields"""
from value_investment.domain.calculators.registry import (
    calculator,
    get_registered_calculators,
    instantiate_calculators,
    clear_registry,
)
from value_investment.domain.fields import ALL_FIELDS

# Explicit imports for IDE support
from value_investment.domain.calculators.gross_profit import GrossProfit
from value_investment.domain.calculators.implied_growth import ImpliedGrowth
from value_investment.domain.calculators.inventory_turnover import InventoryTurnover
from value_investment.domain.calculators.operating_profit_margin import OperatingProfitMargin


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
    "get_registered_calculators",
    "clear_registry",
    "validate_calculators",
]
