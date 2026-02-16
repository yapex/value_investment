"""Tests for dependency injection container - Phase 1"""
import pytest
from unittest.mock import Mock, patch


class TestContainer:
    """Test DI container setup"""

    def test_container_imports(self):
        """Container module should be importable"""
        from value_investment.core.container import Container

        assert Container is not None

    def test_container_has_cache_provider(self):
        """Container should have cache provider"""
        from value_investment.core.container import Container

        container = Container()
        assert hasattr(container, 'cache')

    def test_container_has_akshare_provider(self):
        """Container should have akshare provider"""
        from value_investment.core.container import Container

        container = Container()
        assert hasattr(container, 'akshare_provider')

    def test_container_has_indicator_factory(self):
        """Container should have indicator factory"""
        from value_investment.core.container import Container

        container = Container()
        assert hasattr(container, 'indicator_factory')

    def test_cache_is_singleton(self):
        """Cache should be singleton"""
        from value_investment.core.container import Container

        container = Container()
        cache1 = container.cache()
        cache2 = container.cache()
        assert cache1 is cache2


class TestConfig:
    """Test configuration"""

    def test_config_imports(self):
        """Config module should be importable"""
        from value_investment.core.config import Config

        assert Config is not None

    def test_config_has_cache_dir(self):
        """Config should have cache_dir setting"""
        from value_investment.core.config import Config

        config = Config()
        assert hasattr(config, 'cache_dir')

    def test_config_has_cache_ttl(self):
        """Config should have cache_ttl setting"""
        from value_investment.core.config import Config

        config = Config()
        assert hasattr(config, 'cache_ttl')
