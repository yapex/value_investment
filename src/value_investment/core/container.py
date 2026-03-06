"""Dependency injection container using Pydantic configuration"""
import importlib

from dependency_injector import containers, providers  # type: ignore

from value_investment.core.settings import settings
from value_investment.core.config import DataSourcesConfig
from value_investment.core.defaults import DEFAULT_DATASOURCES
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

    wiring_config = {
        "auto_wire": False,
    }
    
    # Application settings (from Pydantic)
    app_settings = providers.Singleton(settings)
    
    # Data sources configuration (can be overridden)
    datasources = providers.Object(DEFAULT_DATASOURCES)
    
    # Configuration with defaults
    config = providers.Configuration()
    config.cache_dir.from_value("./.cache")
    config.cache_ttl.from_value(86400)
    
    # Cache (singleton)
    cache = providers.Singleton(
        SmartCache,
        cache_dir=config.cache_dir,
        default_ttl=config.cache_ttl,
    )
    
    @providers.method
    def create_provider(self, provider_name: str):
        """Create provider instance from configuration
        
        Args:
            provider_name: Name of provider from config
            
        Returns:
            Provider instance
            
        Raises:
            ImportError: If provider module/class not found
            KeyError: If provider not in config
        """
        ds_config = self.datasources().get_provider(provider_name)
        
        # Dynamic import
        module = importlib.import_module(ds_config.module)
        provider_class = getattr(module, ds_config.class_name)
        
        # Instantiate with cache and field_mappings
        return provider_class(
            cache=self.cache(),
            field_mappings=ds_config.field_mappings,
            **ds_config.init_kwargs
        )
    
    @providers.method
    def get_financial_provider(self, market: str):
        """Get financial data provider for a specific market
        
        Args:
            market: Market code (A/HK/US)
            
        Returns:
            Provider instance for financial data
        """
        ds = self.datasources().get_market_source(market)
        return self.create_provider(ds.financial)
    
    @providers.method
    def get_market_provider(self, market: str):
        """Get market data provider for a specific market
        
        Args:
            market: Market code (A/HK/US)
            
        Returns:
            Provider instance for market data
        """
        ds = self.datasources().get_market_source(market)
        return self.create_provider(ds.market)
    
    # Indicators factory (provider set dynamically)
    indicator_factory = providers.Factory(IndicatorFactory)
