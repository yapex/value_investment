"""Tests for efficiency indicators"""
import pandas as pd
import pytest

from value_investment.indicators.efficiency import (
    FixedAssetTurnoverIndicator,
    AccountsReceivableRatioIndicator,
    ExpenseRatioIndicator,
    FeeRateIndicator,
)


class TestFixedAssetTurnoverIndicator:
    """Test Fixed Asset Turnover indicator"""
    
    def test_calculate_basic(self):
        """Test basic fixed asset turnover calculation"""
        data = pd.DataFrame({
            'revenue': [12000000],
            'fixed_assets': [6000000],
        })
        
        indicator = FixedAssetTurnoverIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None


class TestAccountsReceivableRatioIndicator:
    """Test Accounts Receivable Ratio indicator"""
    
    def test_calculate_basic(self):
        """Test basic accounts receivable ratio calculation"""
        data = pd.DataFrame({
            'accounts_receivable': [1500000],
            'revenue': [12000000],
        })
        
        indicator = AccountsReceivableRatioIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None


class TestExpenseRatioIndicator:
    """Test Expense Ratio indicator"""
    
    def test_calculate_basic(self):
        """Test basic expense ratio calculation"""
        data = pd.DataFrame({
            'operating_cost': [8000000],
            'revenue': [12000000],
        })
        
        indicator = ExpenseRatioIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None


class TestFeeRateIndicator:
    """Test Fee Rate indicator"""
    
    def test_calculate_basic(self):
        """Test basic fee rate calculation"""
        data = pd.DataFrame({
            'fee_income': [500000],
            'operating_cost': [1000000],
        })
        
        indicator = FeeRateIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None
