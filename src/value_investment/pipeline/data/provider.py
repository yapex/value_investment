"""Data provider interface for pipeline"""
from typing import Any, Protocol


class DataProvider(Protocol):
    """Protocol for data providers
    
    Any class implementing these methods can be used as a provider.
    No inheritance required - structural subtyping.
    """

    def fetch_financial_data(
        self,
        stock_code: str,
        fields: set[str],
        end_year: int,
        years: int = 10,
    ) -> dict[str, dict[int, Any]]:
        """Fetch financial data for specified fields

        Args:
            stock_code: Stock code
            fields: Set of standard field names to fetch
            end_year: End year
            years: Number of years to fetch

        Returns:
            {field: {year: value}}
        """
        ...

    @property
    def supported_fields(self) -> set[str]:
        """Set of fields this provider can fetch"""
        ...

    def fetch_indicators(
        self,
        stock_code: str,
        fields: set[str],
        end_year: int,
        years: int = 10,
    ) -> dict[str, dict[int, Any]]:
        """Fetch pre-calculated financial indicators

        Args:
            stock_code: Stock code
            fields: Set of standard indicator fields to fetch
            end_year: End year
            years: Number of years to fetch

        Returns:
            {field: {year: value}}
        """
        ...

    def fetch_market_data(
        self,
        stock_code: str,
        fields: set[str],
    ) -> dict[str, Any]:
        """Fetch current market data (市值、PE、PB等)

        Args:
            stock_code: Stock code
            fields: Set of market fields to fetch (market_cap, pe_ratio, pb_ratio)

        Returns:
            {field: value} 单个时间点的值
        """
        ...
