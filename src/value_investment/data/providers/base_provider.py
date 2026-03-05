"""Base provider class with shared caching logic"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


def _get_ttl_until_next_midnight() -> int:
    """Get TTL in seconds until next midnight (for daily refresh data like stock info)"""
    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int((tomorrow - now).total_seconds())


def _get_ttl_until_june_next_year(end_year: int) -> int:
    """Get TTL in seconds until June 30th of the next year"""
    now = datetime.now()
    june_next_year = datetime(now.year + 1, 6, 30, 23, 59, 59)
    return int((june_next_year - now).total_seconds())


class BaseProvider(ABC):
    """Base class for market-specific providers with shared caching logic"""

    def __init__(self, cache: "SmartCache", market: str):
        """
        Initialize provider

        Args:
            cache: SmartCache instance
            market: Market type - "A" (A股), "HK" (港股), "US" (美股)
        """
        self._cache = cache
        self._market = market

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format"""
        if not date_str:
            return date_str
        if "-" in date_str:
            return date_str
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    @abstractmethod
    def get_stock_info(self, symbol: str, force_refresh: bool = False) -> pd.DataFrame:
        """Get stock basic information - must be implemented by subclass"""
        pass

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        end_date: str,
        start_date: str | None = None,
        adjust: str = "hfq",
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get historical price data - must be implemented by subclass"""
        pass

    @abstractmethod
    def get_balance_sheet(
        self,
        symbol: str,
        end_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get balance sheet - must be implemented by subclass"""
        pass

    @abstractmethod
    def get_income_statement(
        self,
        symbol: str,
        end_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get income statement - must be implemented by subclass"""
        pass

    @abstractmethod
    def get_cash_flow_statement(
        self,
        symbol: str,
        end_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get cash flow statement - must be implemented by subclass"""
        pass
