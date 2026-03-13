"""Tests for growth indicators - more coverage"""
import pandas as pd
import pytest

from value_investment.indicators.growth import (
    ROICIndicator,
    CAGRIndicator,
    RevenueGrowthIndicator,
    OperatingProfitGrowthIndicator,
    NetAssetGrowthIndicator,
    TotalAssetGrowthIndicator,
)


class TestROICIndicator:
    """Test ROIC (Return on Invested Capital) indicator"""
    
    def test_calculate_basic(self):
        """Test basic ROIC calculation"""
        data = pd.DataFrame({
            'net_profit': [1000000, 1200000],
            'total_shareholder_equity': [5000000, 6000000],
            'short_term_borrowings': [500000, 600000],
            'long_term_borrowings': [300000, 400000],
        })
        
        indicator = ROICIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None
        assert isinstance(result.value, (int, float))
    
    def test_calculate_with_tax_rate(self):
        """Test ROIC calculation with custom tax rate"""
        data = pd.DataFrame({
            'net_profit': [1000000],
            'total_shareholder_equity': [5000000],
            'short_term_borrowings': [500000],
            'long_term_borrowings': [300000],
        })
        
        indicator = ROICIndicator()
        result = indicator.calculate(data, tax_rate=0.25)
        
        assert result.value is not None
    
    def test_calculate_with_avg_invested(self):
        """Test ROIC calculation with average invested capital"""
        data = pd.DataFrame({
            'net_profit': [1000000, 1200000],
            'total_shareholder_equity': [5000000, 6000000],
            'short_term_borrowings': [500000, 600000],
            'long_term_borrowings': [300000, 400000],
        })
        
        indicator = ROICIndicator()
        result = indicator.calculate(data, use_avg_invested=True)
        
        assert result.value is not None


class TestCAGRIndicator:
    """Test CAGR (Compound Annual Growth Rate) indicator"""
    
    def test_calculate_basic(self):
        """Test basic CAGR calculation"""
        data = pd.DataFrame({
            'revenue': [100, 120, 144, 173],
            'year': [2021, 2022, 2023, 2024],
        })
        
        indicator = CAGRIndicator()
        result = indicator.calculate(data, field='revenue', periods=3)
        
        assert result.value is not None


class TestRevenueGrowthIndicator:
    """Test Revenue Growth indicator"""
    
    def test_calculate_basic(self):
        """Test basic revenue growth calculation"""
        data = pd.DataFrame({
            'revenue': [1000000, 1200000, 1500000],
            'year': [2022, 2023, 2024],
        })
        
        indicator = RevenueGrowthIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None


class TestOperatingProfitGrowthIndicator:
    """Test Operating Profit Growth indicator"""
    
    def test_calculate_basic(self):
        """Test basic operating profit growth calculation"""
        data = pd.DataFrame({
            'operating_profit': [500000, 600000, 750000],
            'year': [2022, 2023, 2024],
        })
        
        indicator = OperatingProfitGrowthIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None


class TestNetAssetGrowthIndicator:
    """Test Net Asset Growth indicator"""
    
    def test_calculate_basic(self):
        """Test basic net asset growth calculation"""
        data = pd.DataFrame({
            'total_shareholder_equity': [5000000, 6000000, 7200000],
            'year': [2022, 2023, 2024],
        })
        
        indicator = NetAssetGrowthIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None


class TestTotalAssetGrowthIndicator:
    """Test Total Asset Growth indicator"""
    
    def test_calculate_basic(self):
        """Test basic total asset growth calculation"""
        data = pd.DataFrame({
            'total_assets': [10000000, 12000000, 14400000],
            'year': [2022, 2023, 2024],
        })
        
        indicator = TotalAssetGrowthIndicator()
        result = indicator.calculate(data)
        
        assert result.value is not None
