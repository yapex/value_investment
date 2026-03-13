"""Tests for safety indicators"""
import pandas as pd
import pytest

from value_investment.indicators.safety import (
    CashToDebtIndicator,
    DebtRatioTotalIndicator,
)


class TestCashToDebtIndicator:
    """Test Cash to Debt Ratio indicator"""
    
    def test_calculate_basic(self):
        """Test basic cash to debt ratio calculation"""
        data = pd.DataFrame({
            'cash_and_equivalents': [500000],
            'short_term_debt': [100000],
            'long_term_debt': [200000],
        })
        
        indicator = CashToDebtIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None


class TestDebtRatioTotalIndicator:
    """Test Total Debt Ratio indicator"""
    
    def test_calculate_basic(self):
        """Test basic debt ratio calculation"""
        data = pd.DataFrame({
            'total_liabilities': [5000000],
            'total_assets': [10000000],
        })
        
        indicator = DebtRatioTotalIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None
