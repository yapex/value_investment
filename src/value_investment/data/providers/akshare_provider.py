"""Akshare data provider"""
import akshare as ak
import pandas as pd
from typing import TYPE_CHECKING, Optional

from value_investment.data.mapper import DataMapper

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


class AkshareProvider:
    """Akshare data provider for A股/港股/美股"""

    def __init__(self, cache: "SmartCache", market: str = "A"):
        """
        Initialize provider

        Args:
            cache: SmartCache instance
            market: Market type - "A" (A股), "HK" (港股), "US" (美股)
        """
        self._cache = cache
        self._market = market

    def get_stock_info(self, symbol: str) -> pd.DataFrame:
        """
        Get stock basic information

        Args:
            symbol: Stock code (e.g., "600519" for A股)

        Returns:
            DataFrame with stock info
        """
        if self._market == "A":
            return self._get_a_stock_info(symbol)
        elif self._market == "HK":
            return self._get_hk_stock_info(symbol)
        elif self._market == "US":
            return self._get_us_stock_info(symbol)
        else:
            raise ValueError(f"Unsupported market: {self._market}")

    def _get_a_stock_info(self, symbol: str) -> pd.DataFrame:
        """Get A股 stock info"""
        cache_key = f"info_{symbol}"

        # Try cache first
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Fetch from akshare
        data = ak.stock_individual_info_em(symbol=symbol)

        # Cache for 1 day
        self._cache.set(cache_key, data, ttl=86400)
        return data

    def _get_hk_stock_info(self, symbol: str) -> pd.DataFrame:
        """Get 港股 stock info"""
        # TODO: Implement HK stock info
        raise NotImplementedError("HK stock info not implemented yet")

    def _get_us_stock_info(self, symbol: str) -> pd.DataFrame:
        """Get 美股 stock info"""
        # TODO: Implement US stock info
        raise NotImplementedError("US stock info not implemented yet")

    def get_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str = "",
    ) -> pd.DataFrame:
        """
        Get historical price data

        Args:
            symbol: Stock code
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            adjust: Adjustment type - "" (none), "qfq" (forward), "hfq" (backward)

        Returns:
            DataFrame with historical prices
        """
        if self._market == "A":
            return self._get_a_historical_data(symbol, start_date, end_date, adjust)
        elif self._market == "HK":
            return self._get_hk_historical_data(symbol, start_date, end_date, adjust)
        elif self._market == "US":
            return self._get_us_historical_data(symbol, start_date, end_date)
        else:
            raise ValueError(f"Unsupported market: {self._market}")

    def _get_a_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str,
    ) -> pd.DataFrame:
        """Get A股 historical data"""
        cache_key = f"hist_{symbol}_{start_date}_{end_date}_{adjust}"

        # Try cache first
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Fetch from akshare
        data = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
        )

        # Cache for 1 year
        self._cache.set(cache_key, data, ttl=86400 * 365)
        return data

    def _get_hk_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        adjust: str,
    ) -> pd.DataFrame:
        """Get 港股 historical data"""
        # TODO: Implement HK historical data
        raise NotImplementedError("HK historical data not implemented yet")

    def _get_us_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """Get 美股 historical data"""
        # TODO: Implement US historical data
        raise NotImplementedError("US historical data not implemented yet")

    def get_financial_data(
        self,
        symbol: str,
        start_year: int,
        end_year: int,
    ) -> pd.DataFrame:
        """
        Get unified financial data (merged from three statements)

        Args:
            symbol: Stock code
            start_year: Start year
            end_year: End year

        Returns:
            DataFrame with merged financial data
        """
        if self._market == "A":
            return self._get_a_financial_data(symbol, start_year, end_year)
        else:
            raise NotImplementedError(f"Financial data for {self._market} not implemented yet")

    def _get_a_financial_data(
        self,
        symbol: str,
        start_year: int,
        end_year: int,
    ) -> pd.DataFrame:
        """Get A股 financial data by merging three statements"""
        # Get the three statements
        balance = self._get_balance_sheet(symbol)
        income = self._get_profit_sheet(symbol)
        cashflow = self._get_cashflow_sheet(symbol)

        # Merge into unified format
        return self._merge_financial_data(balance, income, cashflow)

    def _get_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """Get balance sheet"""
        # Add SH prefix for A股
        full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
        cache_key = f"balance_{symbol}"

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        data = ak.stock_balance_sheet_by_yearly_em(symbol=full_symbol)
        self._cache.set(cache_key, data, ttl=86400 * 365)
        return data

    def _get_profit_sheet(self, symbol: str) -> pd.DataFrame:
        """Get profit sheet (income statement)"""
        full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
        cache_key = f"income_{symbol}"

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        data = ak.stock_profit_sheet_by_yearly_em(symbol=full_symbol)
        self._cache.set(cache_key, data, ttl=86400 * 365)
        return data

    def _get_cashflow_sheet(self, symbol: str) -> pd.DataFrame:
        """Get cash flow sheet"""
        full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
        cache_key = f"cashflow_{symbol}"

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        data = ak.stock_cash_flow_sheet_by_yearly_em(symbol=full_symbol)
        self._cache.set(cache_key, data, ttl=86400 * 365)
        return data

    def _merge_financial_data(
        self,
        balance: pd.DataFrame,
        income: pd.DataFrame,
        cashflow: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Merge three financial statements into one unified DataFrame

        Args:
            balance: Balance sheet DataFrame
            income: Income statement DataFrame
            cashflow: Cash flow statement DataFrame

        Returns:
            Merged DataFrame with standardized field names
        """
        # Apply field mapping to each statement
        balance_std = DataMapper.map_balance_sheet(balance)
        income_std = DataMapper.map_income_statement(income)
        cashflow_std = DataMapper.map_cash_flow(cashflow)

        # Extract year from REPORT_DATE
        for df in [balance_std, income_std, cashflow_std]:
            if "REPORT_DATE" in df.columns:
                df["year"] = pd.to_datetime(df["REPORT_DATE"]).dt.year

        # Merge on year and security code
        merged = balance_std.merge(
            income_std,
            on=["SECURITY_CODE", "year"],
            how="outer",
            suffixes=("_balance", "_income"),
        )

        merged = merged.merge(
            cashflow_std,
            on=["SECURITY_CODE", "year"],
            how="outer",
            suffixes=("", "_cashflow"),
        )

        # Convert to standard format and sort by year
        return DataMapper.to_standard_format(merged)

    def get_financial_indicator(self, symbol: str) -> pd.DataFrame:
        """
        Get financial analysis indicators

        Args:
            symbol: Stock code

        Returns:
            DataFrame with financial indicators
        """
        if self._market != "A":
            raise NotImplementedError(f"Financial indicators for {self._market} not implemented")

        cache_key = f"indicator_{symbol}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Format symbol for A股
        full_symbol = f"{symbol}.SZ" if not symbol.startswith(("SH", "SZ")) else symbol

        data = ak.stock_financial_analysis_indicator_em(
            symbol=full_symbol,
            indicator="按报告期"
        )

        self._cache.set(cache_key, data, ttl=86400 * 365)
        return data
