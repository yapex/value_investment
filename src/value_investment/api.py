"""Python API for value investment analysis"""
from typing import Optional

from value_investment.data.cache import SmartCache
from value_investment.data.providers.akshare_provider import AkshareProvider
from value_investment.indicators.factory import IndicatorFactory
from value_investment.indicators.base import IndicatorResult
from value_investment.indicators.registry import IndicatorRegistry, register_defaults
from value_investment.indicators.base import IndicatorMeta


class ValueInvestment:
    """
    Python API for value investment analysis

    Example:
        >>> vi = ValueInvestment()
        >>> info = vi.get_stock_info("600519")
        >>> print(info)
    """

    def __init__(self, cache_dir: Optional[str] = None, market: str = "A"):
        """
        Initialize ValueInvestment API

        Args:
            cache_dir: Cache directory path
            market: Market type - "A" (A股), "HK" (港股), "US" (美股)
        """
        self._cache = SmartCache(cache_dir=cache_dir or "./.cache")
        self._provider = AkshareProvider(cache=self._cache, market=market)
        self._factory = IndicatorFactory(provider=self._provider)
        # Initialize indicator registry with defaults
        register_defaults()

    def get_stock_info(self, symbol: str):
        """
        Get stock basic information

        Args:
            symbol: Stock code (e.g., "600519")

        Returns:
            DataFrame with stock info
        """
        return self._provider.get_stock_info(symbol)

    def get_historical_data(
        self,
        symbol: str,
        end_date: str,
        start_date: str | None = None,
        adjust: str = "hfq",
    ):
        """
        Get historical price data

        Args:
            symbol: Stock code
            end_date: End date (YYYYMMDD, required)
            start_date: Start date (YYYYMMDD, optional, defaults to earliest available)
            adjust: Adjustment type - "" (none), "qfq" (forward), "hfq" (backward, default for backtesting)

        Returns:
            DataFrame with historical prices
        """
        return self._provider.get_historical_data(symbol, end_date, start_date, adjust)

    def get_financial_data(
        self,
        symbol: str,
        end_year: int | None = None,
    ):
        """
        Get unified financial data

        Args:
            symbol: Stock code
            end_year: End year (optional, defaults to current year)

        Returns:
            DataFrame with merged financial data (all historical data up to end_year)
        """
        return self._provider.get_financial_data(symbol, end_year)

    def get_financial_indicator(self, symbol: str):
        """
        Get financial analysis indicators

        Args:
            symbol: Stock code

        Returns:
            DataFrame with financial indicators
        """
        return self._provider.get_financial_indicator(symbol)

    def calculate_indicator(
        self,
        indicator_name: str,
        stock_code: str,
        years: int = 10,
        **kwargs,
    ) -> IndicatorResult:
        """
        Calculate a specific indicator

        Args:
            indicator_name: Name of the indicator (e.g., "roe", "roa")
            stock_code: Stock code
            years: Number of years for calculation
            **kwargs: Additional parameters for the indicator

        Returns:
            IndicatorResult with calculated value
        """
        indicator = self._factory.get(indicator_name)

        # Use shared method to prepare data
        years = kwargs.pop('years', 10)
        market_cap = kwargs.get('market_cap')
        financial_data, market_cap = self._prepare_data(stock_code, years, market_cap)

        if market_cap:
            kwargs['market_cap'] = market_cap

        # Pass data to indicator (data-passing pattern)
        return indicator.calculate(financial_data, **kwargs)

    def _prepare_data(
        self,
        stock_code: str,
        years: int = 10,
        market_cap: float = None,
    ) -> tuple:
        """
        Prepare financial data and market cap for indicators.
        Shared by calculate_indicator and analyze methods.
        """
        from datetime import datetime

        current_year = datetime.now().year
        all_data = self._provider.get_financial_data(stock_code, current_year)

        # Take latest years
        if 'year' in all_data.columns:
            all_data = all_data.sort_values('year', ascending=False)
            financial_data = all_data.head(years)
        else:
            financial_data = all_data

        # Auto-fetch market_cap if not provided
        if market_cap is None:
            try:
                info = self._provider.get_stock_info(stock_code)
                if 'item' in info.columns:
                    for _, row in info.iterrows():
                        if '市值' in str(row['item']):
                            market_cap = float(row['value'])
                            break
            except Exception:
                pass

        return financial_data, market_cap

    def analyze(
        self,
        stock_code: str,
        years: int = 10,
        cagr_metrics: list = None,
        market_cap: float = None,
        **kwargs,
    ) -> dict:
        """
        Perform complete analysis

        Args:
            stock_code: Stock code
            years: Number of years for analysis
            cagr_metrics: List of metrics for CAGR calculation, e.g. ["revenue", "net_profit"]
            market_cap: Market capitalization (if not provided, will try to fetch from stock info)
            **kwargs: Additional parameters for indicators

        Returns:
            Dictionary with all indicator results
        """
        # Use shared method to prepare data
        financial_data, market_cap = self._prepare_data(stock_code, years, market_cap)

        # Pass market_cap to indicators
        if market_cap:
            kwargs['market_cap'] = market_cap

        # Calculate all indicators
        results = {}
        for name in self._factory.list_indicators():
            try:
                indicator = self._factory.get(name)
                result = indicator.calculate(financial_data, **kwargs)
                results[name] = result
            except Exception as e:
                results[name] = {"error": str(e)}

        # Calculate additional CAGR metrics if specified
        if cagr_metrics:
            for metric in cagr_metrics:
                cagr_name = f"CAGR_{metric}"
                if cagr_name not in results:
                    try:
                        cagr_indicator = self._factory.get("CAGR")
                        result = cagr_indicator.calculate(financial_data, metric=metric, **kwargs)
                        results[cagr_name] = result
                    except Exception as e:
                        results[cagr_name] = {"error": str(e)}

        return results

    def get_indicator(self, name: str) -> Optional[IndicatorMeta]:
        """
        Get indicator metadata by name

        Args:
            name: Indicator name

        Returns:
            Indicator metadata or None if not found
        """
        registry = IndicatorRegistry.get_instance()
        return registry.get(name)

    def list_indicators(
        self,
        market: Optional[str] = None,
        indicator_type: Optional[str] = None,
    ) -> list:
        """
        List available indicators with optional filters

        Args:
            market: Filter by market ("A股", "港股", "美股")
            indicator_type: Filter by type ("RAW", "SIMPLE", "COMPLEX")

        Returns:
            List of indicator names
        """
        registry = IndicatorRegistry.get_instance()

        results = registry.list_all()

        # Also get indicators from factory (for backward compatibility)
        factory_indicators = self._factory.list_indicators()

        # Combine both sources - get names from registry
        registry_names = {ind.name for ind in results}

        # Add factory indicators that are not in registry
        for name in factory_indicators:
            if name not in registry_names:
                # Create a minimal meta for factory indicators
                from value_investment.indicators.base import IndicatorMeta, IndicatorType
                meta = IndicatorMeta(
                    name=name,
                    display_name=name,
                    type=IndicatorType.SIMPLE,
                    description="",
                )
                results.append(meta)

        # Filter by market
        if market:
            results = [ind for ind in results if market in ind.market_fields or not ind.market_fields]

        # Filter by type
        if indicator_type:
            results = [ind for ind in results if ind.type.value == indicator_type]

        # Return indicator names (backward compatible)
        return [ind.name for ind in results]

    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear cache

        Args:
            symbol: Optional specific symbol to clear cache for
        """
        if symbol:
            self._cache.invalidate(f"info_{symbol}")
            # Clear financial data cache (all end_years)
            for key in list(self._cache._memory_cache.keys()):
                if key.startswith(f"financial_{symbol}_"):
                    self._cache.invalidate(key)
            # Clear historical data cache (all end_dates)
            for key in list(self._cache._memory_cache.keys()):
                if key.startswith(f"hist_{symbol}_"):
                    self._cache.invalidate(key)
            self._cache.invalidate(f"indicator_{symbol}")
        else:
            # Clear all cache
            for key in list(self._cache._memory_cache.keys()):
                self._cache.invalidate(key)
