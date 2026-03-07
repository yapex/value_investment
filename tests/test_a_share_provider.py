import pytest  # type: ignore[import-untyped]
import pandas as pd
from unittest.mock import patch, MagicMock


def test_a_share_provider_initialization():
    """AShareProvider should initialize with cache"""
    from value_investment.data.providers.a_share_provider import AShareProvider
    mock_cache = MagicMock()
    provider = AShareProvider(cache=mock_cache)
    assert provider._cache is mock_cache
    assert hasattr(provider, "get_stock_info")
    assert hasattr(provider, "get_historical_data")


def test_a_share_provider_get_stock_info():
    """AShareProvider.get_stock_info should fetch A股 info"""
    from value_investment.data.providers.a_share_provider import AShareProvider
    mock_cache = MagicMock()
    mock_cache.get.return_value = None
    provider = AShareProvider(cache=mock_cache, market="A")
    
    mock_data = pd.DataFrame({"item": ["股票代码"], "value": ["600519"]})
    with patch("akshare.stock_individual_info_em", return_value=mock_data):
        result = provider.get_stock_info("600519")
    
    assert "item" in result.columns
