"""Dependency injection container using Pydantic configuration"""
import importlib

from dependency_injector import containers, providers  # type: ignore

from value_investment.core.settings import Settings
from value_investment.core.defaults import DEFAULT_DATASOURCES
from value_investment.core.constants import DEFAULT_CACHE_TTL
from value_investment.data.cache import SmartCache
from value_investment.indicators.factory import IndicatorFactory


class Container(containers.DeclarativeContainer):
    """Dependency injection container with Pydantic configuration
    
    Features:
    - Loads configuration from Pydantic Settings
    - Supports dynamic provider creation from config
    - Market-specific provider routing
    - Singleton caching for providers
    """
    
    # Application settings (from Pydantic) - use Factory since Settings() reads env on init
    app_settings = providers.Factory(Settings)
    
    # Data sources configuration (can be overridden)
    datasources = providers.Object(DEFAULT_DATASOURCES)
    
    # Configuration with defaults
    config = providers.Configuration()
    config.cache_dir.from_value("./.cache")
    config.cache_ttl.from_value(DEFAULT_CACHE_TTL)
    
    # Cache (singleton)
    cache = providers.Singleton(
        SmartCache,
        cache_dir=config.cache_dir,
        default_ttl=config.cache_ttl,
    )
    
    # Indicators factory (provider set dynamically)
    indicator_factory = providers.Factory(IndicatorFactory)


def create_provider(container: Container, provider_name: str):
    """Create provider instance from configuration
    
    Args:
        container: The DI container
        provider_name: Name of provider from config
        
    Returns:
        Provider instance
        
    Raises:
        ImportError: If provider module/class not found
        KeyError: If provider not in config
    """
    ds_config = container.datasources().get_provider(provider_name)
    
    # Dynamic import
    module = importlib.import_module(ds_config.module)
    provider_class = getattr(module, ds_config.class_name)
    
    # Instantiate with cache and field_mappings
    return provider_class(
        cache=container.cache(),
        field_mappings=ds_config.field_mappings,
        **ds_config.init_kwargs
    )


def get_financial_provider(container: Container, market: str):
    """Get financial data provider for a specific market
    
    Args:
        container: The DI container
        market: Market code (A/HK/US)
        
    Returns:
        Provider instance for financial data
    """
    ds = container.datasources().get_market_source(market)
    return create_provider(container, ds.financial)


def get_market_provider(container: Container, market: str):
    """Get market data provider for a specific market
    
    Args:
        container: The DI container
        market: Market code (A/HK/US)
        
    Returns:
        Provider instance for market data
    """
    ds = container.datasources().get_market_source(market)
    return create_provider(container, ds.market)
