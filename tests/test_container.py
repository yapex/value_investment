"""Tests for dependency injection container"""

import pytest  # type: ignore
from dependency_injector import containers, providers  # type: ignore


class TestContainerBasic:
    """Test basic Container functionality"""

    def test_container_import(self):
        """Container should be importable"""
        from value_investment.core.container import Container
        assert Container is not None

    def test_container_has_config(self):
        """Container should have config provider"""
        from value_investment.core.container import Container
        
        container = Container()
        assert hasattr(container, 'config')

    def test_container_has_settings(self):
        """Container should have settings provider"""
        from value_investment.core.container import Container
        
        container = Container()
        assert hasattr(container, 'app_settings')

    def test_container_has_datasources(self):
        """Container should have datasources provider"""
        from value_investment.core.container import Container
        
        container = Container()
        assert hasattr(container, 'datasources')

    def test_container_has_cache(self):
        """Container should have cache provider"""
        from value_investment.core.container import Container
        
        container = Container()
        assert hasattr(container, 'cache')


class TestContainerProviders:
    """Test Container provider creation"""

    def test_container_create_provider(self):
        """Container should create providers from config"""
        from value_investment.core.container import Container
        from value_investment.core.config import ProviderConfig
        
        # Create test config
        test_config = ProviderConfig(
            name="test_provider",
            module="value_investment.data.providers.base_provider",
            class_name="BaseProvider",
            init_kwargs={},
            field_mappings={}
        )
        
        container = Container()
        container.datasources.override(
            providers.Object(
                type('Config', (), {
                    'providers': {'test': test_config},
                    'markets': {},
                    'get_provider': lambda self, name: test_config,
                    'get_market_source': lambda self, market: None,
                    'list_providers': lambda self: ['test'],
                    'list_markets': lambda self: [],
                })()
            )
        )
        
        # Should be able to call create_provider method
        assert hasattr(container, 'create_provider')

    def test_container_get_financial_provider(self):
        """Container should provide get_financial_provider method"""
        from value_investment.core.container import Container
        
        container = Container()
        assert hasattr(container, 'get_financial_provider')

    def test_container_get_market_provider(self):
        """Container should provide get_market_provider method"""
        from value_investment.core.container import Container
        
        container = Container()
        assert hasattr(container, 'get_market_provider')


class TestContainerIntegration:
    """Test Container integration"""

    def test_container_with_default_config(self):
        """Container should work with default configuration"""
        from value_investment.core.container import Container
        from value_investment.core.defaults import DEFAULT_DATASOURCES
        
        container = Container()
        
        # Override datasources with default config
        container.datasources.override(
            providers.Object(DEFAULT_DATASOURCES)
        )
        
        # Verify config is accessible
        datasources = container.datasources()
        assert datasources is not None
        assert len(datasources.providers) > 0
        assert len(datasources.markets) > 0

    def test_container_config_override(self):
        """Container should support config override"""
        from value_investment.core.container import Container
        from value_investment.core.config import DataSourcesConfig, ProviderConfig, MarketDataSource
        
        # Create custom config
        custom_config = DataSourcesConfig(
            providers={
                "custom": ProviderConfig(
                    name="custom",
                    module="test.module",
                    class_name="CustomProvider",
                )
            },
            markets={
                "A": MarketDataSource(financial="custom", market="custom")
            }
        )
        
        container = Container()
        container.datasources.override(
            providers.Object(custom_config)
        )
        
        datasources = container.datasources()
        assert "custom" in datasources.providers
        assert datasources.get_provider("custom").class_name == "CustomProvider"
