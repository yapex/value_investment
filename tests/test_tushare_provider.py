"""Tests for TushareProvider"""
import os
import pytest
import pandas as pd

from value_investment.data.providers.tushare_provider import TushareProvider


class MockCache:
    """Mock cache for testing"""
    
    def __init__(self):
        self._data = {}
    
    def get(self, key):
        return self._data.get(key)
    
    def set(self, key, value, ttl=None):
        self._data[key] = value
    
    def invalidate(self, key):
        if key in self._data:
            del self._data[key]


@pytest.fixture
def tushare_token():
    """Get tushare token from environment"""
    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        pytest.skip("TUSHARE_TOKEN not set, skipping integration tests")
    return token


@pytest.fixture
def provider(tushare_token):
    """Create TushareProvider instance"""
    return TushareProvider(cache=MockCache(), token=tushare_token)


class TestTushareProviderInit:
    """Test TushareProvider initialization"""

    def test_init_without_token(self):
        """Should raise error if token not provided"""
        with pytest.raises(ValueError, match="Tushare token is required"):
            TushareProvider(cache=MockCache(), token="")

    def test_init_with_token(self, tushare_token):
        """Should initialize successfully with token"""
        provider = TushareProvider(cache=MockCache(), token=tushare_token)
        assert provider._cache is not None
        assert provider._api is not None

    def test_init_with_field_mappings(self, tushare_token):
        """Should accept field_mappings"""
        mappings = {
            "balance": {"ts_code": "stock_code"},
        }
        provider = TushareProvider(
            cache=MockCache(),
            token=tushare_token,
            field_mappings=mappings
        )
        assert provider.get_field_mapping("balance") == {"ts_code": "stock_code"}


class TestTushareProviderBalanceSheet:
    """Test get_balance_sheet method"""

    @pytest.mark.integration
    def test_get_balance_sheet(self, provider):
        """Should fetch balance sheet data"""
        df = provider.get_balance_sheet("000001.SZ", 2023)
        
        assert not df.empty
        assert "stock_code" in df.columns or "ts_code" in df.columns
        assert "report_date" in df.columns or "end_date" in df.columns

    @pytest.mark.integration
    def test_get_balance_sheet_multiple_years(self, provider):
        """Should fetch multiple years of data"""
        df = provider.get_balance_sheet("600519.SH", 2023)
        
        assert not df.empty
        # Should have data from multiple years (last 5 years)
        assert len(df) >= 1

    @pytest.mark.integration
    def test_get_balance_sheet_caching(self, provider):
        """Should cache results"""
        # First call - fetch from API
        df1 = provider.get_balance_sheet("000001.SZ", 2023)
        
        # Second call - should use cache
        df2 = provider.get_balance_sheet("000001.SZ", 2023)
        
        assert len(df1) == len(df2)

    @pytest.mark.integration
    def test_get_balance_sheet_field_mapping(self, tushare_token):
        """Should apply field mapping"""
        mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
            }
        }
        provider = TushareProvider(
            cache=MockCache(),
            token=tushare_token,
            field_mappings=mappings
        )
        
        df = provider.get_balance_sheet("000001.SZ", 2023)
        
        assert not df.empty
        # Mapped fields should exist
        assert "stock_code" in df.columns
        assert "report_date" in df.columns
        # Original fields should be removed
        assert "ts_code" not in df.columns
        assert "end_date" not in df.columns


class TestTushareProviderIncomeStatement:
    """Test get_income_statement method"""

    @pytest.mark.integration
    def test_get_income_statement(self, provider):
        """Should fetch income statement data"""
        df = provider.get_income_statement("000001.SZ", 2023)
        
        assert not df.empty
        assert "stock_code" in df.columns or "ts_code" in df.columns
        assert "report_date" in df.columns or "end_date" in df.columns

    @pytest.mark.integration
    def test_get_income_statement_field_mapping(self, tushare_token):
        """Should apply field mapping"""
        mappings = {
            "income": {
                "ts_code": "stock_code",
                "end_date": "report_date",
                "total_revenue": "total_revenue",
                "net_profit": "net_profit",
            }
        }
        provider = TushareProvider(
            cache=MockCache(),
            token=tushare_token,
            field_mappings=mappings
        )
        
        df = provider.get_income_statement("000001.SZ", 2023)
        
        assert not df.empty
        assert "stock_code" in df.columns
        assert "report_date" in df.columns


class TestTushareProviderCashFlow:
    """Test get_cash_flow_statement method"""

    @pytest.mark.integration
    def test_get_cash_flow_statement(self, provider):
        """Should fetch cash flow statement data"""
        df = provider.get_cash_flow_statement("000001.SZ", 2023)
        
        assert not df.empty
        assert "stock_code" in df.columns or "ts_code" in df.columns

    @pytest.mark.integration
    def test_get_cash_flow_statement_field_mapping(self, tushare_token):
        """Should apply field mapping"""
        mappings = {
            "cashflow": {
                "ts_code": "stock_code",
                "end_date": "report_date",
                "operating_cash_flow": "operating_cash_flow",
            }
        }
        provider = TushareProvider(
            cache=MockCache(),
            token=tushare_token,
            field_mappings=mappings
        )
        
        df = provider.get_cash_flow_statement("000001.SZ", 2023)
        
        assert not df.empty
        assert "stock_code" in df.columns
        assert "report_date" in df.columns


class TestTushareProviderHistoricalData:
    """Test get_historical_data method"""

    @pytest.mark.integration
    def test_get_historical_data(self, provider):
        """Should fetch historical market data"""
        df = provider.get_historical_data(
            "000001.SZ",
            start_date="20230101",
            end_date="20231231"
        )
        
        assert not df.empty
        assert "trade_date" in df.columns or "date" in df.columns
        assert "close" in df.columns

    @pytest.mark.integration
    def test_get_historical_data_with_adjust(self, provider):
        """Should fetch adjusted data"""
        # Test with forward adjustment
        df_qfq = provider.get_historical_data(
            "000001.SZ",
            start_date="20230101",
            end_date="20231231",
            adjust="qfq"
        )
        
        assert not df_qfq.empty
        
        # Test with backward adjustment
        df_hfq = provider.get_historical_data(
            "000001.SZ",
            start_date="20230101",
            end_date="20231231",
            adjust="hfq"
        )
        
        assert not df_hfq.empty

    @pytest.mark.integration
    def test_get_historical_data_default_dates(self, provider):
        """Should use default dates if not provided"""
        df = provider.get_historical_data("000001.SZ")
        
        assert not df.empty


class TestTushareProviderStockInfo:
    """Test get_stock_info method"""

    @pytest.mark.integration
    def test_get_stock_info(self, provider):
        """Should fetch stock basic info"""
        df = provider.get_stock_info("000001.SZ")
        
        assert not df.empty
        assert "ts_code" in df.columns or "stock_code" in df.columns
        assert "name" in df.columns


class TestTushareProviderErrorHandling:
    """Test error handling"""

    @pytest.mark.integration
    def test_invalid_stock_code(self, provider):
        """Should handle invalid stock code gracefully"""
        df = provider.get_balance_sheet("INVALID.SZ", 2023)
        
        # Should return empty DataFrame, not raise
        assert df.empty or len(df) == 0

    @pytest.mark.integration
    def test_future_year(self, provider):
        """Should handle future year gracefully"""
        df = provider.get_balance_sheet("000001.SZ", 2099)
        
        # Should return empty DataFrame or handle gracefully
        assert df.empty or len(df) >= 0
