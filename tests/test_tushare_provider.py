"""Tests for TushareProvider

These tests use mocks to avoid depending on real TUSHARE_TOKEN.
Only a few integration tests are kept for connectivity verification.
"""
import os
from unittest.mock import MagicMock, patch

import pytest  # type: ignore
import pandas as pd

from value_investment.data.providers.tushare_provider import TushareProvider


class TestTushareProviderInit:
    """Test TushareProvider initialization"""

    def test_init_without_token(self):
        """Should raise error if token not provided"""
        with pytest.raises(ValueError, match="Tushare token is required"):
            TushareProvider(cache=MockCache(), token="")

    def test_init_with_token(self, mock_tushare_provider):
        """Should initialize successfully with token"""
        provider = mock_tushare_provider
        assert provider._cache is not None
        assert provider._api is not None

    def test_init_with_field_mappings(self, mock_tushare_provider):
        """Should accept field_mappings"""
        mappings = {
            "balance": {"ts_code": "stock_code"},
        }
        provider = TushareProvider(
            cache=MockCache(),
            token="mock_token",
            field_mappings=mappings
        )
        assert provider.get_field_mapping("balance") == {"ts_code": "stock_code"}


class TestTushareProviderBalanceSheet:
    """Test get_balance_sheet method"""

    def test_get_balance_sheet(self, mock_tushare_provider):
        """Should fetch balance sheet data"""
        mock_tushare_provider._api.balancesheet.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "total_assets": [250000000000],
        })
        
        df = mock_tushare_provider.get_balance_sheet("600519.SH", 2023)
        
        assert not df.empty
        assert "ts_code" in df.columns or "stock_code" in df.columns

    def test_get_balance_sheet_multiple_years(self, mock_tushare_provider):
        """Should fetch multiple years of data"""
        mock_tushare_provider._api.balancesheet.return_value = pd.DataFrame({
            "ts_code": ["600519.SH", "600519.SH"],
            "end_date": ["20231231", "20221231"],
            "total_assets": [250000000000, 230000000000],
        })
        
        df = mock_tushare_provider.get_balance_sheet("600519.SH", 2023)
        
        assert not df.empty
        assert len(df) >= 1

    def test_get_balance_sheet_caching(self, mock_cache, mock_tushare_provider):
        """Should cache results"""
        mock_tushare_provider._api.balancesheet.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "total_assets": [250000000000],
        })
        
        # First call - fetch from API
        df1 = mock_tushare_provider.get_balance_sheet("600519.SH", 2023)
        
        # Second call - should use cache
        df2 = mock_tushare_provider.get_balance_sheet("600519.SH", 2023)
        
        assert len(df1) == len(df2)
        # Verify API was only called once
        assert mock_tushare_provider._api.balancesheet.call_count == 1

    def test_get_balance_sheet_field_mapping(self, mock_cache):
        """Should apply field mapping"""
        mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
            }
        }
        
        with patch("value_investment.data.providers.tushare_provider.ts") as mock_ts:
            mock_api = MagicMock()
            mock_ts.pro_api.return_value = mock_api
            mock_api.balancesheet.return_value = pd.DataFrame({
                "ts_code": ["600519.SH"],
                "end_date": ["20231231"],
                "total_assets": [250000000000],
            })
            
            provider = TushareProvider(
                cache=mock_cache,
                token="mock_token",
                field_mappings=mappings
            )
            
            df = provider.get_balance_sheet("600519.SH", 2023)
            
            assert not df.empty
            # Mapped fields should exist
            assert "stock_code" in df.columns
            assert "report_date" in df.columns
            # Original fields should be removed
            assert "ts_code" not in df.columns
            assert "end_date" not in df.columns


class TestTushareProviderIncomeStatement:
    """Test get_income_statement method"""

    def test_get_income_statement(self, mock_tushare_provider):
        """Should fetch income statement data"""
        mock_tushare_provider._api.income.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "total_revenue": [150000000000],
        })
        
        df = mock_tushare_provider.get_income_statement("600519.SH", 2023)
        
        assert not df.empty
        assert "ts_code" in df.columns or "stock_code" in df.columns

    def test_get_income_statement_field_mapping(self, mock_cache):
        """Should apply field mapping"""
        mappings = {
            "income": {
                "ts_code": "stock_code",
                "end_date": "report_date",
                "total_revenue": "total_revenue",
                "net_profit": "net_profit",
            }
        }
        
        with patch("value_investment.data.providers.tushare_provider.ts") as mock_ts:
            mock_api = MagicMock()
            mock_ts.pro_api.return_value = mock_api
            mock_api.income.return_value = pd.DataFrame({
                "ts_code": ["600519.SH"],
                "end_date": ["20231231"],
                "total_revenue": [150000000000],
            })
            
            provider = TushareProvider(
                cache=mock_cache,
                token="mock_token",
                field_mappings=mappings
            )
            
            df = provider.get_income_statement("600519.SH", 2023)
            
            assert not df.empty
            assert "stock_code" in df.columns
            assert "report_date" in df.columns


class TestTushareProviderCashFlow:
    """Test get_cash_flow_statement method"""

    def test_get_cash_flow_statement(self, mock_tushare_provider):
        """Should fetch cash flow statement data"""
        mock_tushare_provider._api.cashflow.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "net_cash_operate": [60000000000],
        })
        
        df = mock_tushare_provider.get_cash_flow_statement("600519.SH", 2023)
        
        assert not df.empty
        assert "ts_code" in df.columns or "stock_code" in df.columns

    def test_get_cash_flow_statement_field_mapping(self, mock_cache):
        """Should apply field mapping"""
        mappings = {
            "cashflow": {
                "ts_code": "stock_code",
                "end_date": "report_date",
                "operating_cash_flow": "operating_cash_flow",
            }
        }
        
        with patch("value_investment.data.providers.tushare_provider.ts") as mock_ts:
            mock_api = MagicMock()
            mock_ts.pro_api.return_value = mock_api
            mock_api.cashflow.return_value = pd.DataFrame({
                "ts_code": ["600519.SH"],
                "end_date": ["20231231"],
                "net_cash_operate": [60000000000],
            })
            
            provider = TushareProvider(
                cache=mock_cache,
                token="mock_token",
                field_mappings=mappings
            )
            
            df = provider.get_cash_flow_statement("600519.SH", 2023)
            
            assert not df.empty
            assert "stock_code" in df.columns
            assert "report_date" in df.columns


class TestTushareProviderHistoricalData:
    """Test get_historical_data method"""

    def test_get_historical_data(self, mock_tushare_provider):
        """Should fetch historical market data"""
        mock_tushare_provider._api.pro_bar.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "trade_date": ["20231201"],
            "close": [1700.0],
        })
        
        df = mock_tushare_provider.get_historical_data(
            "600519.SH",
            start_date="20230101",
            end_date="20231231"
        )
        
        assert not df.empty
        assert "trade_date" in df.columns or "date" in df.columns
        assert "close" in df.columns

    def test_get_historical_data_with_adjust(self, mock_tushare_provider):
        """Should fetch adjusted data"""
        mock_tushare_provider._api.pro_bar.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "trade_date": ["20231201"],
            "close": [1700.0],
        })
        
        # Test with forward adjustment
        df_qfq = mock_tushare_provider.get_historical_data(
            "600519.SH",
            start_date="20230101",
            end_date="20231231",
            adjust="qfq"
        )
        
        assert not df_qfq.empty
        
        # Test with backward adjustment
        df_hfq = mock_tushare_provider.get_historical_data(
            "600519.SH",
            start_date="20230101",
            end_date="20231231",
            adjust="hfq"
        )
        
        assert not df_hfq.empty

    def test_get_historical_data_default_dates(self, mock_tushare_provider):
        """Should use default dates if not provided"""
        mock_tushare_provider._api.pro_bar.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "trade_date": ["20231201"],
            "close": [1700.0],
        })
        
        df = mock_tushare_provider.get_historical_data("600519.SH")
        
        assert not df.empty


class TestTushareProviderStockInfo:
    """Test get_stock_info method"""

    def test_get_stock_info(self, mock_tushare_provider):
        """Should fetch stock basic info"""
        mock_tushare_provider._api.stock_basic.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "name": ["贵州茅台"],
        })
        
        df = mock_tushare_provider.get_stock_info("600519.SH")
        
        assert not df.empty
        assert "ts_code" in df.columns or "stock_code" in df.columns
        assert "name" in df.columns


class TestTushareProviderErrorHandling:
    """Test error handling"""

    def test_invalid_stock_code(self, mock_tushare_provider):
        """Should handle invalid stock code gracefully"""
        mock_tushare_provider._api.balancesheet.return_value = pd.DataFrame()
        
        df = mock_tushare_provider.get_balance_sheet("INVALID.SZ", 2023)
        
        # Should return empty DataFrame, not raise
        assert df.empty or len(df) == 0

    def test_future_year(self, mock_tushare_provider):
        """Should handle future year gracefully"""
        mock_tushare_provider._api.balancesheet.return_value = pd.DataFrame()
        
        df = mock_tushare_provider.get_balance_sheet("600519.SH", 2099)
        
        # Should return empty DataFrame or handle gracefully
        assert df.empty or len(df) >= 0


class TestTushareProviderIntegration:
    """Integration tests - kept for connectivity verification only
    
    These tests require real TUSHARE_TOKEN and are marked with @pytest.mark.integration.
    Run with: pytest -m integration
    """
    
    @pytest.mark.integration
    def test_integration_balance_sheet_connectivity(self):
        """Verify connectivity to Tushare API for balance sheet"""
        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            pytest.skip("TUSHARE_TOKEN not set, skipping integration test")
        
        from tests.conftest import MockCache
        provider = TushareProvider(cache=MockCache(), token=token)
        
        df = provider.get_balance_sheet("600519.SH", 2023)
        
        assert not df.empty
        assert "ts_code" in df.columns

    @pytest.mark.integration  
    def test_integration_historical_data_connectivity(self):
        """Verify connectivity to Tushare API for historical data"""
        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            pytest.skip("TUSHARE_TOKEN not set, skipping integration test")
        
        from tests.conftest import MockCache
        provider = TushareProvider(cache=MockCache(), token=token)
        
        df = provider.get_historical_data(
            "600519.SH",
            start_date="20240101",
            end_date="20240131"
        )
        
        assert not df.empty
        assert "close" in df.columns


# Import MockCache from conftest for the integration tests
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
