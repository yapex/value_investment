"""Dependency injection container"""
from dependency_injector import containers, providers

from value_investment.core.config import Config
from value_investment.data.cache import SmartCache
from value_investment.data.providers.factory import ProviderFactory
from value_investment.indicators.factory import IndicatorFactory


class Container(containers.DeclarativeContainer):
    """Dependency injection container"""

    # Configuration
    config = providers.Configuration()
    config.cache_dir(default="./.cache")
    config.cache_ttl(default=86400)
    config.market(default="A")

    # Core dependencies
    app_config = providers.Singleton(
        Config,
        cache_dir=config.cache_dir,
        cache_ttl=config.cache_ttl,
    )

    # Cache
    cache = providers.Singleton(
        SmartCache,
        cache_dir=config.cache_dir,
        default_ttl=config.cache_ttl,
    )

    # Data providers - use factory for market-specific providers
    akshare_provider = providers.Callable(
        ProviderFactory.create_provider,
        cache=cache,
        market=config.market,
    )

    # Indicators
    indicator_factory = providers.Factory(
        IndicatorFactory,
        provider=akshare_provider,
    )
