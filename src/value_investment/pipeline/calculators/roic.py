"""ROIC Calculator"""
from typing import Any

from value_investment.pipeline.fields.registry import get_registry


class ROICCalculator:
    """ROIC (Return on Invested Capital) Calculator
    
    ROIC = Operating Profit / (Total Assets - Cash - Current Liabilities)
    = Operating Profit / Working Capital
    
    Dependencies are declared in the Field Registry, not hardcoded.
    """

    name = "roic"

    @property
    def required_fields(self) -> set[str]:
        """Get required fields from Field Registry"""
        registry = get_registry()
        return set(registry.get_dependencies(self.name))

    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        """Calculate ROIC from results
        
        Args:
            results: {field: {year: value}}
            
        Returns:
            {year: roic_value}
        """
        # Get fields from registry
        registry = get_registry()
        deps = registry.get_dependencies(self.name)
        
        # Build results dict with defaults
        operating_profit = results.get(deps[0], {})  # operating_profit
        total_assets = results.get(deps[1], {})     # total_assets
        cash = results.get(deps[2], {})             # cash_and_equivalents
        current_liabilities = results.get(deps[3], {})  # current_liabilities

        roic = {}
        for year in operating_profit:
            invested_capital = (
                total_assets.get(year, 0)
                - cash.get(year, 0)
                - current_liabilities.get(year, 0)
            )
            if invested_capital != 0:
                roic[year] = operating_profit[year] / invested_capital
            else:
                roic[year] = 0.0

        return roic
