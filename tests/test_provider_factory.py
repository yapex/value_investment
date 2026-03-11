import pytest
from unittest.mock import MagicMock


def test_provider_factory_returns_ashare_for_market_a():
    """ProviderFactory should return AShareProvider for market='A'"""
    from value_investment.data.providers.factory import ProviderFactory
    mock_cache = MagicMock()
    provider = ProviderFactory.create_provider(mock_cache, market="A")
    assert provider.__class__.__name__ == "AShareProvider"


def test_provider_factory_returns_hkshare_for_market_hk():
    """ProviderFactory should return HKShareProvider for market='HK'"""
    from value_investment.data.providers.factory import ProviderFactory
    mock_cache = MagicMock()
    provider = ProviderFactory.create_provider(mock_cache, market="HK")
    assert provider.__class__.__name__ == "HKShareProvider"


def test_provider_factory_returns_us_share_for_market_us():
    """ProviderFactory should return USShareProvider for market='US'"""
    from value_investment.data.providers.factory import ProviderFactory
    mock_cache = MagicMock()
    provider = ProviderFactory.create_provider(mock_cache, market="US")
    assert provider.__class__.__name__ == "USShareProvider"


def test_provider_factory_raises_for_unsupported_market():
    """ProviderFactory should raise ValueError for unsupported market"""
    from value_investment.data.providers.factory import ProviderFactory
    mock_cache = MagicMock()
    with pytest.raises(ValueError) as exc_info:
        ProviderFactory.create_provider(mock_cache, market="INVALID")
    assert "Unsupported market" in str(exc_info.value)
