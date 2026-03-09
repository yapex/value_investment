from datetime import datetime
from typing import Any

from value_investment.core.constants import DATE_FORMAT_COMPACT
from value_investment.data.mapper import DataMapper


class DataProvider:
    """Lightweight dependency provider - fetches data by stock_code"""

    def __init__(self, stock_provider, market: str = 'A'):
        self._provider = stock_provider
        self._market = market

    def get(self, data_type: str, stock_code: str, **kwargs) -> Any:
        # Set default end_date if not provided
        if data_type == 'prices' and 'end_date' not in kwargs:
            kwargs['end_date'] = datetime.now().strftime(DATE_FORMAT_COMPACT)

        fetchers = {
            'quarterly': lambda: self._map_quarterly(
                self._provider.get_quarterly_indicator(stock_code)
            ),
            'prices': lambda: self._provider.get_historical_data(stock_code, **kwargs),
            'stock_info': lambda: self._provider.get_stock_info(stock_code),
            'financial_indicator': lambda: self._map_financial_indicator(
                self._provider.get_financial_indicator(stock_code)
            ),
        }
        if data_type not in fetchers:
            raise ValueError(f"Unknown data type: {data_type}")
        return fetchers[data_type]()

    def _map_financial_indicator(self, df):
        """Apply field mapping to financial_indicator data"""
        if df is None or (hasattr(df, 'empty') and df.empty):
            return df
        return DataMapper.map_financial_indicator(df, market=self._market)

    def _map_quarterly(self, df):
        """Apply field mapping to quarterly data"""
        if df is None or (hasattr(df, 'empty') and df.empty):
            return df
        return DataMapper.map_quarterly(df, market=self._market)

class DependencyRegistry:
    """Dependency registry - maps declarations to fetchers"""

    def __init__(self, data_provider: DataProvider):
        self._provider = data_provider

    def resolve(self, needs: list[str], stock_code: str, **kwargs) -> dict:
        """Resolve dependencies based on declarations"""
        if not needs:
            return {}
        return {n: self._provider.get(n, stock_code, **kwargs) for n in needs}
