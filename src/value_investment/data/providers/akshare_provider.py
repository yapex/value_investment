"""Akshare data provider"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from value_investment.data.mapper import DataMapper

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


def _get_ttl_until_next_midnight() -> int:
    """Get TTL in seconds until next midnight (for daily refresh data like stock info)"""
    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int((tomorrow - now).total_seconds())


def _get_ttl_until_june_next_year(end_year: int) -> int:
    """Get TTL in seconds until June 30th of the next year

    This gives sufficient time for financial reports to be published.

    Args:
        end_year: The end year of the financial data

    Returns:
        TTL in seconds until next year June 30th
    """
    now = datetime.now()
    # June 30th of next year
    june_next_year = datetime(now.year + 1, 6, 30, 23, 59, 59)
    return int((june_next_year - now).total_seconds())


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

    def _detect_market(self, code: str) -> Optional[str]:
        """Detect market from stock code

        Args:
            code: Stock code

        Returns:
            Market name string ("A股", "港股", "美股") or None
        """
        if not code:
            return None

        code = code.strip()

        # A股: 6-digit codes starting with 0, 3, 6
        if code.isdigit() and len(code) == 6:
            if code[0] in ("0", "3", "6"):
                return "A股"

        # 港股: 5-digit codes
        if code.isdigit() and len(code) == 5:
            return "港股"

        # 美股: alphabetic ticker symbols
        if code.isalpha():
            return "美股"

        return None

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

        # Cache until next midnight
        self._cache.set(cache_key, data, ttl=_get_ttl_until_next_midnight())
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
        end_date: str,
        start_date: str | None = None,
        adjust: str = "hfq",
    ) -> pd.DataFrame:
        """
        Get historical price data

        Args:
            symbol: Stock code
            end_date: End date (YYYYMMDD, required)
            start_date: Start date (YYYYMMDD, optional, defaults to earliest available)
            adjust: Adjustment type - "" (none), "qfq" (forward), "hfq" (backward)

        Returns:
            DataFrame with historical prices
        """
        if self._market == "A":
            return self._get_a_historical_data(symbol, end_date, start_date, adjust)
        elif self._market == "HK":
            return self._get_hk_historical_data(symbol, end_date, start_date, adjust)
        elif self._market == "US":
            return self._get_us_historical_data(symbol, end_date, start_date)
        else:
            raise ValueError(f"Unsupported market: {self._market}")

    def _get_a_historical_data(
        self,
        symbol: str,
        end_date: str,
        start_date: str | None = None,
        adjust: str = "hfq",
    ) -> pd.DataFrame:
        """Get A股 historical data with end_date-based cache

        Args:
            symbol: Stock code
            end_date: End date (YYYYMMDD or YYYY-MM-DD, required)
            start_date: Start date (YYYYMMDD or YYYY-MM-DD, optional, for filtering)
            adjust: Adjustment type

        Returns:
            DataFrame with historical prices
        """
        # Normalize date format to YYYY-MM-DD for comparison
        end_date_normalized = self._normalize_date(end_date)
        start_date_normalized = self._normalize_date(start_date) if start_date else None

        # Use end_date-based cache key
        cache_key = f"hist_{symbol}_{end_date}_{adjust}"

        # Try cache first
        cached = self._cache.get(cache_key)
        if cached is not None:
            # Filter by start_date if provided
            if start_date_normalized is not None:
                cached = cached[cached["日期"] >= start_date_normalized]
            return cached

        # Fetch full data from akshare (from earliest to end_date)
        data = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date="19700101",  # Fetch from earliest available
            end_date=end_date,
            adjust=adjust,
        )

        # Cache for 1 year
        self._cache.set(cache_key, data, ttl=86400 * 365)

        # Filter by start_date if provided
        if start_date_normalized is not None:
            data = data[data["日期"] >= start_date_normalized]

        return data

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format for comparison

        Args:
            date_str: Date string in YYYYMMDD or YYYY-MM-DD format

        Returns:
            Normalized date string in YYYY-MM-DD format
        """
        if not date_str:
            return date_str
        # If already in YYYY-MM-DD format, return as-is
        if "-" in date_str:
            return date_str
        # Convert YYYYMMDD to YYYY-MM-DD
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    def _get_hk_historical_data(
        self,
        symbol: str,
        end_date: str,
        start_date: str | None = None,
        adjust: str = "hfq",
    ) -> pd.DataFrame:
        """Get 港股 historical data"""
        # TODO: Implement HK historical data
        raise NotImplementedError("HK historical data not implemented yet")

    def _get_us_historical_data(
        self,
        symbol: str,
        end_date: str,
        start_date: str | None = None,
    ) -> pd.DataFrame:
        """Get 美股 historical data"""
        # TODO: Implement US historical data
        raise NotImplementedError("US historical data not implemented yet")

    def get_financial_data(
        self,
        symbol: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """
        Get unified financial data (merged from three statements)

        Args:
            symbol: Stock code
            end_year: End year (inclusive)
            start_year: Start year (optional, defaults to earliest available)

        Returns:
            DataFrame with merged financial data
        """
        if self._market == "A":
            return self._get_a_financial_data(symbol, end_year, start_year)
        else:
            raise NotImplementedError(f"Financial data for {self._market} not implemented yet")

    def _get_a_financial_data(
        self,
        symbol: str,
        end_year: int,
        start_year: int | None = None,
    ) -> pd.DataFrame:
        """Get A股 financial data with merged cache

        Args:
            symbol: Stock code
            end_year: End year (inclusive)
            start_year: Start year (optional, for filtering)

        Returns:
            DataFrame with merged financial data
        """
        # Use merged cache key based on end_year
        cache_key = f"financial_{symbol}_{end_year}"
        ttl = _get_ttl_until_june_next_year(end_year)

        cached = self._cache.get(cache_key)
        if cached is not None:
            # Filter by start_year if provided
            if start_year is not None:
                cached = cached[cached["year"] >= start_year]
            return cached

        # Get the three statements (still cached individually for other uses)
        balance = self._get_balance_sheet(symbol)
        income = self._get_profit_sheet(symbol)
        cashflow = self._get_cashflow_sheet(symbol)

        # Merge into unified format
        merged = self._merge_financial_data(balance, income, cashflow)

        # Cache the merged data
        self._cache.set(cache_key, merged, ttl=ttl)

        # Filter by start_year if provided
        if start_year is not None:
            merged = merged[merged["year"] >= start_year]

        return merged

    def _get_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """Get balance sheet (no separate cache, use merged cache in get_financial_data)"""
        # Add SH prefix for A股
        full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
        return ak.stock_balance_sheet_by_yearly_em(symbol=full_symbol)

    def _get_profit_sheet(self, symbol: str) -> pd.DataFrame:
        """Get profit sheet (income statement) (no separate cache, use merged cache in get_financial_data)"""
        full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
        return ak.stock_profit_sheet_by_yearly_em(symbol=full_symbol)

    def _get_cashflow_sheet(self, symbol: str) -> pd.DataFrame:
        """Get cash flow sheet (no separate cache, use merged cache in get_financial_data)"""
        full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
        return ak.stock_cash_flow_sheet_by_yearly_em(symbol=full_symbol)

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
