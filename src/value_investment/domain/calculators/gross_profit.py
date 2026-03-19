"""Gross Profit Calculator"""
from typing import Any

from value_investment.domain.calculators import calculator
from value_investment.domain.fields import CustomFields, IFRSFields


@calculator
class GrossProfit:
    """Gross Profit Calculator
    
    Gross Profit = Total Revenue - Operating Cost
    """

    name = CustomFields.GROSS_PROFIT

    required_fields = {
        IFRSFields.TOTAL_REVENUE,
        IFRSFields.OPERATING_COST,
    }

    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        """Calculate gross profit from revenue and cost

        Args:
            results: {field: {year: value}}

        Returns:
            {year: gross_profit_value}
        """
        revenue = results.get(IFRSFields.TOTAL_REVENUE, {})
        cost = results.get(IFRSFields.OPERATING_COST, {})

        return {
            year: revenue.get(year, 0) - cost.get(year, 0)
            for year in revenue
        }
