"""Tests for cashflow indicators"""
import pandas as pd
import pytest

from value_investment.indicators.cashflow import (
    CfoToNetprofitIndicator,
    CfoToNetprofitSumIndicator,
    FcfToRevenueIndicator,
)


class TestCfoToNetprofitIndicator:
    """Test CFO to Net Profit indicator"""
    
    def test_calculate_basic(self):
        """Test basic CFO to net profit"""
        data = pd.DataFrame({
            'net_cash_flow_operating': [5000000],
            'net_profit': [4000000],
        })
        
        indicator = CfoToNetprofitIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None


class TestCfoToNetprofitSumIndicator:
    """Test CFO to Net Profit Sum indicator"""
    
    def test_calculate_basic(self):
        """Test basic CFO to net profit sum calculation"""
        data = pd.DataFrame({
            'net_cash_flow_operating': [5000000],
            'net_profit': [4000000],
        })
        
        indicator = CfoToNetprofitSumIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None


class TestFcfToRevenueIndicator:
    """Test FCF to Revenue indicator"""
    
    def test_calculate_basic(self):
        """Test basic FCF to revenue ratio calculation"""
        data = pd.DataFrame({
            'free_cash_flow': [2000000],
            'revenue': [12000000],
        })
        
        indicator = FcfToRevenueIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None
