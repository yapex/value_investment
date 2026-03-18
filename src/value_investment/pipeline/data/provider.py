"""Data provider interface for pipeline"""
from abc import ABC, abstractmethod
from typing import Any


class DataProvider(ABC):
    """Abstract data provider interface for pipeline handlers"""

    @abstractmethod
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
        pass

    @property
    @abstractmethod
    def supported_fields(self) -> set[str]:
        """Set of fields this provider can fetch"""
        pass
