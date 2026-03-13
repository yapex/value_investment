"""Tests for calculated indicators"""
import pandas as pd
import pytest

from value_investment.indicators.calculated import (
    ROEIndicator,
    ROAIndicator,
    GrossMarginIndicator,
    NetProfitMarginIndicator,
    AssetTurnoverIndicator,
    TotalAssetsTurnoverIndicator,
    EquityMultiplierIndicator,
    OperatingCashFlowIndicator,
)


class TestROEIndicator:
    """Test ROE (Return on Equity) indicator"""
    
    def test_calculate_basic(self):
        """Test basic ROE calculation"""
        data = pd.DataFrame({
            'net_profit': [1000000],
            'total_shareholder_equity': [10000000],
        })
        
        indicator = ROEIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None
    
    def test_calculate_with_year(self):
        """Test ROE with year column"""
        data = pd.DataFrame({
            'net_profit': [1000000, 1200000],
            'total_shareholder_equity': [10000000, 12000000],
            'year': [2023, 2024],
        })
        
        indicator = ROEIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None


class TestROAIndicator:
    """Test ROA (Return on Assets) indicator"""
    
    def test_calculate_basic(self):
        """Test basic ROA calculation"""
        data = pd.DataFrame({
            'net_profit': [1000000],
            'total_assets': [20000000],
        })
        
        indicator = ROAIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None


class TestGrossMarginIndicator:
    """Test Gross Margin indicator"""
    
    def test_calculate_basic(self):
        """Test basic gross margin calculation"""
        data = pd.DataFrame({
            'gross_profit': [5000000],
            'revenue': [10000000],
        })
        
        indicator = GrossMarginIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None


class TestNetProfitMarginIndicator:
    """Test Net Profit Margin indicator"""
    
    def test_calculate_basic(self):
        """Test basic net profit margin calculation"""
        data = pd.DataFrame({
            'net_profit': [1000000],
            'revenue': [10000000],
        })
        
        indicator = NetProfitMarginIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None


class TestAssetTurnoverIndicator:
    """Test Asset Turnover indicator"""
    
    def test_calculate_basic(self):
        """Test basic asset turnover calculation"""
        data = pd.DataFrame({
            'revenue': [10000000],
            'total_assets': [20000000],
        })
        
        indicator = AssetTurnoverIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None


class TestTotalAssetsTurnoverIndicator:
    """Test Total Assets Turnover indicator"""
    
    def test_calculate_basic(self):
        """Test basic total assets turnover calculation"""
        data = pd.DataFrame({
            'revenue': [10000000],
            'total_assets': [20000000],
        })
        
        indicator = TotalAssetsTurnoverIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None


class TestEquityMultiplierIndicator:
    """Test Equity Multiplier indicator"""
    
    def test_calculate_basic(self):
        """Test basic equity multiplier calculation"""
        data = pd.DataFrame({
            'total_assets': [20000000],
            'total_shareholder_equity': [10000000],
        })
        
        indicator = EquityMultiplierIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None


class TestOperatingCashFlowIndicator:
    """Test Operating Cash Flow indicator"""
    
    def test_calculate_basic(self):
        """Test basic operating cash flow"""
        data = pd.DataFrame({
            'net_cash_flow_operating': [5000000],
        })
        
        indicator = OperatingCashFlowIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None
