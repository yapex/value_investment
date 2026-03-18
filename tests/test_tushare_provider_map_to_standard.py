"""Test TushareProvider uses DataMapper.map_to_standard() for field mapping"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch

from value_investment.data.providers.tushare_provider import TushareProvider
from value_investment.data.mapper import DataMapper


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
            if isinstance(cached, dict) and "data" in cached:
                data = cached["data"]
            else:
                data = cached
            if date_column and isinstance(data, pd.DataFrame) and not data.empty:
                data = self._filter_by_date(data, date_column, start_date, end_date)
            return data

        data = fetch_func()
        if isinstance(data, pd.DataFrame) and not data.empty and end_date:
            self.set(key, {"data": data, "_cached_end_date": end_date}, ttl=ttl)
        else:
            self.set(key, data, ttl=ttl)
        if date_column and isinstance(data, pd.DataFrame) and not data.empty:
            data = self._filter_by_date(data, date_column, start_date, end_date)
        return data

    def _filter_by_date(self, df, date_column, start_date, end_date):
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


class TestTushareProviderMapToStandard:
    """Tests for using DataMapper.map_to_standard() instead of _apply_mapping()"""

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_balance_sheet_uses_map_to_standard(self, mock_ts):
        """Balance sheet should use DataMapper.map_to_standard() for field mapping"""
        # Setup mock
        mock_api = Mock()
        mock_ts.pro_api.return_value = mock_api
        
        # Mock API return with Tushare field names
        mock_api.balancesheet.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "ann_date": ["20240430"],
            "total_assets": [1000000],
            "total_liab": [500000],
            "total_hldr_eqy_excl_min_int_shares": [480000],
            "update_flag": ["1"],
        })
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        # Fetch balance sheet
        result = provider.get_balance_sheet("600519", 2023)
        
        # Verify standard field names are used
        assert "stock_code" in result.columns, f"Expected 'stock_code' but got {result.columns.tolist()}"
        assert "report_date" in result.columns, f"Expected 'report_date' but got {result.columns.tolist()}"
        assert "announce_date" in result.columns, f"Expected 'announce_date' but got {result.columns.tolist()}"
        
        # Verify original Tushare fields are NOT present
        assert "ts_code" not in result.columns, "ts_code should be mapped to stock_code"
        assert "end_date" not in result.columns, "end_date should be mapped to report_date"

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_income_statement_uses_map_to_standard(self, mock_ts):
        """Income statement should use DataMapper.map_to_standard() for field mapping"""
        mock_api = Mock()
        mock_ts.pro_api.return_value = mock_api
        
        mock_api.income.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "ann_date": ["20240430"],
            "total_operate_income": [1200000],
            "netprofit": [400000],
            "update_flag": ["1"],
        })
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        result = provider.get_income_statement("600519", 2023)
        
        # Verify standard field names
        assert "stock_code" in result.columns
        assert "report_date" in result.columns
        
        # Income statement specific fields
        assert "total_revenue" in result.columns or "operating_income" in result.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cash_flow_uses_map_to_standard(self, mock_ts):
        """Cash flow statement should use DataMapper.map_to_standard() for field mapping"""
        mock_api = Mock()
        mock_ts.pro_api.return_value = mock_api
        
        mock_api.cashflow.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "ann_date": ["20240430"],
            "netcash_operate": [500000],
            "netcash_invest": [-200000],
            "netcash_finance": [-100000],
            "update_flag": ["1"],
        })
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        result = provider.get_cash_flow_statement("600519", 2023)
        
        # Verify standard field names
        assert "stock_code" in result.columns
        assert "report_date" in result.columns
        assert "operating_cash_flow" in result.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_map_to_standard_handles_none(self, mock_ts):
        """map_to_standard should handle None input gracefully"""
        mock_api = Mock()
        mock_ts.pro_api.return_value = mock_api
        
        # Return empty DataFrame
        mock_api.balancesheet.return_value = pd.DataFrame()
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        result = provider.get_balance_sheet("600519", 2023)
        
        # Should return empty DataFrame, not raise error
        assert isinstance(result, pd.DataFrame)

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_balance_sheet_mapping_completeness(self, mock_ts):
        """Verify balance sheet mapping maps all key fields correctly"""
        mock_api = Mock()
        mock_ts.pro_api.return_value = mock_api
        
        mock_api.balancesheet.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "ann_date": ["20240430"],
            "TOTAL_ASSETS": [1000000],
            "total_liab": [500000],
            "total_hldr_eqy_excl_min_int_shares": [480000],
            "monetaryfunds": [100000],
            "accounts_rece": [50000],
            "inventory": [30000],
            "fixed_assets": [200000],
            "update_flag": ["1"],
        })
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        result = provider.get_balance_sheet("600519", 2023)
        
        # Key balance sheet fields should be mapped
        assert "total_assets" in result.columns
        assert "total_liabilities" in result.columns  # from total_liab mapping
        # Note: total_equity mapping depends on the field name in Tushare API

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_income_statement_mapping_completeness(self, mock_ts):
        """Verify income statement mapping maps all key fields correctly"""
        mock_api = Mock()
        mock_ts.pro_api.return_value = mock_api
        
        mock_api.income.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "ann_date": ["20240430"],
            "total_operate_income": [1200000],
            "operate_income": [1150000],
            "operate_cost": [800000],
            "operate_profit": [350000],
            "netprofit": [400000],
            "update_flag": ["1"],
        })
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        result = provider.get_income_statement("600519", 2023)
        
        # Key income statement fields should be mapped
        assert "total_revenue" in result.columns  # from total_operate_income
        assert "operating_income" in result.columns  # from operate_income
        assert "operating_cost" in result.columns  # from operate_cost
        assert "net_profit" in result.columns  # from netprofit

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cash_flow_mapping_completeness(self, mock_ts):
        """Verify cash flow mapping maps all key fields correctly"""
        mock_api = Mock()
        mock_ts.pro_api.return_value = mock_api
        
        mock_api.cashflow.return_value = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "end_date": ["20231231"],
            "ann_date": ["20240430"],
            "netcash_operate": [500000],
            "netcash_invest": [-200000],
            "netcash_finance": [-100000],
            "construct_long_asset": [50000],
            "update_flag": ["1"],
        })
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        result = provider.get_cash_flow_statement("600519", 2023)
        
        # Key cash flow fields should be mapped
        assert "operating_cash_flow" in result.columns  # from netcash_operate
        assert "investing_cash_flow" in result.columns  # from netcash_invest
        assert "financing_cash_flow" in result.columns  # from netcash_finance
        assert "capital_expenditure" in result.columns  # from construct_long_asset
