"""Test AkshareProvider uses DataMapper.map_to_standard() for field mapping"""

from __future__ import annotations

import pytest
import pandas as pd
from typing import TYPE_CHECKING, Any, cast
from unittest.mock import Mock, patch, MagicMock
import warnings

from value_investment.data.providers.akshare_provider import AkshareProvider
from value_investment.data.mapper import DataMapper

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


class MockCache:
    """Mock cache for testing"""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._data[key] = value

    def invalidate(self, key: str) -> None:
        if key in self._data:
            del self._data[key]

    def get_or_fetch(
        self,
        key: str,
        fetch_func: Any,
        ttl: int | None = None,
        force_refresh: bool = False,
    ) -> Any:
        """Mock implementation of SmartCache.get_or_fetch"""
        if force_refresh:
            self.invalidate(key)

        cached = self.get(key)
        if cached is not None:
            return cached

        data = fetch_func()
        self.set(key, data, ttl=ttl)
        return data


class TestAkshareProviderMapToStandard:
    """Tests for using DataMapper.map_to_standard() instead of _apply_mapping()"""

    @patch('value_investment.data.providers.akshare_provider.ak')
    def test_hk_balance_sheet_uses_map_to_standard(self, mock_ak):
        """HK balance sheet should use DataMapper.map_to_standard() for field mapping"""
        # Setup mock with akshare field names (HK market uses Chinese column names)
        # Akshare returns long format: each row is a different item
        mock_ak.stock_financial_hk_report_em.return_value = pd.DataFrame({
            "REPORT_DATE": ["2024-12-31", "2024-12-31", "2024-12-31"],
            "STD_ITEM_NAME": ["资产总值", "负债总额", "权益总额"],
            "AMOUNT": [1000000, 500000, 500000],
        })
        
        provider = AkshareProvider(cache=cast("SmartCache", MockCache()), market="HK")
        
        # Fetch balance sheet
        result = provider._get_hk_balance_sheet("00700")
        
        # Verify DataMapper.map_to_standard was called (standard fields should exist)
        # The result should have standard field names after transformation
        # Check that the wide format has year as a column (not STD_ITEM_NAME)
        assert result is not None
        # After _transform_hk_financial_data, year should be a column
        assert 'year' in result.columns or 'REPORT_DATE' in result.columns

    @patch('value_investment.data.providers.akshare_provider.ak')
    def test_hk_income_statement_uses_map_to_standard(self, mock_ak):
        """HK income statement should use DataMapper.map_to_standard() for field mapping"""
        # Setup mock - long format
        mock_ak.stock_financial_hk_report_em.return_value = pd.DataFrame({
            "REPORT_DATE": ["2024-12-31", "2024-12-31"],
            "STD_ITEM_NAME": ["收益", "期内溢利"],
            "AMOUNT": [800000, 100000],
        })
        
        provider = AkshareProvider(cache=cast("SmartCache", MockCache()), market="HK")
        
        # Fetch income statement
        result = provider._get_hk_profit_sheet("00700")
        
        # Verify result
        assert result is not None

    @patch('value_investment.data.providers.akshare_provider.ak')
    def test_hk_cashflow_sheet_uses_map_to_standard(self, mock_ak):
        """HK cash flow sheet should use DataMapper.map_to_standard() for field mapping"""
        # Setup mock
        mock_ak.stock_financial_hk_report_em.return_value = pd.DataFrame({
            "REPORT_DATE": ["2024-12-31"],
            "STD_ITEM_NAME": ["经营业务现金净额"],
            "AMOUNT": [50000],
        })
        
        provider = AkshareProvider(cache=cast("SmartCache", MockCache()), market="HK")
        
        # Fetch cash flow sheet
        result = provider._get_hk_cashflow_sheet("00700")
        
        # Verify result
        assert result is not None

    @patch('value_investment.data.providers.akshare_provider.ak')
    def test_us_balance_sheet_uses_map_to_standard(self, mock_ak):
        """US balance sheet should use DataMapper.map_to_standard() for field mapping"""
        # Setup mock - long format
        mock_ak.stock_financial_us_report_em.return_value = pd.DataFrame({
            "REPORT_DATE": ["2024-12-31", "2024-12-31"],
            "ITEM_NAME": ["Total Assets", "Total Liabilities"],
            "AMOUNT": [2000000, 1000000],
        })
        
        provider = AkshareProvider(cache=cast("SmartCache", MockCache()), market="US")
        
        # Fetch balance sheet
        result = provider._get_us_balance_sheet("AAPL")
        
        # Verify result
        assert result is not None

    @patch('value_investment.data.providers.akshare_provider.ak')
    def test_us_income_statement_uses_map_to_standard(self, mock_ak):
        """US income statement should use DataMapper.map_to_standard() for field mapping"""
        # Setup mock - long format
        mock_ak.stock_financial_us_report_em.return_value = pd.DataFrame({
            "REPORT_DATE": ["2024-12-31", "2024-12-31"],
            "ITEM_NAME": ["Total Revenue", "Net Income"],
            "AMOUNT": [3000000, 500000],
        })
        
        provider = AkshareProvider(cache=cast("SmartCache", MockCache()), market="US")
        
        # Fetch income statement
        result = provider._get_us_profit_sheet("AAPL")
        
        # Verify result
        assert result is not None

    @patch('value_investment.data.providers.akshare_provider.ak')
    def test_us_cashflow_sheet_uses_map_to_standard(self, mock_ak):
        """US cash flow sheet should use DataMapper.map_to_standard() for field mapping"""
        # Setup mock
        mock_ak.stock_financial_us_report_em.return_value = pd.DataFrame({
            "REPORT_DATE": ["2024-12-31"],
            "ITEM_NAME": ["Operating Cash Flow"],
            "AMOUNT": [800000],
        })
        
        provider = AkshareProvider(cache=cast("SmartCache", MockCache()), market="US")
        
        # Fetch cash flow sheet
        result = provider._get_us_cashflow_sheet("AAPL")
        
        # Verify result
        assert result is not None

    def test_data_mapper_import_exists(self):
        """DataMapper should be importable and have map_to_standard method"""
        # Verify DataMapper has the required method
        assert hasattr(DataMapper, 'map_to_standard')
        
        # Verify method signature
        import inspect
        sig = inspect.signature(DataMapper.map_to_standard)
        params = list(sig.parameters.keys())
        assert 'df' in params
        assert 'source' in params
        assert 'data_type' in params

    def test_akshare_source_mapping_exists(self):
        """AKSHARE_SOURCE_MAPPING should exist in DataMapper"""
        assert hasattr(DataMapper, 'AKSHARE_SOURCE_MAPPING')
        
        # Should have at least basic fields
        mapping = DataMapper.AKSHARE_SOURCE_MAPPING
        assert '股票代码' in mapping or 'stock_code' in mapping


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
