"""Shared pytest fixtures for value_investment tests

This module provides:
- MockCache: Simple in-memory cache for testing
- Mock tushare API responses
- Fixtures that don't depend on external environment
"""
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch


class MockCache:
    """Mock cache for testing - simple in-memory implementation

    Supports SmartCache interface including get_or_fetch_with_range
    """

    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value, ttl=None):
        self._data[key] = value

    def invalidate(self, key):
        if key in self._data:
            del self._data[key]

    def clear(self):
        self._data.clear()

    def get_or_fetch_with_range(
        self,
        key,
        date_column,
        fetch_func,
        start_date=None,
        end_date=None,
        ttl=None,
        force_refresh=False,
    ):
        """Mock implementation of SmartCache.get_or_fetch_with_range"""
        if force_refresh:
            self.invalidate(key)

        cached = self.get(key)
        if cached is not None:
            # 模拟 SmartCache 的行为
            if isinstance(cached, dict) and "data" in cached:
                data = cached["data"]
            else:
                data = cached
            # 如果有日期过滤，应用过滤
            if date_column and isinstance(data, pd.DataFrame) and not data.empty:
                data = self._filter_by_date(data, date_column, start_date, end_date)
            return data

        # 缓存未命中，调用 fetch_func
        data = fetch_func()
        # 存储带元数据的缓存
        if isinstance(data, pd.DataFrame) and not data.empty and end_date:
            self.set(key, {"data": data, "_cached_end_date": end_date}, ttl=ttl)
        else:
            self.set(key, data, ttl=ttl)
        # 如果有日期过滤，应用过滤
        if date_column and isinstance(data, pd.DataFrame) and not data.empty:
            data = self._filter_by_date(data, date_column, start_date, end_date)
        return data

    def _filter_by_date(self, df, date_column, start_date, end_date):
        """模拟 SmartCache 的日期过滤"""
        if df.empty or date_column not in df.columns:
            return df
        df_copy = df.copy()
        df_copy["_date_temp"] = pd.to_datetime(df_copy[date_column])
        if start_date:
            start_dt = pd.to_datetime(start_date)
            df_copy = df_copy[df_copy["_date_temp"] >= start_dt]
        if end_date:
            end_dt = pd.to_datetime(end_date)
            df_copy = df_copy[df_copy["_date_temp"] <= end_dt]
        return df_copy.drop(columns=["_date_temp"])


@pytest.fixture
def mock_cache():
    """Provide a fresh MockCache instance"""
    return MockCache()


# Sample mock data for tushare API responses
MOCK_BALANCE_SHEET_DATA = pd.DataFrame({
    "ts_code": ["600519.SH", "600519.SH"],
    "end_date": ["20231231", "20221231"],
    "total_assets": [250000000000, 230000000000],
    "total_liab": [80000000000, 75000000000],
    "total_equity": [170000000000, 155000000000],
})

MOCK_INCOME_STATEMENT_DATA = pd.DataFrame({
    "ts_code": ["600519.SH", "600519.SH"],
    "end_date": ["20231231", "20221231"],
    "total_revenue": [150000000000, 140000000000],
    "net_profit": [70000000000, 65000000000],
    "basic_eps": [55.0, 51.0],
})

MOCK_CASH_FLOW_DATA = pd.DataFrame({
    "ts_code": ["600519.SH", "600519.SH"],
    "end_date": ["20231231", "20221231"],
    "net_cash_operate": [60000000000, 55000000000],
    "net_cash_invest": [-20000000000, -18000000000],
})

MOCK_HISTORICAL_DATA = pd.DataFrame({
    "ts_code": ["600519.SH"] * 5,
    "trade_date": ["20240101", "20240102", "20240103", "20240104", "20240105"],
    "open": [1700.0, 1710.0, 1720.0, 1715.0, 1725.0],
    "high": [1710.0, 1720.0, 1730.0, 1725.0, 1735.0],
    "low": [1690.0, 1700.0, 1710.0, 1705.0, 1715.0],
    "close": [1705.0, 1715.0, 1725.0, 1720.0, 1730.0],
    "vol": [1000000, 1100000, 1050000, 1080000, 1120000],
})

MOCK_STOCK_INFO_DATA = pd.DataFrame({
    "ts_code": ["600519.SH"],
    "name": ["贵州茅台"],
    "industry": ["白酒"],
    "list_date": ["20010827"],
})


@pytest.fixture
def mock_tushare_api():
    """Mock tushare pro_api with sample data"""
    with patch("value_investment.data.providers.tushare_provider.ts") as mock_ts:
        mock_api = MagicMock()
        mock_ts.pro_api.return_value = mock_api

        # Set up default responses
        mock_api.balancesheet.return_value = MOCK_BALANCE_SHEET_DATA
        mock_api.income.return_value = MOCK_INCOME_STATEMENT_DATA
        mock_api.cashflow.return_value = MOCK_CASH_FLOW_DATA
        mock_api.daily.return_value = MOCK_HISTORICAL_DATA
        mock_api.pro_bar.return_value = MOCK_HISTORICAL_DATA
        mock_api.stock_basic.return_value = MOCK_STOCK_INFO_DATA

        yield mock_api, mock_ts


@pytest.fixture
def mock_tushare_provider(mock_cache, mock_tushare_api):
    """Create TushareProvider with mocked API"""
    from value_investment.providers.a_share import TushareProvider

    mock_api, mock_ts = mock_tushare_api
    provider = TushareProvider(cache=mock_cache, token="mock_token_for_testing")
    return provider


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require real API access)"
    )
