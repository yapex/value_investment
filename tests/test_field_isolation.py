"""Tests for field mapping in DataProvider"""
import pytest
import pandas as pd
from value_investment.core.dependencies import DataProvider, DependencyRegistry


class MockProviderWithFinancialData:
    """Mock provider that returns raw provider fields"""

    def get_quarterly_indicator(self, code):
        # Return raw provider fields (before mapping)
        return pd.DataFrame({
            '报告期': ['2024-12-31', '2024-09-30'],
            '净利润': [100.0, 80.0],
            'NETPROFIT': [100.0, 80.0],
        })

    def get_historical_data(self, code, *args, **kwargs):
        return pd.DataFrame({'date': [], 'close': []})

    def get_stock_info(self, code):
        return pd.DataFrame()

    def get_financial_indicator(self, code):
        # Return raw provider fields (before mapping)
        return pd.DataFrame({
            '报告期': ['2024-12-31'],
            '净利润': [100.0],
            '营业总收入': [500.0],
            '总市值(元)': [1000000.0],
            '总市值(港元)': [2000000.0],
        })


class MockProviderWithHKFinancialData:
    """Mock provider that returns HK raw provider fields"""

    def get_quarterly_indicator(self, code):
        return pd.DataFrame({
            '报告期': ['2024-12-31', '2024-09-30'],
            '股东应占溢利': [100.0, 80.0],
            'DATE_TYPE_CODE': ['Q4', 'Q3'],
        })

    def get_historical_data(self, code, *args, **kwargs):
        return pd.DataFrame({'date': [], 'close': []})

    def get_stock_info(self, code):
        return pd.DataFrame()

    def get_financial_indicator(self, code):
        return pd.DataFrame({
            '报告期': ['2024-12-31'],
            '净利润': [100.0],
            '营业总收入': [500.0],
            '总市值(港元)': [2000000.0],
        })


def test_data_provider_maps_financial_indicator_fields():
    """DataProvider should map financial_indicator fields to internal standard fields"""
    provider = MockProviderWithFinancialData()
    data_provider = DataProvider(provider, market='A')

    result = data_provider.get('financial_indicator', '600519')

    # After mapping, should have internal standard fields
    assert 'net_profit' in result.columns, "Should have mapped '净利润' to 'net_profit'"
    assert 'total_revenue' in result.columns, "Should have mapped '营业总收入' to 'total_revenue'"
    assert 'a_market_cap' in result.columns, "Should have mapped '总市值(元)' to 'a_market_cap'"


def test_data_provider_maps_quarterly_fields():
    """DataProvider should map quarterly fields to internal standard fields"""
    provider = MockProviderWithFinancialData()
    data_provider = DataProvider(provider, market='A')

    result = data_provider.get('quarterly', '600519')

    # After mapping, should have internal standard fields
    assert 'net_profit' in result.columns, "Should have mapped '净利润' to 'net_profit'"


def test_data_provider_hk_market_mapping():
    """DataProvider should apply HK-specific custom mappings"""
    provider = MockProviderWithHKFinancialData()
    data_provider = DataProvider(provider, market='HK')

    result = data_provider.get('financial_indicator', '00700')

    # HK should have hk_market_cap from 总市值(港元)
    assert 'hk_market_cap' in result.columns, "Should have mapped '总市值(港元)' to 'hk_market_cap' for HK"


def test_data_provider_no_original_fields():
    """DataProvider should NOT preserve original fields (strict mode)"""
    provider = MockProviderWithFinancialData()
    data_provider = DataProvider(provider, market='A')

    result = data_provider.get('financial_indicator', '600519')

    # Should NOT preserve original fields (strict mode)
    assert 'net_profit_original' not in result.columns, \
        "Should NOT preserve original provider fields in strict mode"
    assert '净利润' not in result.columns, \
        "Should NOT have raw provider fields in strict mode"


def test_dependency_registry_resolve_with_mapping():
    """DependencyRegistry should return mapped data"""
    provider = MockProviderWithFinancialData()
    data_provider = DataProvider(provider, market='A')
    registry = DependencyRegistry(data_provider)

    result = registry.resolve(['financial_indicator'], '600519')

    # Should have mapped fields
    assert 'financial_indicator' in result
    assert 'net_profit' in result['financial_indicator'].columns
