"""Unit tests for TushareProvider (no API token required)"""
import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock, patch

from value_investment.data.providers.tushare_provider import TushareProvider


class MockCache:
    """Mock cache for testing"""
    
    def __init__(self):
        self._data = {}
        self.get_call_count = 0
        self.set_call_count = 0
    
    def get(self, key):
        self.get_call_count += 1
        return self._data.get(key)
    
    def set(self, key, value, ttl=None):
        self.set_call_count += 1
        self._data[key] = value
    
    def invalidate(self, key):
        if key in self._data:
            del self._data[key]


class TestTushareProviderUnit:
    """Unit tests without API calls"""

    def test_init_without_token_raises(self):
        """Should raise error if token not provided"""
        with pytest.raises(ValueError, match="Tushare token is required"):
            TushareProvider(cache=MockCache(), token="")

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_init_with_token(self, mock_ts):
        """Should initialize with token"""
        mock_api = Mock()
        mock_ts.pro_api.return_value = mock_api
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        mock_ts.set_token.assert_called_once_with("test_token")
        mock_ts.pro_api.assert_called_once()
        assert provider._api == mock_api

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_field_mapping_stored(self, mock_ts):
        """Should store field mappings"""
        mock_ts.pro_api.return_value = Mock()
        
        mappings = {
            "balance": {"ts_code": "stock_code"},
            "income": {"total_revenue": "total_revenue"},
        }
        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings=mappings
        )
        
        assert provider.get_field_mapping("balance") == {"ts_code": "stock_code"}
        assert provider.get_field_mapping("income") == {"total_revenue": "total_revenue"}
        assert provider.get_field_mapping("unknown") == {}

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_apply_mapping_integration(self, mock_ts):
        """Should apply field mapping to data"""
        mock_ts.pro_api.return_value = Mock()
        
        mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
                "total_assets": "total_assets",
            }
        }
        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings=mappings
        )
        
        # Create mock data
        df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "end_date": ["2023-12-31"],
            "total_assets": [1000],
            "other_field": [999],
        })
        
        result = provider._apply_mapping(df, "balance")
        assert result is not None
        
        # Check mapping applied
        assert "stock_code" in result.columns
        assert "report_date" in result.columns
        assert "total_assets" in result.columns
        assert "other_field" in result.columns  # Unmapped fields kept
        assert "ts_code" not in result.columns
        assert "end_date" not in result.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cache_key_generation(self, mock_ts):
        """Should generate cache keys correctly"""
        mock_ts.pro_api.return_value = Mock()
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        key1 = provider._get_cache_key("balance", "000001.SZ", "2023")
        assert key1 == "balance:000001.SZ:2023"
        
        key2 = provider._get_cache_key("income", "600519.SH", "2023")
        assert key2 == "income:600519.SH:2023"

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cache_integration(self, mock_ts):
        """Should use cache"""
        mock_ts.pro_api.return_value = Mock()
        cache = MockCache()
        provider = TushareProvider(cache=cache, token="test_token")
        
        # Store in cache
        cache.set("test_key", pd.DataFrame({"data": [1]}))
        
        # Retrieve from cache
        result = provider._get_from_cache("test_key")
        assert result is not None
        assert len(result) == 1
        
        # Cache get was called
        assert cache.get_call_count == 1

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cache_set(self, mock_ts):
        """Should set cache"""
        mock_ts.pro_api.return_value = Mock()
        cache = MockCache()
        provider = TushareProvider(cache=cache, token="test_token")
        
        df = pd.DataFrame({"data": [1, 2, 3]})
        provider._set_to_cache("my_key", df)
        
        assert cache.set_call_count == 1
        assert "my_key" in cache._data

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_get_balance_sheet_with_mock(self, mock_ts):
        """Should fetch and map balance sheet data"""
        # Mock API response
        mock_api = Mock()
        mock_df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "end_date": ["2023-12-31"],
            "total_assets": [1000],
        })
        mock_api.balancesheet.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api
        
        mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
            }
        }
        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings=mappings
        )
        
        df = provider.get_balance_sheet("000001.SZ", 2023)
        
        # Verify API was called
        mock_api.balancesheet.assert_called_once()
        
        # Verify mapping applied
        assert "stock_code" in df.columns
        assert "report_date" in df.columns
        assert "ts_code" not in df.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_get_income_statement_with_mock(self, mock_ts):
        """Should fetch and map income statement data"""
        mock_api = Mock()
        mock_df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "end_date": ["2023-12-31"],
            "total_revenue": [1000],
            "net_profit": [100],
        })
        mock_api.income.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api
        
        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings={"income": {"ts_code": "stock_code"}}
        )
        
        df = provider.get_income_statement("000001.SZ", 2023)
        
        mock_api.income.assert_called_once()
        assert "stock_code" in df.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_get_cash_flow_with_mock(self, mock_ts):
        """Should fetch and map cash flow data"""
        mock_api = Mock()
        mock_df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "end_date": ["2023-12-31"],
            "operating_cash_flow": [500],
        })
        mock_api.cashflow.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api
        
        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings={"cashflow": {"ts_code": "stock_code"}}
        )
        
        df = provider.get_cash_flow_statement("000001.SZ", 2023)
        
        mock_api.cashflow.assert_called_once()
        assert "stock_code" in df.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_get_historical_data_with_mock(self, mock_ts):
        """Should fetch and map historical data"""
        mock_api = Mock()
        mock_df = pd.DataFrame({
            "trade_date": ["20231231"],
            "close": [10.5],
            "open": [10.0],
            "vol": [1000],
        })
        mock_api.daily.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api
        
        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings={"market": {"close": "close"}}
        )
        
        df = provider.get_historical_data(
            "000001.SZ",
            start_date="20230101",
            end_date="20231231",
            adjust="qfq"
        )
        
        mock_api.daily.assert_called_once()
        # Verify adjust parameter
        call_args = mock_api.daily.call_args
        assert call_args[1]["adj"] == "qfq"

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_get_stock_info_with_mock(self, mock_ts):
        """Should fetch stock info"""
        mock_api = Mock()
        mock_df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "name": ["平安银行"],
            "area": ["深圳"],
        })
        mock_api.stock_basic.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        df = provider.get_stock_info("000001.SZ")
        
        mock_api.stock_basic.assert_called_once()
        assert "name" in df.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_empty_result_handling(self, mock_ts):
        """Should handle empty results"""
        mock_api = Mock()
        mock_api.balancesheet.return_value = pd.DataFrame()
        mock_ts.pro_api.return_value = mock_api
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        df = provider.get_balance_sheet("INVALID.SZ", 2023)
        
        assert df.empty

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cache_hit(self, mock_ts):
        """Should use cached data on cache hit"""
        mock_api = Mock()
        mock_df = pd.DataFrame({"ts_code": ["000001.SZ"]})
        mock_api.balancesheet.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api
        
        cache = MockCache()
        provider = TushareProvider(cache=cache, token="test_token")
        
        # First call - cache miss
        df1 = provider.get_balance_sheet("000001.SZ", 2023)
        assert mock_api.balancesheet.call_count == 1
        
        # Second call - cache hit
        df2 = provider.get_balance_sheet("000001.SZ", 2023)
        # Should not call API again
        assert mock_api.balancesheet.call_count == 1
