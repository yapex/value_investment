"""Tests for default data source configuration"""

import pytest  # type: ignore


class TestDefaultConfig:
    """Test default configuration"""

    def test_defaults_import(self):
        """Default config should be importable"""
        from value_investment.core.defaults import DEFAULT_DATASOURCES
        assert DEFAULT_DATASOURCES is not None

    def test_defaults_has_providers(self):
        """Default config should have providers defined"""
        from value_investment.core.defaults import DEFAULT_DATASOURCES
        
        assert len(DEFAULT_DATASOURCES.providers) > 0
        assert "tushare_a" in DEFAULT_DATASOURCES.providers or "akshare_a" in DEFAULT_DATASOURCES.providers

    def test_defaults_has_markets(self):
        """Default config should have market configurations"""
        from value_investment.core.defaults import DEFAULT_DATASOURCES
        
        assert "A" in DEFAULT_DATASOURCES.markets
        assert len(DEFAULT_DATASOURCES.markets) >= 1

    def test_defaults_market_a_config(self):
        """Default config should have A market configuration"""
        from value_investment.core.defaults import DEFAULT_DATASOURCES
        
        a_market = DEFAULT_DATASOURCES.get_market_source("A")
        assert a_market.financial is not None
        assert a_market.market is not None

    def test_defaults_provider_has_field_mappings(self):
        """Default providers should have field mappings"""
        from value_investment.core.defaults import DEFAULT_DATASOURCES
        
        # At least one provider should have field mappings
        has_mappings = any(
            provider.field_mappings 
            for provider in DEFAULT_DATASOURCES.providers.values()
        )
        assert has_mappings, "At least one provider should have field_mappings defined"

    def test_defaults_all_markets_valid(self):
        """All market configurations should reference valid providers"""
        from value_investment.core.defaults import DEFAULT_DATASOURCES
        
        provider_names = set(DEFAULT_DATASOURCES.providers.keys())
        
        for market, ds in DEFAULT_DATASOURCES.markets.items():
            assert ds.financial in provider_names, f"Market {market} references unknown provider: {ds.financial}"
            assert ds.market in provider_names, f"Market {market} references unknown provider: {ds.market}"

    def test_defaults_list_methods(self):
        """Config should provide list methods"""
        from value_investment.core.defaults import DEFAULT_DATASOURCES
        
        providers = DEFAULT_DATASOURCES.list_providers()
        assert isinstance(providers, list)
        assert len(providers) > 0
        
        markets = DEFAULT_DATASOURCES.list_markets()
        assert isinstance(markets, list)
        assert "A" in markets
