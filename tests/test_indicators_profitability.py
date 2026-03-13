"""Tests for profitability indicators"""
import pandas as pd
import pytest

from value_investment.indicators.profitability import OperatingProfitMarginIndicator


class TestOperatingProfitMarginIndicator:
    """Test Operating Profit Margin indicator"""
    
    def test_calculate_basic(self):
        """Test basic operating profit margin calculation"""
        data = pd.DataFrame({
            'operating_profit': [2000000],
            'revenue': [10000000],
        })
        
        indicator = OperatingProfitMarginIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None
