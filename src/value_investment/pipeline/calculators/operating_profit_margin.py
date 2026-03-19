"""Operating Profit Margin Calculator"""
from typing import Any

from value_investment.pipeline.calculators import calculator
from value_investment.pipeline.fields import IFRSFields


@calculator
class OperatingProfitMarginCalculator:
    """Operating Profit Margin Calculator
    
    Operating Profit Margin = Operating Profit / Total Revenue * 100
    
    营业利润率 = 营业利润 / 营业总收入 * 100%
    
    衡量企业营业利润占营业收入的比例，反映主营业务的盈利能力。
    """

    name = IFRSFields.OPERATING_PROFIT_MARGIN

    required_fields = {
        IFRSFields.OPERATING_PROFIT,  # 营业利润
        IFRSFields.TOTAL_REVENUE,     # 营业总收入
    }

    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        """Calculate operating profit margin
        
        Args:
            results: {field: {year: value}}
            
        Returns:
            {year: operating_profit_margin_percentage}
        """
        operating_profit = results.get(IFRSFields.OPERATING_PROFIT, {})
        revenue = results.get(IFRSFields.TOTAL_REVENUE, {})
        
        # Calculate margin for each year
        margin = {}
        for year in operating_profit:
            op = operating_profit.get(year, 0)
            rev = revenue.get(year, 0)
            
            # Avoid division by zero
            if rev > 0:
                margin[year] = (op / rev) * 100
        
        return margin
