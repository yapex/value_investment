"""Simple dependency injection container

A lightweight alternative to dependency_injector, using plain Python classes.
"""
import importlib
from typing import Any

from value_investment.core.settings import Settings, settings
from value_investment.core.config import DataSourcesConfig
from value_investment.core.defaults import DEFAULT_DATASOURCES
from value_investment.data.cache import SmartCache


class SimpleContainer:
    """Simple dependency injection container
    
    Features:
    - Plain Python implementation (no magic)
    - Pydantic configuration support
    - Dynamic provider creation
    - Market-specific routing
    - Singleton caching
    
    Usage:
        container = SimpleContainer()
        provider = container.get_financial_provider("A")
        df = provider.get_balance_sheet("000001.SZ", 2023)
    """
    
    def __init__(
        self,
        datasources: DataSourcesConfig | None = None,
        cache_dir: str | None = None,
        cache_ttl: int | None = None,
    ):
        """Initialize container
        
        Args:
            datasources: Data sources configuration (uses DEFAULT_DATASOURCES if None)
            cache_dir: Cache directory (uses settings if None)
            cache_ttl: Cache TTL in seconds (uses settings if None)
        """
        self._datasources = datasources or DEFAULT_DATASOURCES
        self._settings = settings
        
        # Cache configuration
        cache_dir = cache_dir or self._settings.cache_dir
        cache_ttl = cache_ttl or self._settings.cache_ttl
        
        # Initialize cache (singleton)
        self._cache = SmartCache(cache_dir=cache_dir, default_ttl=cache_ttl)
        
        # Provider cache (singleton instances)
        self._providers: dict[str, Any] = {}
    
    @property
    def datasources(self) -> DataSourcesConfig:
        """Get data sources configuration"""
        return self._datasources
    
    @property
    def cache(self) -> SmartCache:
        """Get cache instance"""
        return self._cache
    
    def create_provider(self, provider_name: str) -> Any:
        """Create provider instance from configuration
        
        Args:
            provider_name: Provider name from config
            
        Returns:
            Provider instance
            
        Raises:
            ImportError: If provider module/class not found
            KeyError: If provider not in config
        """
        config = self._datasources.get_provider(provider_name)
        
        # Dynamic import
        module = importlib.import_module(config.module)
        provider_class = getattr(module, config.class_name)
        
        # Instantiate with cache and field_mappings
        provider = provider_class(
            cache=self._cache,
            field_mappings=config.field_mappings,
            **config.init_kwargs
        )
        
        return provider
    
    def get_provider(self, provider_name: str) -> Any:
        """Get or create provider instance (singleton)
        
        Args:
            provider_name: Provider name
            
        Returns:
            Provider instance
        """
        if provider_name not in self._providers:
            self._providers[provider_name] = self.create_provider(provider_name)
        
        return self._providers[provider_name]
    
    def get_financial_provider(self, market: str) -> Any:
        """Get financial data provider for a specific market
        
        Args:
            market: Market code (A/HK/US)
            
        Returns:
            Provider instance for financial data
        """
        ds = self._datasources.get_market_source(market)
        return self.get_provider(ds.financial)
    
    def get_market_provider(self, market: str) -> Any:
        """Get market data provider for a specific market
        
        Args:
            market: Market code (A/HK/US)
            
        Returns:
            Provider instance for market data
        """
        ds = self._datasources.get_market_source(market)
        return self.get_provider(ds.market)
    
    def get_provider_for_data_type(self, market: str, data_type: str) -> Any:
        """Get appropriate provider for data type
        
        Args:
            market: Market code (A/HK/US)
            data_type: Type of data ("financial" or "market")
            
        Returns:
            Provider instance
        """
        if data_type == "market":
            return self.get_market_provider(market)
        else:
            return self.get_financial_provider(market)
    
    def clear_cache(self) -> None:
        """Clear all caches"""
        self._cache.clear()
        self._providers.clear()
