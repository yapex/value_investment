import pytest
from value_investment.core.dependencies import DataProvider, DependencyRegistry

class MockProvider:
    def get_quarterly_indicator(self, code):
        return f"quarterly:{code}"

    def get_historical_data(self, code, *args, **kwargs):
        return f"prices:{code}"

    def get_stock_info(self, code):
        return f"info:{code}"

def test_data_provider_get():
    provider = MockProvider()
    data_provider = DataProvider(provider)

    result = data_provider.get('quarterly', '600519')
    assert result == "quarterly:600519"

def test_dependency_registry_resolve():
    provider = MockProvider()
    data_provider = DataProvider(provider)
    registry = DependencyRegistry(data_provider)

    result = registry.resolve(['quarterly', 'prices'], '600519')
    assert result['quarterly'] == "quarterly:600519"
    assert result['prices'] == "prices:600519"
