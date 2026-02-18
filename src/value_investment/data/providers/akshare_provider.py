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
        cache_key = f"info_{symbol}"

        # Try cache first
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Fetch from akshare
        data = ak.stock_hk_company_profile_em(symbol=symbol)

        # Convert wide format to item/value format
        # Original: single row DataFrame with columns as fields
        # Target: DataFrame with "item" and "value" columns
        items = []
        values = []

        # Add stock code
        items.append("股票代码")
        values.append(symbol)

        # Add all columns from the profile data
        for col in data.columns:
            items.append(col)
            # Get the value from the first row
            val = data.iloc[0][col]
            values.append(val)

        result = pd.DataFrame({"item": items, "value": values})

        # Cache until next June 30th (company info rarely changes)
        self._cache.set(
            cache_key, result, ttl=_get_ttl_until_june_next_year(datetime.now().year)
        )
        return result

    def _get_us_stock_info(self, symbol: str) -> pd.DataFrame:
        """Get 美股 stock info"""
        cache_key = f"info_{symbol}"

        # Try cache first
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        # Fetch from akshare - returns item/value format directly
        data = ak.stock_individual_basic_info_us_xq(symbol=symbol)

        # Cache until next June 30th (company info rarely changes)
        self._cache.set(
            cache_key, data, ttl=_get_ttl_until_june_next_year(datetime.now().year)
        )
        return data

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
        """Get A股 historical data with smart cache (full data cached, filtered on retrieval)

        Args:
            symbol: Stock code
            end_date: End date (YYYYMMDD or YYYY-MM-DD, required)
            start_date: Start date (YYYYMMDD or YYYY-MM-DD, optional, for filtering)
            adjust: Adjustment type

        Returns:
            DataFrame with historical prices
        """
        # Normalize date format to YYYY-MM-DD for filtering
        end_date_normalized = self._normalize_date(end_date)
        start_date_normalized = self._normalize_date(start_date) if start_date else None

        # Use symbol-based cache key (no end_date in key)
        cache_key = f"hist_{symbol}_{adjust}"

        def fetch_full_data() -> pd.DataFrame:
            """Fetch full historical data from akshare"""
            data = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date="19700101",  # Fetch from earliest available
                end_date=end_date,
                adjust=adjust,
            )
            # Convert date column to string for consistent format
            data["日期"] = pd.to_datetime(data["日期"]).dt.strftime("%Y-%m-%d")
            return data

        # Use smart cache with range filtering
        result = self._cache.get_or_fetch_with_range(
            key=cache_key,
            date_column="日期",
            fetch_func=fetch_full_data,
            start_date=start_date_normalized,
            end_date=end_date_normalized,
            ttl=86400 * 365,  # Cache for 1 year
        )

        return result

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
        """Get 港股 historical data with smart cache (full data cached, filtered on retrieval)

        Args:
            symbol: Stock code
            end_date: End date (YYYYMMDD or YYYY-MM-DD, required)
            start_date: Start date (YYYYMMDD or YYYY-MM-DD, optional, for filtering)
            adjust: Adjustment type (ignored for HK, kept for API compatibility)

        Returns:
            DataFrame with historical prices
        """
        # Normalize date format to YYYY-MM-DD for filtering
        end_date_normalized = self._normalize_date(end_date)
        start_date_normalized = self._normalize_date(start_date) if start_date else None

        # Use symbol-based cache key (no end_date in key)
        cache_key = f"hist_{symbol}_{adjust}"

        def fetch_full_data() -> pd.DataFrame:
            """Fetch full historical data from akshare"""
            # Convert end_date to akshare format (YYYYMMDD)
            end_date_ak = end_date.replace("-", "") if isinstance(end_date, str) else end_date
            # Use a reasonable start date for historical data
            start_date_ak = "19700101"

            data = ak.stock_hk_hist(symbol=symbol, start_date=start_date_ak, end_date=end_date_ak)
            # Convert date column to string for consistent format
            data["日期"] = pd.to_datetime(data["日期"]).dt.strftime("%Y-%m-%d")
            return data

        # Use smart cache with range filtering
        result = self._cache.get_or_fetch_with_range(
            key=cache_key,
            date_column="日期",
            fetch_func=fetch_full_data,
            start_date=start_date_normalized,
            end_date=end_date_normalized,
            ttl=86400 * 365,  # Cache for 1 year
        )

        return result

    def _get_us_historical_data(
        self,
        symbol: str,
        end_date: str,
        start_date: str | None = None,
    ) -> pd.DataFrame:
        """Get 美股 historical data"""
        # TODO: Implement US historical data
        raise NotImplementedError("US historical data not implemented yet")

    def get_balance_sheet(
        self,
        symbol: str,
        end_year: int | None = None,
    ) -> pd.DataFrame:
        """
        Get balance sheet

        Args:
            symbol: Stock code
            end_year: End year (optional, defaults to current year)

        Returns:
            DataFrame with balance sheet data
        """
        from datetime import datetime
        if end_year is None:
            end_year = datetime.now().year

        if self._market == "A":
            df = self._get_balance_sheet(symbol)
            return self._filter_by_year(df, end_year)
        elif self._market == "HK":
            df = self._get_hk_balance_sheet(symbol)
            return self._filter_by_year(df, end_year)
        elif self._market == "US":
            df = self._get_us_balance_sheet(symbol)
            return self._filter_by_year(df, end_year)
        else:
            raise NotImplementedError(f"Balance sheet for {self._market} not implemented yet")

    def get_profit_sheet(
        self,
        symbol: str,
        end_year: int | None = None,
    ) -> pd.DataFrame:
        """
        Get profit sheet (income statement)

        Args:
            symbol: Stock code
            end_year: End year (optional, defaults to current year)

        Returns:
            DataFrame with profit sheet data
        """
        from datetime import datetime
        if end_year is None:
            end_year = datetime.now().year

        if self._market == "A":
            df = self._get_profit_sheet(symbol)
            return self._filter_by_year(df, end_year)
        elif self._market == "HK":
            df = self._get_hk_profit_sheet(symbol)
            return self._filter_by_year(df, end_year)
        elif self._market == "US":
            df = self._get_us_profit_sheet(symbol)
            return self._filter_by_year(df, end_year)
        else:
            raise NotImplementedError(f"Profit sheet for {self._market} not implemented yet")

    def get_cashflow_sheet(
        self,
        symbol: str,
        end_year: int | None = None,
    ) -> pd.DataFrame:
        """
        Get cash flow sheet

        Args:
            symbol: Stock code
            end_year: End year (optional, defaults to current year)

        Returns:
            DataFrame with cash flow sheet data
        """
        from datetime import datetime
        if end_year is None:
            end_year = datetime.now().year

        if self._market == "A":
            df = self._get_cashflow_sheet(symbol)
            return self._filter_by_year(df, end_year)
        elif self._market == "HK":
            df = self._get_hk_cashflow_sheet(symbol)
            return self._filter_by_year(df, end_year)
        elif self._market == "US":
            df = self._get_us_cashflow_sheet(symbol)
            return self._filter_by_year(df, end_year)
        else:
            raise NotImplementedError(f"Cash flow sheet for {self._market} not implemented yet")

    def _filter_by_year(
        self,
        df: pd.DataFrame,
        end_year: int,
    ) -> pd.DataFrame:
        """
        Filter DataFrame by end_year

        Args:
            df: Input DataFrame
            end_year: End year to filter by

        Returns:
            Filtered DataFrame with data up to end_year
        """
        if df.empty:
            return df

        # Try to find year column - check common column names
        # Priority: REPORT (fiscal year like "2025/FY") > year > REPORT_DATE_NAME ("2024年报") > REPORT_DATE > FISCAL_YEAR
        year_col = None
        for col in ["REPORT", "year", "REPORT_DATE_NAME", "REPORT_DATE", "FISCAL_YEAR"]:
            if col in df.columns:
                year_col = col
                break

        if year_col is None:
            return df

        # Extract year from the column
        df = df.copy()
        try:
            if year_col == "REPORT":
                # For US stocks: "2025/FY" -> extract 2025
                df["_year"] = pd.to_numeric(
                    df[year_col].astype(str).str.extract(r"(\d{4})")[0],
                    errors="coerce"
                )
            elif year_col == "REPORT_DATE_NAME":
                # For A股: "2024年报" -> extract 2024
                df["_year"] = pd.to_numeric(
                    df[year_col].astype(str).str.extract(r"(\d{4})")[0],
                    errors="coerce"
                )
            elif df[year_col].dtype.kind in ['O', 'U'] or "string" in str(df[year_col].dtype):
                # For date strings like "2024-12-31" (handle StringArray by converting to str first)
                df["_year"] = pd.to_datetime(df[year_col].astype(str), errors="coerce").dt.year
            else:
                # Already numeric
                df["_year"] = pd.to_numeric(df[year_col], errors="coerce")

            # Filter: keep rows where year <= end_year (ignore NaN)
            result = df[df["_year"] <= end_year].drop(columns=["_year"])
        except Exception:
            # If anything fails, return original data
            result = df

        return result

    def _get_hk_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """Get 港股 balance sheet"""
        cache_key = f"balance_sheet_hk_{symbol}"
        ttl = _get_ttl_until_june_next_year(datetime.now().year)

        def fetch():
            return ak.stock_financial_hk_report_em(
                stock=symbol, symbol="资产负债表", indicator="年度"
            )

        return self._cache.get_or_fetch(cache_key, fetch, ttl=ttl)

    def _get_hk_profit_sheet(self, symbol: str) -> pd.DataFrame:
        """Get 港股 profit sheet (income statement)"""
        cache_key = f"profit_sheet_hk_{symbol}"
        ttl = _get_ttl_until_june_next_year(datetime.now().year)

        def fetch():
            return ak.stock_financial_hk_report_em(
                stock=symbol, symbol="利润表", indicator="年度"
            )

        return self._cache.get_or_fetch(cache_key, fetch, ttl=ttl)

    def _get_hk_cashflow_sheet(self, symbol: str) -> pd.DataFrame:
        """Get 港股 cash flow sheet"""
        cache_key = f"cashflow_sheet_hk_{symbol}"
        ttl = _get_ttl_until_june_next_year(datetime.now().year)

        def fetch():
            return ak.stock_financial_hk_report_em(
                stock=symbol, symbol="现金流量表", indicator="年度"
            )

        return self._cache.get_or_fetch(cache_key, fetch, ttl=ttl)

    def _get_us_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """Get 美股 balance sheet"""
        cache_key = f"balance_sheet_us_{symbol}"
        ttl = _get_ttl_until_june_next_year(datetime.now().year)

        def fetch():
            return ak.stock_financial_us_report_em(
                stock=symbol, symbol="资产负债表", indicator="年报"
            )

        return self._cache.get_or_fetch(cache_key, fetch, ttl=ttl)

    def _get_us_profit_sheet(self, symbol: str) -> pd.DataFrame:
        """Get 美股 profit sheet (income statement)"""
        cache_key = f"profit_sheet_us_{symbol}"
        ttl = _get_ttl_until_june_next_year(datetime.now().year)

        def fetch():
            return ak.stock_financial_us_report_em(
                stock=symbol, symbol="综合损益表", indicator="年报"
            )

        return self._cache.get_or_fetch(cache_key, fetch, ttl=ttl)

    def _get_us_cashflow_sheet(self, symbol: str) -> pd.DataFrame:
        """Get 美股 cash flow sheet"""
        cache_key = f"cashflow_sheet_us_{symbol}"
        ttl = _get_ttl_until_june_next_year(datetime.now().year)

        def fetch():
            return ak.stock_financial_us_report_em(
                stock=symbol, symbol="现金流量表", indicator="年报"
            )

        return self._cache.get_or_fetch(cache_key, fetch, ttl=ttl)

    def _get_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """Get A股 balance sheet"""
        cache_key = f"balance_sheet_a_{symbol}"
        ttl = _get_ttl_until_june_next_year(datetime.now().year)

        def fetch():
            full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
            return ak.stock_balance_sheet_by_yearly_em(symbol=full_symbol)

        return self._cache.get_or_fetch(cache_key, fetch, ttl=ttl)

    def _get_profit_sheet(self, symbol: str) -> pd.DataFrame:
        """Get A股 profit sheet (income statement)"""
        cache_key = f"profit_sheet_a_{symbol}"
        ttl = _get_ttl_until_june_next_year(datetime.now().year)

        def fetch():
            full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
            return ak.stock_profit_sheet_by_yearly_em(symbol=full_symbol)

        return self._cache.get_or_fetch(cache_key, fetch, ttl=ttl)

    def _get_cashflow_sheet(self, symbol: str) -> pd.DataFrame:
        """Get A股 cash flow sheet"""
        cache_key = f"cashflow_sheet_a_{symbol}"
        ttl = _get_ttl_until_june_next_year(datetime.now().year)

        def fetch():
            full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
            return ak.stock_cash_flow_sheet_by_yearly_em(symbol=full_symbol)

        return self._cache.get_or_fetch(cache_key, fetch, ttl=ttl)

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
