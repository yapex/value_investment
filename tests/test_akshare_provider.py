"""Tests for AkshareProvider"""
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch


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
    
    def get_or_fetch_with_range(self, key, date_column, fetch_func, start_date, end_date, ttl, force_refresh):
        cached = self._data.get(key)
        if cached is not None and not force_refresh:
            return cached
        result = fetch_func()
        self._data[key] = result
        return result
    
    def get_or_fetch(self, key, fetch_func, ttl, force_refresh):
        cached = self._data.get(key)
        if cached is not None and not force_refresh:
            return cached
        result = fetch_func()
        self._data[key] = result
        return result


class TestAkshareProviderInit:
    """Test AkshareProvider initialization"""

    def test_init_default(self):
        """Should initialize with default market"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        provider = AkshareProvider(cache=MockCache())
        assert provider._market == "A"

    def test_init_with_market(self):
        """Should initialize with custom market"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        provider = AkshareProvider(cache=MockCache(), market="HK")
        assert provider._market == "HK"

    def test_init_with_field_mappings(self):
        """Should initialize with field mappings"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        mappings = {"balance": {"ts_code": "stock_code"}}
        provider = AkshareProvider(cache=MockCache(), field_mappings=mappings)
        
        assert provider.get_field_mapping("balance") == {"ts_code": "stock_code"}


class TestAkshareProviderNormalize:
    """Test code normalization"""

    def test_normalize_hk_code_5_digit(self):
        """Should normalize HK code to 5 digits"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        provider = AkshareProvider(cache=MockCache())
        
        assert provider._normalize_hk_code("700") == "00700"
        assert provider._normalize_hk_code("7") == "00007"
        assert provider._normalize_hk_code("00700") == "00700"
        assert provider._normalize_hk_code("09988") == "09988"

    def test_normalize_hk_code_empty(self):
        """Should handle empty string"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        provider = AkshareProvider(cache=MockCache())
        
        assert provider._normalize_hk_code("") == ""


class TestAkshareProviderDetect:
    """Test market detection"""

    def test_detect_a_share(self):
        """Should detect A股"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        provider = AkshareProvider(cache=MockCache())
        
        assert provider._detect_market("600519") == "A股"
        assert provider._detect_market("000001") == "A股"
        assert provider._detect_market("300750") == "A股"

    def test_detect_hk_share(self):
        """Should detect 港股"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        provider = AkshareProvider(cache=MockCache())
        
        assert provider._detect_market("00700") == "港股"
        assert provider._detect_market("09988") == "港股"

    def test_detect_us_share(self):
        """Should detect 美股"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        provider = AkshareProvider(cache=MockCache())
        
        assert provider._detect_market("AAPL") == "美股"
        assert provider._detect_market("TSLA") == "美股"

    def test_detect_invalid(self):
        """Should return None for invalid codes"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        provider = AkshareProvider(cache=MockCache())
        
        assert provider._detect_market("") is None
        assert provider._detect_market("123") is None


class TestAkshareProviderStockInfo:
    """Test get_stock_info method"""

    def test_get_stock_info_basic(self):
        """Should fetch stock info"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.akshare_provider.ak") as mock_ak:
            mock_ak.stock_individual_info_em.return_value = pd.DataFrame({
                "item": ["股票代码", "股票名称"],
                "value": ["600519", "贵州茅台"]
            })
            
            provider = AkshareProvider(cache=cache)
            result = provider.get_stock_info("600519")
            
            assert not result.empty

    def test_get_stock_info_with_cache(self):
        """Should use cache when available"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"item": ["code"], "value": ["600519"]})
        cache.set("info_600519", cached_data)
        
        with patch("value_investment.data.providers.akshare_provider.ak") as mock_ak:
            provider = AkshareProvider(cache=cache)
            result = provider.get_stock_info("600519")
            
            mock_ak.stock_individual_info_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_stock_info_force_refresh(self):
        """Should refresh when force_refresh=True"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"item": ["code"], "value": ["600519"]})
        cache.set("info_600519", cached_data)
        
        with patch("value_investment.data.providers.akshare_provider.ak") as mock_ak:
            mock_ak.stock_individual_info_em.return_value = pd.DataFrame({
                "item": ["股票代码"],
                "value": ["600519"]
            })
            
            provider = AkshareProvider(cache=cache)
            result = provider.get_stock_info("600519", force_refresh=True)
            
            mock_ak.stock_individual_info_em.assert_called_once()


class TestAkshareProviderHistoricalData:
    """Test get_historical_data method"""

    def test_get_historical_data_basic(self):
        """Should fetch historical data"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.akshare_provider.ak") as mock_ak:
            mock_ak.stock_zh_a_hist_tx.return_value = pd.DataFrame({
                "date": ["2024-01-01", "2024-01-02"],
                "open": [1500.0, 1550.0],
                "close": [1520.0, 1570.0],
                "high": [1550.0, 1600.0],
                "low": [1480.0, 1530.0],
                "amount": [1000000, 1100000]
            })
            
            provider = AkshareProvider(cache=cache)
            result = provider.get_historical_data("600519")
            
            assert not result.empty

    def test_get_historical_data_with_dates(self):
        """Should filter by date range"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.akshare_provider.ak") as mock_ak:
            mock_ak.stock_zh_a_hist_tx.return_value = pd.DataFrame({
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "open": [1500.0, 1550.0, 1600.0],
                "close": [1520.0, 1570.0, 1620.0],
                "high": [1550.0, 1600.0, 1650.0],
                "low": [1480.0, 1530.0, 1580.0],
                "amount": [1000000, 1100000, 1200000]
            })
            
            provider = AkshareProvider(cache=cache)
            result = provider.get_historical_data(
                "600519",
                start_date="20240101",
                end_date="20240102"
            )
            
            assert not result.empty


class TestAkshareProviderCache:
    """Test cache functionality"""

    def test_get_balance_sheet_uses_cache(self):
        """Should use cache for balance sheet"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"REPORT": ["2023-12-31"], "total_assets": [100]})
        cache.set("balance_sheet_a_600519", cached_data)
        
        with patch("value_investment.data.providers.akshare_provider.ak") as mock_ak:
            provider = AkshareProvider(cache=cache)
            result = provider.get_balance_sheet("600519", 2023)
            
            mock_ak.stock_balance_sheet_by_yearly_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_income_statement_uses_cache(self):
        """Should use cache for income statement"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"REPORT": ["2023-12-31"], "net_profit": [100]})
        cache.set("profit_sheet_a_600519", cached_data)
        
        with patch("value_investment.data.providers.akshare_provider.ak") as mock_ak:
            provider = AkshareProvider(cache=cache)
            result = provider.get_income_statement("600519", 2023)
            
            mock_ak.stock_profit_sheet_by_yearly_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_cash_flow_statement_uses_cache(self):
        """Should use cache for cash flow statement"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"REPORT": ["2023-12-31"], "operating_cash_flow": [100]})
        cache.set("cashflow_sheet_a_600519", cached_data)
        
        with patch("value_investment.data.providers.akshare_provider.ak") as mock_ak:
            provider = AkshareProvider(cache=cache)
            result = provider.get_cash_flow_statement("600519", 2023)
            
            mock_ak.stock_cash_flow_sheet_by_yearly_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_balance_sheet_force_refresh(self):
        """Should refresh when force_refresh=True"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"REPORT": ["2023-12-31"], "total_assets": [100]})
        cache.set("balance_sheet_a_600519", cached_data)
        
        with patch("value_investment.data.providers.akshare_provider.ak") as mock_ak:
            mock_ak.stock_balance_sheet_by_yearly_em.return_value = pd.DataFrame({
                "REPORT": ["2023-12-31"],
                "total_assets": [200]
            })
            
            provider = AkshareProvider(cache=cache)
            result = provider.get_balance_sheet("600519", 2023, force_refresh=True)
            
            mock_ak.stock_balance_sheet_by_yearly_em.assert_called_once()

    def test_get_historical_data_uses_cache(self):
        """Should use cache for historical data"""
        from value_investment.data.providers.akshare_provider import AkshareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"日期": ["2024-01-01"], "收盘": [150]})
        cache.set("hist_600519_hfq", cached_data)
        
        with patch("value_investment.data.providers.akshare_provider.ak") as mock_ak:
            provider = AkshareProvider(cache=cache)
            result = provider.get_historical_data("600519")
            
            mock_ak.stock_zh_a_hist_tx.assert_not_called()
            assert result.equals(cached_data)
