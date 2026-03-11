"""Data source configuration models using Pydantic"""
import os
from pydantic import BaseModel, Field, field_validator


class ProviderConfig(BaseModel):
    """Configuration for a data provider
    
    Attributes:
        name: Unique identifier for the provider
        module: Python module path (e.g., "value_investment.data.providers.tushare_provider")
        class_name: Provider class name within the module
        init_kwargs: Keyword arguments for provider initialization (supports ${ENV_VAR} syntax)
        field_mappings: Field name mappings by data type (e.g., "income", "balance", "market")
    """
    
    name: str
    module: str
    class_name: str
    init_kwargs: dict[str, str] = Field(default_factory=dict)
    field_mappings: dict[str, dict[str, str]] = Field(default_factory=dict)
    
    @field_validator('init_kwargs')
    @classmethod
    def expand_env_vars(cls, v: dict) -> dict:
        """Expand environment variables in init_kwargs
        
        Supports ${VAR_NAME} syntax. If variable is not found, replaces with empty string.
        
        Example:
            {"token": "${TUSHARE_TOKEN}"} → {"token": "actual_token_value"}
        """
        result = {}
        for k, val in v.items():
            if isinstance(val, str) and val.startswith('${') and val.endswith('}'):
                env_var = val[2:-1]
                result[k] = os.getenv(env_var, '')
            else:
                result[k] = val
        return result
    
    def get_mapping(self, data_type: str) -> dict[str, str]:
        """Get field mapping for a specific data type
        
        Args:
            data_type: Type of data (e.g., "income", "balance", "cashflow", "market")
            
        Returns:
            Dictionary mapping native field names to standard field names
        """
        return self.field_mappings.get(data_type, {})


class MarketDataSource(BaseModel):
    """Data source configuration for a specific market
    
    Attributes:
        financial: Provider name for financial data (balance sheet, income, cashflow)
        market: Provider name for market data (prices, volumes)
    """
    
    financial: str
    market: str


class DataSourcesConfig(BaseModel):
    """Complete data source configuration
    
    Attributes:
        providers: Dictionary of provider configurations keyed by name
        markets: Dictionary of market data source configurations keyed by market code (A/HK/US)
    """
    
    providers: dict[str, ProviderConfig]
    markets: dict[str, MarketDataSource]
    
    @field_validator('markets')
    @classmethod
    def validate_providers_exist(cls, v: dict, info) -> dict:
        """Validate that all referenced providers are defined
        
        Raises:
            ValueError: If a market references an unknown provider
        """
        # Get providers from validation context
        providers_data = info.data.get('providers', {})
        providers = set(providers_data.keys()) if providers_data else set()
        
        for market, ds in v.items():
            if ds.financial not in providers:
                raise ValueError(
                    f"Market '{market}' references unknown financial provider: {ds.financial}. "
                    f"Available providers: {list(providers)}"
                )
            if ds.market not in providers:
                raise ValueError(
                    f"Market '{market}' references unknown market provider: {ds.market}. "
                    f"Available providers: {list(providers)}"
                )
        return v
    
    def get_provider(self, name: str) -> ProviderConfig:
        """Get provider configuration by name
        
        Args:
            name: Provider name
            
        Returns:
            ProviderConfig instance
            
        Raises:
            KeyError: If provider not found
        """
        return self.providers[name]
    
    def get_market_source(self, market: str) -> MarketDataSource:
        """Get market data source configuration
        
        Args:
            market: Market code (A/HK/US)
            
        Returns:
            MarketDataSource instance. Falls back to "A" market if not found.
            
        Raises:
            KeyError: If market not found and no fallback
        """
        if market in self.markets:
            return self.markets[market]
        # Fallback to A market
        if 'A' in self.markets:
            return self.markets['A']
        # Return first available market
        return next(iter(self.markets.values()))
    
    def list_providers(self) -> list[str]:
        """List all provider names"""
        return list(self.providers.keys())
    
    def list_markets(self) -> list[str]:
        """List all market codes"""
        return list(self.markets.keys())
