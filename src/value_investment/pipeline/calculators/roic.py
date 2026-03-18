"""ROIC Calculator"""
from typing import Any


class ROICCalculator:
    """ROIC (Return on Invested Capital) Calculator
    
    ROIC = EBIT / (Total Assets - Cash - Current Liabilities)
    = EBIT / Working Capital
    """

    name = "roic"

    @property
    def required_fields(self) -> set[str]:
        return {"ebit", "total_assets", "cash", "current_liabilities"}

    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        """Calculate ROIC from results
        
        Args:
            results: {field: {year: value}}
            
        Returns:
            {year: roic_value}
        """
        ebit = results.get("ebit", {})
        total_assets = results.get("total_assets", {})
        cash = results.get("cash", {})
        current_liabilities = results.get("current_liabilities", {})

        roic = {}
        for year in ebit:
            invested_capital = (
                total_assets.get(year, 0)
                - cash.get(year, 0)
                - current_liabilities.get(year, 0)
            )
            if invested_capital != 0:
                roic[year] = ebit[year] / invested_capital
            else:
                roic[year] = 0.0

        return roic
