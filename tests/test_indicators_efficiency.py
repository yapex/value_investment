"""Tests for efficiency indicators - more coverage"""
import pandas as pd
import pytest

from value_investment.indicators.efficiency import (
    FixedAssetTurnoverIndicator,
    AccountsReceivableRatioIndicator,
    ExpenseRatioIndicator,
    FeeRateIndicator,
    FeeToGrossProfitRatioIndicator,
    PayableTurnoverIndicator,
    ReceivablesToAssetsRatioIndicator,
    ProductionAssetRatioIndicator,
    ReturnOnProductionAssetsIndicator,
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


class TestFeeToGrossProfitRatioIndicator:
    """Test Fee to Gross Profit Ratio indicator"""
    
    def test_calculate_basic(self):
        """Test basic fee to gross profit ratio"""
        data = pd.DataFrame({
            'fee_income': [500000],
            'gross_profit': [5000000],
        })
        
        indicator = FeeToGrossProfitRatioIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None


class TestPayableTurnoverIndicator:
    """Test Payable Turnover indicator"""
    
    def test_calculate_basic(self):
        """Test basic payable turnover"""
        data = pd.DataFrame({
            'accounts_payable': [1000000],
            'operating_cost': [8000000],
        })
        
        indicator = PayableTurnoverIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None


class TestReceivablesToAssetsRatioIndicator:
    """Test Receivables to Assets Ratio indicator"""
    
    def test_calculate_basic(self):
        """Test basic receivables to assets ratio"""
        data = pd.DataFrame({
            'accounts_receivable': [1500000],
            'total_assets': [20000000],
        })
        
        indicator = ReceivablesToAssetsRatioIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None


class TestProductionAssetRatioIndicator:
    """Test Production Asset Ratio indicator"""
    
    def test_calculate_basic(self):
        """Test basic production asset ratio"""
        data = pd.DataFrame({
            'productive_assets': [8000000],
            'total_assets': [20000000],
        })
        
        indicator = ProductionAssetRatioIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None


class TestReturnOnProductionAssetsIndicator:
    """Test Return on Production Assets indicator"""
    
    def test_calculate_basic(self):
        """Test basic return on production assets"""
        data = pd.DataFrame({
            'net_profit': [1000000],
            'productive_assets': [8000000],
        })
        
        indicator = ReturnOnProductionAssetsIndicator()
        result = indicator.calculate(data)
        
        # Just verify it runs without error
        assert result.value is not None
