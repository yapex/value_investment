import pytest
import pandas as pd
from unittest.mock import MagicMock


def test_base_provider_has_cache_and_market():
    """BaseProvider should have cache and market as init parameters"""
    from value_investment.data.providers.base_provider import BaseProvider
    mock_cache = MagicMock()
    # BaseProvider is abstract, but we can check the __init__ signature
    import inspect
    sig = inspect.signature(BaseProvider.__init__)
    params = list(sig.parameters.keys())
    assert 'cache' in params
    assert 'market' in params


def test_base_provider_abstract_methods():
    """BaseProvider should define abstract methods for market-specific implementations"""
    from value_investment.data.providers.base_provider import BaseProvider
    # Should have abstract methods for each data type
    import inspect
    methods = [m for m in dir(BaseProvider) if not m.startswith('_')]
    assert 'get_stock_info' in methods
    assert 'get_historical_data' in methods
    assert 'get_balance_sheet' in methods
    assert 'get_income_statement' in methods
    assert 'get_cash_flow_statement' in methods
