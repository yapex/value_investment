from typing import Protocol

import pandas as pd


class IMarketDataProvider(Protocol):
    """Interface for market data (prices, volumes) - handles historical trading data"""

    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = ""
    ) -> pd.DataFrame:
        """Get historical price data"""
        ...


class ICompanyInfoProvider(Protocol):
    """Interface for company information - static data like name, industry"""

    def get_stock_info(self, stock_code: str) -> pd.DataFrame:
        """Get basic stock information"""
        ...


class IFinancialStatementProvider(Protocol):
    """Interface for financial statements - balance sheet, income, cash flow"""

    def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get balance sheet data"""
        ...

    def get_income_statement(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get income statement data"""
        ...

    def get_cash_flow_statement(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get cash flow statement data"""
        ...


# Backward-compatible alias - keep existing code working
IStockProvider = IFinancialStatementProvider


class IStockProviderOld(Protocol):
    """Original abstract interface for stock data providers (deprecated, use focused interfaces)"""

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
