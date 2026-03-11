"""美股 data provider"""
from datetime import datetime
from typing import TYPE_CHECKING, cast

import pandas as pd

from value_investment.core.constants import DATE_FORMAT, HISTORICAL_DATA_TTL
from value_investment.data.providers.base_provider import (
    BaseProvider,
    get_ttl_until_june_next_year,
)

if TYPE_CHECKING:
    import akshare as ak  # type: ignore[import-untyped]
    from value_investment.data.cache import SmartCache


class USShareProvider(BaseProvider):
    """Akshare data provider for 美股 (US stocks)"""

    def __init__(self, cache, market: str = "US", **kwargs):
        """Initialize USShareProvider
        
        Args:
            cache: Cache instance
            market: Market type (default: "US")
            **kwargs: Additional arguments passed to BaseProvider
        """
        super().__init__(cache, **kwargs)
        self._market = market

    def get_stock_info(self, stock_code: str, force_refresh: bool = False) -> pd.DataFrame:
        """Get 美股 stock info"""
        import akshare as ak  # type: ignore[import-untyped]

        cache_key = f"info_{stock_code}"

        if force_refresh:
            self._cache.invalidate(cache_key)

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cast(pd.DataFrame, cached)

        # Fetch from akshare - returns item/value format directly
        data = ak.stock_individual_basic_info_us_xq(symbol=stock_code)

        self._cache.set(
            cache_key, data, ttl=get_ttl_until_june_next_year(datetime.now().year)
        )
        return data

    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "hfq",
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get 美股 historical data"""
        import akshare as ak  # type: ignore[import-untyped]

        end_date_normalized = self._normalize_date(end_date) if end_date else None
        start_date_normalized = self._normalize_date(start_date) if start_date else None

        cache_key = f"hist_us_{stock_code}"

        def fetch_full_data() -> pd.DataFrame:
            data = ak.stock_us_daily(symbol=stock_code, adjust="")

            if data is None or (hasattr(data, 'empty') and data.empty):
                return pd.DataFrame()

            data = data.rename(columns={'date': '日期'})
            data["日期"] = pd.to_datetime(data["日期"]).dt.strftime(DATE_FORMAT)
            return data

        result = self._cache.get_or_fetch_with_range(
            key=cache_key, date_column="日期", fetch_func=fetch_full_data,
            start_date=start_date_normalized, end_date=end_date_normalized,
            ttl=HISTORICAL_DATA_TTL, force_refresh=force_refresh,
        )
        return cast(pd.DataFrame, result)

    def get_balance_sheet(
        self, stock_code: str, end_year: int | None = None, start_year: int | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        import akshare as ak  # type: ignore[import-untyped]

        if end_year is None:
            end_year = datetime.now().year

        cache_key = f"balance_sheet_us_{stock_code}"

        def fetch():
            df = ak.stock_financial_us_report_em(
                stock=stock_code, symbol="资产负债表", indicator="年报"
            )
            return self._transform_us_financial_data(df)

        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(cast(pd.DataFrame, df), end_year)

    def get_income_statement(
        self, stock_code: str, end_year: int | None = None, start_year: int | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        import akshare as ak  # type: ignore[import-untyped]

        if end_year is None:
            end_year = datetime.now().year

        cache_key = f"profit_sheet_us_{stock_code}"

        def fetch():
            df = ak.stock_financial_us_report_em(
                stock=stock_code, symbol="综合损益表", indicator="年报"
            )
            return self._transform_us_financial_data(df)

        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(cast(pd.DataFrame, df), end_year)

    def get_cash_flow_statement(
        self, stock_code: str, end_year: int | None = None, start_year: int | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        import akshare as ak  # type: ignore[import-untyped]

        if end_year is None:
            end_year = datetime.now().year

        cache_key = f"cashflow_sheet_us_{stock_code}"

        def fetch():
            df = ak.stock_financial_us_report_em(
                stock=stock_code, symbol="现金流量表", indicator="年报"
            )
            return self._transform_us_financial_data(df)

        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(cast(pd.DataFrame, df), end_year)

    def _normalize_date(self, date: str | None) -> str | None:
        """Normalize date string to YYYY-MM-DD format"""
        if date is None:
            return None
        # Handle YYYYMMDD format
        if len(date) == 8 and date.isdigit():
            return f"{date[:4]}-{date[4:6]}-{date[6:8]}"
        return date

    def _transform_us_financial_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform 美股 financial data from long to wide format"""
        if df.empty:
            return df

        item_col = 'ITEM_NAME' if 'ITEM_NAME' in df.columns else 'STD_ITEM_NAME'
        if item_col not in df.columns or 'AMOUNT' not in df.columns:
            return df

        if 'REPORT_DATE' in df.columns:
            df['year'] = pd.to_datetime(df['REPORT_DATE']).dt.year

        try:
            wide_df = df.pivot_table(
                index='year',
                columns=item_col,
                values='AMOUNT',
                aggfunc='first'
            )
            wide_df = wide_df.reset_index()
            return wide_df
        except Exception:
            return df

    def _filter_by_year(self, df: pd.DataFrame, end_year: int) -> pd.DataFrame:
        """Filter DataFrame by end_year"""
        if df.empty:
            return df

        if 'year' not in df.columns:
            return df

        df = df.copy()
        df = cast(pd.DataFrame, df[df['year'] <= end_year])
        return df
