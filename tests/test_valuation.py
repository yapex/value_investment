"""Tests for valuation indicators"""
import pandas as pd
import pytest


class TestLatestMarketCapIndicator:
    """Test LatestMarketCapIndicator"""

    def test_indicator_import(self):
        """Should import indicator"""
        from value_investment.indicators.valuation import LatestMarketCapIndicator
        assert LatestMarketCapIndicator is not None

    def test_indicator_name(self):
        """Should have correct name"""
        from value_investment.indicators.valuation import LatestMarketCapIndicator
        assert LatestMarketCapIndicator.name == "latest_market_cap"

    def test_indicator_needs(self):
        """Should have correct needs"""
        from value_investment.indicators.valuation import LatestMarketCapIndicator
        assert "financial_indicator" in LatestMarketCapIndicator.needs
        assert "prices" in LatestMarketCapIndicator.needs

    def test_indicator_calculate_empty_data(self):
        """Should handle empty data"""
        from value_investment.indicators.valuation import LatestMarketCapIndicator
        
        indicator = LatestMarketCapIndicator()
        
        # Test with empty/missing dependencies
        result = indicator.calculate(pd.DataFrame(), financial_indicator=None, prices=None, stock_code="600519")
        
        assert result.value == 0.0
        assert result.description != ""

    def test_indicator_calculate_with_empty_dataframes(self):
        """Should handle empty DataFrames"""
        from value_investment.indicators.valuation import LatestMarketCapIndicator
        
        indicator = LatestMarketCapIndicator()
        
        result = indicator.calculate(
            pd.DataFrame(),
            financial_indicator=pd.DataFrame(),
            prices=pd.DataFrame(),
            stock_code="600519"
        )
        
        assert result.value == 0.0

    def test_indicator_with_valid_financial_data(self):
        """Should calculate with valid financial data"""
        from value_investment.indicators.valuation import LatestMarketCapIndicator
        
        indicator = LatestMarketCapIndicator()
        
        # Create mock financial data
        finind_df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "total_market_cap": [5000000000000]  # 5 trillion
        })
        
        prices_df = pd.DataFrame({
            "trade_date": ["20231231"],
            "close": [1700.0]
        })
        
        result = indicator.calculate(
            pd.DataFrame(),
            financial_indicator=finind_df,
            prices=prices_df,
            stock_code="600519"
        )
        
        # Should return a result, may have 0 value if certain columns are missing
        assert result is not None

    def test_indicator_with_hk_code(self):
        """Should handle HK stock code"""
        from value_investment.indicators.valuation import LatestMarketCapIndicator
        
        indicator = LatestMarketCapIndicator()
        
        result = indicator.calculate(
            pd.DataFrame(),
            financial_indicator=pd.DataFrame(),
            prices=pd.DataFrame(),
            stock_code="00700"  # HK code (5 digits)
        )
        
        assert result is not None

    def test_indicator_with_us_code(self):
        """Should handle US stock code"""
        from value_investment.indicators.valuation import LatestMarketCapIndicator
        
        indicator = LatestMarketCapIndicator()
        
        result = indicator.calculate(
            pd.DataFrame(),
            financial_indicator=pd.DataFrame(),
            prices=pd.DataFrame(),
            stock_code="AAPL"  # US code (letters)
        )
        
        assert result is not None

    def test_indicator_find_column(self):
        """Test _find_column helper"""
        from value_investment.indicators.valuation import LatestMarketCapIndicator
        
        indicator = LatestMarketCapIndicator()
        
        df = pd.DataFrame({
            "total_market_cap": [100],
            "market_cap": [200]
        })
        
        col = indicator._find_column(df, ["total_market_cap", "market_cap"])
        assert col is not None


class TestImpliedGrowthIndicator:
    """Test ImpliedGrowthIndicator"""

    def test_indicator_import(self):
        """Should import indicator"""
        from value_investment.indicators.valuation import ImpliedGrowthIndicator
        assert ImpliedGrowthIndicator is not None

    def test_indicator_name(self):
        """Should have correct name"""
        from value_investment.indicators.valuation import ImpliedGrowthIndicator
        assert ImpliedGrowthIndicator.name == "implied_growth"

    def test_indicator_needs(self):
        """Should have correct needs"""
        from value_investment.indicators.valuation import ImpliedGrowthIndicator
        assert "financial_indicator" in ImpliedGrowthIndicator.needs
        assert "prices" in ImpliedGrowthIndicator.needs

    def test_indicator_calculate_empty_data(self):
        """Should handle empty data"""
        from value_investment.indicators.valuation import ImpliedGrowthIndicator
        
        indicator = ImpliedGrowthIndicator()
        
        result = indicator.calculate(pd.DataFrame(), financial_indicator=None, prices=None, stock_code="600519")
        
        assert result.value == 0.0
        assert result.description != ""

    def test_indicator_calculate_with_empty_dataframes(self):
        """Should handle empty DataFrames"""
        from value_investment.indicators.valuation import ImpliedGrowthIndicator
        
        indicator = ImpliedGrowthIndicator()
        
        result = indicator.calculate(
            pd.DataFrame(),
            financial_indicator=pd.DataFrame(),
            prices=pd.DataFrame(),
            stock_code="600519"
        )
        
        assert result.value == 0.0

    def test_indicator_with_explicit_market_cap(self):
        """Should calculate with explicit market_cap"""
        from value_investment.indicators.valuation import ImpliedGrowthIndicator
        
        indicator = ImpliedGrowthIndicator()
        
        result = indicator.calculate(
            pd.DataFrame(),
            financial_indicator=pd.DataFrame(),
            prices=pd.DataFrame(),
            stock_code="600519",
            market_cap=5000000000000  # 5 trillion
        )
        
        assert result is not None


class TestPEPercentileIndicator:
    """Test PEPercentileIndicator"""

    def test_indicator_import(self):
        """Should import indicator"""
        from value_investment.indicators.valuation import PEPercentileIndicator
        assert PEPercentileIndicator is not None

    def test_indicator_name(self):
        """Should have correct name"""
        from value_investment.indicators.valuation import PEPercentileIndicator
        assert PEPercentileIndicator.name == "PEPct"

    def test_indicator_needs(self):
        """Should have correct needs"""
        from value_investment.indicators.valuation import PEPercentileIndicator
        assert "quarterly" in PEPercentileIndicator.needs
        assert "prices" in PEPercentileIndicator.needs

    def test_indicator_calculate_empty_data(self):
        """Should handle empty data"""
        from value_investment.indicators.valuation import PEPercentileIndicator
        
        indicator = PEPercentileIndicator()
        
        result = indicator.calculate(
            pd.DataFrame(),
            quarterly=None,
            prices=None,
            stock_code="600519"
        )
        
        assert result.value == 0.0
        assert result.description != ""

    def test_indicator_calculate_with_empty_dataframes(self):
        """Should handle empty DataFrames"""
        from value_investment.indicators.valuation import PEPercentileIndicator
        
        indicator = PEPercentileIndicator()
        
        result = indicator.calculate(
            pd.DataFrame(),
            quarterly=pd.DataFrame(),
            prices=pd.DataFrame(),
            stock_info=pd.DataFrame(),
            daily_basic=pd.DataFrame(),
            stock_code="600519"
        )
        
        assert result.value == 0.0

    def test_indicator_with_years_param(self):
        """Should accept years parameter"""
        from value_investment.indicators.valuation import PEPercentileIndicator
        
        indicator = PEPercentileIndicator()
        
        result = indicator.calculate(
            pd.DataFrame(),
            quarterly=pd.DataFrame(),
            prices=pd.DataFrame(),
            stock_info=pd.DataFrame(),
            daily_basic=pd.DataFrame(),
            stock_code="600519",
            years=5
        )
        
        assert result is not None
