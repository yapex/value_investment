from dataclasses import dataclass
from typing import Any
from datetime import datetime

class DataProvider:
    """Lightweight dependency provider - fetches data by stock_code"""

    def __init__(self, stock_provider):
        self._provider = stock_provider

    def get(self, data_type: str, stock_code: str, **kwargs) -> Any:
        # Set default end_date if not provided
        if data_type == 'prices' and 'end_date' not in kwargs:
            kwargs['end_date'] = datetime.now().strftime('%Y%m%d')

        fetchers = {
            'quarterly': lambda: self._provider.get_quarterly_indicator(stock_code),
            'prices': lambda: self._provider.get_historical_data(stock_code, **kwargs),
            'stock_info': lambda: self._provider.get_stock_info(stock_code),
            'financial_indicator': lambda: self._provider.get_financial_indicator(stock_code),
        }
        if data_type not in fetchers:
            raise ValueError(f"Unknown data type: {data_type}")
        return fetchers[data_type]()

class DependencyRegistry:
    """Dependency registry - maps declarations to fetchers"""

    def __init__(self, data_provider: DataProvider):
        self._provider = data_provider

    def resolve(self, needs: list[str], stock_code: str, **kwargs) -> dict:
        """Resolve dependencies based on declarations"""
        if not needs:
            return {}
        return {n: self._provider.get(n, stock_code, **kwargs) for n in needs}
