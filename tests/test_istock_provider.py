import pytest
from typing import Protocol
from value_investment.core.interfaces import IStockProvider

def test_provider_implements_protocol():
    """AkshareProvider should implement IStockProvider"""
    from value_investment.data.providers.akshare_provider import AkshareProvider

    # Check that provider has all required methods
    required_methods = [
        'get_stock_info',
        'get_quarterly_indicator',
        'get_historical_data',
        'get_balance_sheet',
        'get_profit_sheet',
        'get_cashflow_sheet',
    ]

    for method in required_methods:
        assert hasattr(AkshareProvider, method), f"Missing method: {method}"
