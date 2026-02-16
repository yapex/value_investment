"""Tests for provider multi-market indicators"""
import pytest
from unittest.mock import Mock, patch


class TestProviderMarketIndicators:
    """Test AkshareProvider multi-market financial indicator support"""

    def test_detect_market_from_code(self):
        """Should auto-detect market from stock code"""
        from value_investment.data.providers.akshare_provider import AkshareProvider

        # Create mock cache
        mock_cache = Mock()

        provider = AkshareProvider(mock_cache, market="A")

        # Check that detect_market method exists or add it
        if hasattr(provider, '_detect_market'):
            assert provider._detect_market("600519") == "A股"
            assert provider._detect_market("00700") == "港股"
            assert provider._detect_market("AAPL") == "美股"
        else:
            # If method doesn't exist, test should fail
            assert False, "_detect_market method not implemented"

    def test_provider_init_with_market(self):
        """Should initialize provider with market parameter"""
        from value_investment.data.providers.akshare_provider import AkshareProvider

        mock_cache = Mock()

        provider_a = AkshareProvider(mock_cache, market="A")
        assert provider_a._market == "A"

        provider_hk = AkshareProvider(mock_cache, market="HK")
        assert provider_hk._market == "HK"

        provider_us = AkshareProvider(mock_cache, market="US")
        assert provider_us._market == "US"
