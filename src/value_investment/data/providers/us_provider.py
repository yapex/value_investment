"""US market data provider

.. deprecated::
    请使用 pipeline/data/us_provider.py 替代。
    此模块将在未来版本中移除。
"""
import warnings
from datetime import datetime
from typing import TYPE_CHECKING, cast

import pandas as pd

from value_investment.core.constants import DATE_FORMAT, HISTORICAL_DATA_TTL
from value_investment.data.mapper import DataMapper
from value_investment.data.providers.base_provider import get_ttl_until_june_next_year

if TYPE_CHECKING:
    pass


class USProvider:
    """AkShare data provider for US stocks

    .. deprecated::
        请使用 pipeline/data/us_provider.py 替代。
    """

    def __init__(self, cache, market: str = "US", **kwargs):
        warnings.warn(
            "USProvider 已deprecated，请使用 pipeline/data/us_provider.py",
            DeprecationWarning,
            stacklevel=2,
        )

    def get_stock_info(self, stock_code: str, force_refresh: bool = False) -> pd.DataFrame:
        """Get US stock info

        Args:
            stock_code: Stock ticker symbol (e.g., "AAPL")
            force_refresh: If True, force refresh from data source

        Returns:
            DataFrame with stock info
        """
        import akshare as ak  # type: ignore[import-untyped]

        cache_key = f"info_us_{stock_code}"

        if force_refresh:
            self._cache.invalidate(cache_key)

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cast(pd.DataFrame, cached)

        # Fetch from akshare
        data = ak.stock_individual_basic_info_us_xq(symbol=stock_code)

        # Cache until next June 30th
        ttl = get_ttl_until_june_next_year(datetime.now().year)
        self._cache.set(cache_key, data, ttl=ttl)
        return data

    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "hfq",
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get US stock historical data

        Args:
            stock_code: Stock ticker symbol (e.g., "AAPL")
            start_date: Start date (YYYYMMDD format)
            end_date: End date (YYYYMMDD format)
            adjust: Adjustment type (default: "hfq" for backtesting)
            force_refresh: If True, force refresh from data source

        Returns:
            DataFrame with historical prices
        """
        import akshare as ak  # type: ignore[import-untyped]

        end_date_normalized = self._normalize_date(end_date) if end_date else None
        start_date_normalized = self._normalize_date(start_date) if start_date else None

        cache_key = f"hist_us_{stock_code}"

        def fetch_full_data() -> pd.DataFrame:
            data = ak.stock_us_daily(symbol=stock_code, adjust="")

            if data is None or (hasattr(data, 'empty') and data.empty):
                return pd.DataFrame()

            # Rename date column to standard format
            data = data.rename(columns={'date': '日期'})
            data["日期"] = pd.to_datetime(data["日期"]).dt.strftime(DATE_FORMAT)
            return data

        result = self._cache.get_or_fetch_with_range(
            key=cache_key,
            date_column="日期",
            fetch_func=fetch_full_data,
            start_date=start_date_normalized,
            end_date=end_date_normalized,
            ttl=HISTORICAL_DATA_TTL,
            force_refresh=force_refresh,
        )
        return cast(pd.DataFrame, result)

    def get_balance_sheet(
        self,
        stock_code: str,
        end_year: int | None = None,
        start_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get US stock balance sheet

        Args:
            stock_code: Stock ticker symbol (e.g., "AAPL")
            end_year: End year (defaults to current year)
            start_year: Start year (ignored for AkShare)
            force_refresh: If True, force refresh from data source

        Returns:
            DataFrame with balance sheet data (mapped to standard fields)
        """
        import akshare as ak  # type: ignore[import-untyped]

        if end_year is None:
            end_year = datetime.now().year

        cache_key = f"balance_sheet_us_{stock_code}"

        def fetch():
            df = ak.stock_financial_us_report_em(
                stock=stock_code,
                symbol="资产负债表",
                indicator="年报"
            )
            # Transform from long format to wide format
            return self._transform_financial_data(df)

        df = self._cache.get_or_fetch(
            cache_key,
            fetch,
            ttl=get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )

        # Filter by year
        filtered = self._filter_by_year(cast(pd.DataFrame, df), end_year)

        # Apply field mapping
        return DataMapper.map_balance_sheet(filtered)

    def get_income_statement(
        self,
        stock_code: str,
        end_year: int | None = None,
        start_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get US stock income statement

        Args:
            stock_code: Stock ticker symbol (e.g., "AAPL")
            end_year: End year (defaults to current year)
            start_year: Start year (ignored for AkShare)
            force_refresh: If True, force refresh from data source

        Returns:
            DataFrame with income statement data (mapped to standard fields)
        """
        import akshare as ak  # type: ignore[import-untyped]

        if end_year is None:
            end_year = datetime.now().year

        cache_key = f"profit_sheet_us_{stock_code}"

        def fetch():
            df = ak.stock_financial_us_report_em(
                stock=stock_code,
                symbol="综合损益表",
                indicator="年报"
            )
            return self._transform_financial_data(df)

        df = self._cache.get_or_fetch(
            cache_key,
            fetch,
            ttl=get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )

        # Filter by year
        filtered = self._filter_by_year(cast(pd.DataFrame, df), end_year)

        # Apply field mapping
        return DataMapper.map_income_statement(filtered)

    def get_cash_flow_statement(
        self,
        stock_code: str,
        end_year: int | None = None,
        start_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get US stock cash flow statement

        Args:
            stock_code: Stock ticker symbol (e.g., "AAPL")
            end_year: End year (defaults to current year)
            start_year: Start year (ignored for AkShare)
            force_refresh: If True, force refresh from data source

        Returns:
            DataFrame with cash flow data (mapped to standard fields)
        """
        import akshare as ak  # type: ignore[import-untyped]

        if end_year is None:
            end_year = datetime.now().year

        cache_key = f"cashflow_sheet_us_{stock_code}"

        def fetch():
            df = ak.stock_financial_us_report_em(
                stock=stock_code,
                symbol="现金流量表",
                indicator="年报"
            )
            return self._transform_financial_data(df)

        df = self._cache.get_or_fetch(
            cache_key,
            fetch,
            ttl=get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )

        # Filter by year
        filtered = self._filter_by_year(cast(pd.DataFrame, df), end_year)

        # Apply field mapping
        return DataMapper.map_cash_flow(filtered)

    def get_financial_indicators(
        self,
        stock_code: str,
        end_year: int | None = None,
        start_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get US stock financial analysis indicators

        Args:
            stock_code: Stock ticker symbol (e.g., "AAPL")
            end_year: End year (defaults to current year)
            start_year: Start year (ignored for AkShare)
            force_refresh: If True, force refresh from data source

        Returns:
            DataFrame with financial indicators (mapped to standard fields)
        """
        import akshare as ak  # type: ignore[import-untyped]

        if end_year is None:
            end_year = datetime.now().year

        cache_key = f"indicator_us_{stock_code}"

        if force_refresh:
            self._cache.invalidate(cache_key)

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cast(pd.DataFrame, cached)

        # Fetch from akshare
        data = ak.stock_financial_us_analysis_indicator_em(
            symbol=stock_code,
            indicator="年报"
        )

        if data is None or (hasattr(data, 'empty') and data.empty):
            return pd.DataFrame()

        # Apply field mapping for US market
        data = DataMapper.map_financial_indicator(data, market="US")

        # Filter by year
        result = self._filter_indicators_by_year(data, end_year)

        # Cache until next June 30th
        ttl = get_ttl_until_june_next_year(datetime.now().year)
        self._cache.set(cache_key, result, ttl=ttl)
        return result

    def _normalize_date(self, date: str | None) -> str | None:
        """Normalize date string to YYYY-MM-DD format

        Args:
            date: Date string (YYYYMMDD or YYYY-MM-DD)

        Returns:
            Normalized date string (YYYY-MM-DD) or None
        """
        if date is None:
            return None
        if len(date) == 8 and date.isdigit():
            return f"{date[:4]}-{date[4:6]}-{date[6:8]}"
        return date

    def _transform_financial_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform financial data from long format to wide format

        AkShare returns data in long format with ITEM_NAME and AMOUNT columns.
        This converts it to wide format where each item becomes a column.

        Args:
            df: DataFrame with columns REPORT_DATE, ITEM_NAME, AMOUNT

        Returns:
            DataFrame in wide format with year as index and items as columns
        """
        if df.empty:
            return df

        if 'ITEM_NAME' not in df.columns or 'AMOUNT' not in df.columns:
            return df

        # Extract year from REPORT_DATE
        if 'REPORT_DATE' in df.columns:
            df['year'] = pd.to_datetime(df['REPORT_DATE']).dt.year

        # Pivot: make each item a column, AMOUNT as values, year as index
        try:
            wide_df = df.pivot_table(
                index='year',
                columns='ITEM_NAME',
                values='AMOUNT',
                aggfunc='first'
            )
            wide_df = wide_df.reset_index()
            return wide_df
        except Exception:
            return df

    def _filter_by_year(self, df: pd.DataFrame, end_year: int) -> pd.DataFrame:
        """Filter DataFrame by end_year

        Args:
            df: Input DataFrame
            end_year: End year to filter by

        Returns:
            Filtered DataFrame with data up to end_year
        """
        if df.empty:
            return df

        if 'year' not in df.columns:
            return df

        df = df.copy()
        df = cast(pd.DataFrame, df[df['year'] <= end_year])
        return df

    def _filter_indicators_by_year(self, df: pd.DataFrame, end_year: int) -> pd.DataFrame:
        """Filter financial indicators DataFrame by end_year

        Args:
            df: Input DataFrame with REPORT_DATE column
            end_year: End year to filter by

        Returns:
            Filtered DataFrame
        """
        if df.empty:
            return df

        # Try to extract year from REPORT_DATE
        if 'REPORT_DATE' not in df.columns:
            return df

        working_df = df.copy()
        working_df['year'] = pd.to_datetime(working_df['REPORT_DATE']).dt.year

        # Filter by year
        mask = working_df['year'] <= end_year
        result = working_df.loc[mask]

        # Drop temporary year column
        result = result.drop(columns=['year'], errors='ignore')

        return cast(pd.DataFrame, result)
