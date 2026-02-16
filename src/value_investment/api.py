"""Python API for value investment analysis"""
from typing import Optional

from value_investment.data.cache import SmartCache
from value_investment.data.providers.akshare_provider import AkshareProvider
from value_investment.indicators.factory import IndicatorFactory
from value_investment.indicators.base import IndicatorResult


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
        start_date: str,
        end_date: str,
        adjust: str = "hfq",
    ):
        """
        Get historical price data

        Args:
            symbol: Stock code
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            adjust: Adjustment type - "" (none), "qfq" (forward), "hfq" (backward, default for backtesting)

        Returns:
            DataFrame with historical prices
        """
        return self._provider.get_historical_data(symbol, start_date, end_date, adjust)

    def get_financial_data(
        self,
        symbol: str,
        start_year: int,
        end_year: int,
    ):
        """
        Get unified financial data

        Args:
            symbol: Stock code
            start_year: Start year
            end_year: End year

        Returns:
            DataFrame with merged financial data
        """
        return self._provider.get_financial_data(symbol, start_year, end_year)

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
        return indicator.calculate(stock_code, years, self._provider, **kwargs)

    def analyze(
        self,
        stock_code: str,
        years: int = 10,
        **kwargs,
    ) -> dict:
        """
        Perform complete analysis

        Args:
            stock_code: Stock code
            years: Number of years for analysis
            **kwargs: Additional parameters for indicators

        Returns:
            Dictionary with all indicator results
        """
        results = {}
        for name in self._factory.list_indicators():
            try:
                result = self._factory.get(name).calculate(
                    stock_code, years, self._provider, **kwargs
                )
                results[name] = result
            except Exception as e:
                results[name] = {"error": str(e)}
        return results

    def list_indicators(self) -> list:
        """
        List all available indicators

        Returns:
            List of indicator names
        """
        return self._factory.list_indicators()

    def clear_cache(self, symbol: Optional[str] = None):
        """
        Clear cache

        Args:
            symbol: Optional specific symbol to clear cache for
        """
        if symbol:
            self._cache.invalidate(f"info_{symbol}")
            self._cache.invalidate(f"balance_{symbol}")
            self._cache.invalidate(f"income_{symbol}")
            self._cache.invalidate(f"cashflow_{symbol}")
            self._cache.invalidate(f"hist_{symbol}")
            self._cache.invalidate(f"indicator_{symbol}")
        else:
            # Clear all cache
            for key in list(self._cache._memory_cache.keys()):
                self._cache.invalidate(key)
