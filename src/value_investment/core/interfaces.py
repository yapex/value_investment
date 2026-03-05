from typing import Protocol

import pandas as pd


class IStockProvider(Protocol):
    """Abstract interface for stock data providers"""

    def get_stock_info(self, stock_code: str) -> pd.DataFrame:
        """Get basic stock information"""
        ...

    def get_quarterly_indicator(self, stock_code: str) -> pd.DataFrame:
        """Get quarterly financial indicators"""
        ...

    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = ""
    ) -> pd.DataFrame:
        """Get historical price data"""
        ...

    def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get balance sheet data"""
        ...

    def get_income_statement(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get income statement data"""
        ...

    def get_cash_flow_statement(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get cash flow statement data"""
        ...
