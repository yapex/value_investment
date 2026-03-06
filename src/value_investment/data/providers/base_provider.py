"""Base provider with field mapping and cache support"""
from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BaseProvider(ABC):
    """Abstract base class for all data providers
    
    Features:
    - Field mapping support (native fields → standard fields)
    - Cache integration
    - Common helper methods
    
    Usage:
        class TushareProvider(BaseProvider):
            def __init__(self, cache, field_mappings=None, token=""):
                super().__init__(cache, field_mappings)
                self._token = token
            
            def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
                df = self._fetch_data(...)  # Fetch from API
                return self._apply_mapping(df, "balance")  # Apply mapping
    """
    
    def __init__(
        self,
        cache: Any,
        field_mappings: dict[str, dict[str, str]] | None = None,
        **kwargs: Any,
    ):
        """Initialize provider
        
        Args:
            cache: Cache instance (SmartCache or compatible)
            field_mappings: Field name mappings by data type
                Example: {"income": {"ts_code": "stock_code"}, "balance": {...}}
            **kwargs: Additional provider-specific arguments (token, timeout, etc.)
        """
        self._cache = cache
        self._field_mappings = field_mappings or {}
        self._init_kwargs = kwargs
    
    def get_field_mapping(self, data_type: str) -> dict[str, str]:
        """Get field mapping for a specific data type
        
        Args:
            data_type: Type of data (e.g., "income", "balance", "cashflow", "market")
            
        Returns:
            Dictionary mapping native field names to standard field names
        """
        return self._field_mappings.get(data_type, {})
    
    def _apply_mapping(
        self,
        df: pd.DataFrame | None,
        data_type: str,
    ) -> pd.DataFrame | None:
        """Apply field mapping to DataFrame
        
        Only renames columns that exist in the DataFrame.
        Unmapped columns are kept as-is.
        
        Args:
            df: DataFrame to transform (can be None)
            data_type: Type of data (to select correct mapping)
            
        Returns:
            Transformed DataFrame with standard field names.
            Returns None if input is None.
        """
        if df is None:
            return None
        
        if df.empty:
            return df
        
        # Get mapping for this data type
        mapping = self.get_field_mapping(data_type)
        
        if not mapping:
            return df
        
        # Build rename map (only for columns that exist)
        rename_map = {
            native: standard
            for native, standard in mapping.items()
            if native in df.columns
        }
        
        if not rename_map:
            return df
        
        # Apply renaming
        return df.rename(columns=rename_map)
    
    def _get_from_cache(self, key: str) -> Any | None:
        """Get data from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if not found
        """
        try:
            return self._cache.get(key)
        except Exception:
            return None
    
    def _set_to_cache(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set data to cache
        
        Args:
            key: Cache key
            value: Data to cache
            ttl: Time to live in seconds (optional, uses default if not provided)
        """
        try:
            self._cache.set(key, value, ttl=ttl)
        except Exception:
            pass  # Cache errors should not break data fetching
    
    def _invalidate_cache(self, key: str) -> None:
        """Invalidate cache entry
        
        Args:
            key: Cache key
        """
        try:
            self._cache.invalidate(key)
        except Exception:
            pass
    
    def _get_cache_key(self, *parts: str) -> str:
        """Build cache key from parts
        
        Args:
            *parts: Key parts (e.g., data_type, stock_code, year)
            
        Returns:
            Colon-separated cache key
        """
        return ":".join(str(p) for p in parts)
    
    @abstractmethod
    def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get balance sheet data
        
        Args:
            stock_code: Stock code
            end_year: End year
            
        Returns:
            DataFrame with balance sheet data (standard field names)
        """
        pass
    
    # Optional methods with default implementations
    
    def get_income_statement(
        self,
        stock_code: str,
        end_year: int,
    ) -> pd.DataFrame:
        """Get income statement data
        
        Args:
            stock_code: Stock code
            end_year: End year
            
        Returns:
            DataFrame with income statement data (standard field names)
        """
        raise NotImplementedError("Provider does not support income statements")
    
    def get_cash_flow_statement(
        self,
        stock_code: str,
        end_year: int,
    ) -> pd.DataFrame:
        """Get cash flow statement data
        
        Args:
            stock_code: Stock code
            end_year: End year
            
        Returns:
            DataFrame with cash flow statement data (standard field names)
        """
        raise NotImplementedError("Provider does not support cash flow statements")
    
    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "",
    ) -> pd.DataFrame:
        """Get historical market data (prices, volumes)
        
        Args:
            stock_code: Stock code
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            adjust: Adjustment type ("", "qfq", "hfq")
            
        Returns:
            DataFrame with historical market data (standard field names)
        """
        raise NotImplementedError("Provider does not support historical data")
    
    def get_stock_info(self, stock_code: str) -> pd.DataFrame:
        """Get stock basic information
        
        Args:
            stock_code: Stock code
            
        Returns:
            DataFrame with stock info
        """
        raise NotImplementedError("Provider does not support stock info")
