"""ROIC Calculator"""
from typing import Any

from value_investment.pipeline.fields import (
    OPERATING_PROFIT,
    TOTAL_ASSETS,
    CASH_AND_EQUIVALENTS,
    CURRENT_LIABILITIES,
)


class ROICCalculator:
    """ROIC (Return on Invested Capital) Calculator
    
    ROIC = Operating Profit / (Total Assets - Cash - Current Liabilities)
    = Operating Profit / Working Capital
    """

    required_fields = {
        OPERATING_PROFIT,
        TOTAL_ASSETS,
        CASH_AND_EQUIVALENTS,
        CURRENT_LIABILITIES,
    }

    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        """Calculate ROIC from results
        
        Args:
            results: {field: {year: value}}
            
        Returns:
            {year: roic_value}
        """
        operating_profit = results.get(OPERATING_PROFIT, {})
        total_assets = results.get(TOTAL_ASSETS, {})
        cash = results.get(CASH_AND_EQUIVALENTS, {})
        current_liabilities = results.get(CURRENT_LIABILITIES, {})

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
