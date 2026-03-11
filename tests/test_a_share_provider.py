"""Tests for AShareProvider"""
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


class TestAShareProviderInit:
    """Test AShareProvider initialization"""

    def test_init_default(self):
        """Should initialize with default market"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        provider = AShareProvider(cache=MockCache())
        assert provider._market == "A"

    def test_init_with_market(self):
        """Should initialize with custom market"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        provider = AShareProvider(cache=MockCache(), market="A")
        assert provider._market == "A"


class TestAShareProviderNormalize:
    """Test date normalization"""

    def test_normalize_date_8_digit(self):
        """Should normalize 8-digit date"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        provider = AShareProvider(cache=MockCache())
        
        assert provider._normalize_date("20240101") == "2024-01-01"
        assert provider._normalize_date("19991231") == "1999-12-31"

    def test_normalize_date_already_formatted(self):
        """Should handle already formatted date"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        provider = AShareProvider(cache=MockCache())
        
        assert provider._normalize_date("2024-01-01") == "2024-01-01"
        assert provider._normalize_date(None) is None


class TestAShareProviderSymbol:
    """Test symbol formatting"""

    def test_format_stock_symbol_with_prefix(self):
        """Should keep symbol with prefix"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        provider = AShareProvider(cache=MockCache())
        
        assert provider._format_stock_symbol("SH600519") == "SH600519"
        assert provider._format_stock_symbol("SZ000001") == "SZ000001"

    def test_format_stock_symbol_adding_prefix(self):
        """Should add prefix for 6-digit codes"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        provider = AShareProvider(cache=MockCache())
        
        # Shanghai stock (starts with 6)
        assert provider._format_stock_symbol("600519") == "SH600519"
        # Shenzhen stock (starts with 0 or 3)
        assert provider._format_stock_symbol("000001") == "SZ000001"
        assert provider._format_stock_symbol("300750") == "SZ300750"


class TestAShareProviderStockInfo:
    """Test get_stock_info method"""

    def test_get_stock_info_basic(self):
        """Should fetch stock info"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            mock_ak.stock_individual_info_em.return_value = pd.DataFrame({
                "item": ["股票代码", "股票名称"],
                "value": ["600519", "贵州茅台"]
            })
            
            provider = AShareProvider(cache=cache)
            result = provider.get_stock_info("600519")
            
            assert not result.empty

    def test_get_stock_info_with_cache(self):
        """Should use cache when available"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"item": ["code"], "value": ["600519"]})
        cache.set("info_600519", cached_data)
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            provider = AShareProvider(cache=cache)
            result = provider.get_stock_info("600519")
            
            mock_ak.stock_individual_info_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_stock_info_force_refresh(self):
        """Should refresh when force_refresh=True"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"item": ["code"], "value": ["600519"]})
        cache.set("info_600519", cached_data)
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            mock_ak.stock_individual_info_em.return_value = pd.DataFrame({
                "item": ["股票代码"],
                "value": ["600519"]
            })
            
            provider = AShareProvider(cache=cache)
            result = provider.get_stock_info("600519", force_refresh=True)
            
            mock_ak.stock_individual_info_em.assert_called_once()


class TestAShareProviderHistoricalData:
    """Test get_historical_data method"""

    def test_get_historical_data_basic(self):
        """Should fetch historical data"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            mock_ak.stock_zh_a_hist_tx.return_value = pd.DataFrame({
                "date": ["2024-01-01", "2024-01-02"],
                "open": [1500.0, 1550.0],
                "close": [1520.0, 1570.0],
                "high": [1550.0, 1600.0],
                "low": [1480.0, 1530.0],
                "amount": [1000000, 1100000]
            })
            
            provider = AShareProvider(cache=cache)
            result = provider.get_historical_data("600519")
            
            assert not result.empty

    def test_get_historical_data_with_dates(self):
        """Should filter by date range"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            mock_ak.stock_zh_a_hist_tx.return_value = pd.DataFrame({
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "open": [1500.0, 1550.0, 1600.0],
                "close": [1520.0, 1570.0, 1620.0],
                "high": [1550.0, 1600.0, 1650.0],
                "low": [1480.0, 1530.0, 1580.0],
                "amount": [1000000, 1100000, 1200000]
            })
            
            provider = AShareProvider(cache=cache)
            result = provider.get_historical_data(
                "600519",
                start_date="20240101",
                end_date="20240102"
            )
            
            assert not result.empty


class TestAShareProviderFinancial:
    """Test financial data methods"""

    def test_get_balance_sheet_basic(self):
        """Should fetch balance sheet"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            mock_ak.stock_balance_sheet_by_yearly_em.return_value = pd.DataFrame({
                "REPORT": ["2023-12-31"],
                "total_assets": [250000000000]
            })
            
            provider = AShareProvider(cache=cache)
            result = provider.get_balance_sheet("600519", 2023)
            
            assert result is not None

    def test_get_income_statement_basic(self):
        """Should fetch income statement"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            mock_ak.stock_profit_sheet_by_yearly_em.return_value = pd.DataFrame({
                "REPORT": ["2023-12-31"],
                "net_profit": [70000000000]
            })
            
            provider = AShareProvider(cache=cache)
            result = provider.get_income_statement("600519", 2023)
            
            assert result is not None

    def test_get_cash_flow_statement_basic(self):
        """Should fetch cash flow statement"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            mock_ak.stock_cash_flow_sheet_by_yearly_em.return_value = pd.DataFrame({
                "REPORT": ["2023-12-31"],
                "operating_cash_flow": [60000000000]
            })
            
            provider = AShareProvider(cache=cache)
            result = provider.get_cash_flow_statement("600519", 2023)
            
            assert result is not None


class TestAShareProviderFilter:
    """Test year filtering"""

    def test_filter_by_year_basic(self):
        """Should filter by year"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        provider = AShareProvider(cache=MockCache())
        
        df = pd.DataFrame({
            "REPORT": ["2020-12-31", "2021-12-31", "2022-12-31", "2023-12-31"],
            "value": [100, 200, 300, 400]
        })
        
        result = provider._filter_by_year(df, 2022)
        
        assert len(result) == 3

    def test_filter_by_year_empty(self):
        """Should handle empty DataFrame"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        provider = AShareProvider(cache=MockCache())
        
        result = provider._filter_by_year(pd.DataFrame(), 2022)
        
        assert result.empty

    def test_filter_by_year_no_year_column(self):
        """Should handle DataFrame without year column"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        provider = AShareProvider(cache=MockCache())
        
        df = pd.DataFrame({"value": [100, 200]})
        
        result = provider._filter_by_year(df, 2022)
        
        assert result.equals(df)

    def test_filter_by_year_with_year_column(self):
        """Should filter by year using year column"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        provider = AShareProvider(cache=MockCache())
        
        df = pd.DataFrame({
            "year": [2020, 2021, 2022, 2023],
            "value": [100, 200, 300, 400]
        })
        
        result = provider._filter_by_year(df, 2022)
        
        assert len(result) == 3

    def test_filter_by_year_with_report_date_name(self):
        """Should filter by year using REPORT_DATE_NAME column"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        provider = AShareProvider(cache=MockCache())
        
        df = pd.DataFrame({
            "REPORT_DATE_NAME": ["2020年报", "2021年报", "2022年报", "2023年报"],
            "value": [100, 200, 300, 400]
        })
        
        result = provider._filter_by_year(df, 2022)
        
        assert len(result) == 3


class TestAShareProviderCache:
    """Test cache functionality"""

    def test_get_balance_sheet_uses_cache(self):
        """Should use cache for balance sheet"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"REPORT": ["2023-12-31"], "total_assets": [100]})
        cache.set("balance_sheet_a_600519", cached_data)
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            provider = AShareProvider(cache=cache)
            result = provider.get_balance_sheet("600519", 2023)
            
            mock_ak.stock_balance_sheet_by_yearly_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_income_statement_uses_cache(self):
        """Should use cache for income statement"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"REPORT": ["2023-12-31"], "net_profit": [100]})
        cache.set("profit_sheet_a_600519", cached_data)
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            provider = AShareProvider(cache=cache)
            result = provider.get_income_statement("600519", 2023)
            
            mock_ak.stock_profit_sheet_by_yearly_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_cash_flow_statement_uses_cache(self):
        """Should use cache for cash flow statement"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"REPORT": ["2023-12-31"], "operating_cash_flow": [100]})
        cache.set("cashflow_sheet_a_600519", cached_data)
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            provider = AShareProvider(cache=cache)
            result = provider.get_cash_flow_statement("600519", 2023)
            
            mock_ak.stock_cash_flow_sheet_by_yearly_em.assert_not_called()
            assert result.equals(cached_data)

    def test_get_balance_sheet_force_refresh(self):
        """Should refresh when force_refresh=True"""
        from value_investment.data.providers.a_share_provider import AShareProvider
        
        cache = MockCache()
        cached_data = pd.DataFrame({"REPORT": ["2023-12-31"], "total_assets": [100]})
        cache.set("balance_sheet_a_600519", cached_data)
        
        with patch("value_investment.data.providers.a_share_provider.ak") as mock_ak:
            mock_ak.stock_balance_sheet_by_yearly_em.return_value = pd.DataFrame({
                "REPORT": ["2023-12-31"],
                "total_assets": [200]
            })
            
            provider = AShareProvider(cache=cache)
            result = provider.get_balance_sheet("600519", 2023, force_refresh=True)
            
            mock_ak.stock_balance_sheet_by_yearly_em.assert_called_once()
