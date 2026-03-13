"""A股 data provider

DEPRECATED: 此模块基于 AKShare 实现，已被废弃。
请使用 tushare_provider.TushareProvider 作为 A 股数据源替代。

此模块将在未来版本中移除。
"""
import warnings
from datetime import datetime
from typing import TYPE_CHECKING, cast

import pandas as pd

from value_investment.core.constants import DATE_FORMAT, HISTORICAL_DATA_TTL
from value_investment.data.providers.base_provider import (
    BaseProvider,
    get_ttl_until_next_midnight,
    get_ttl_until_june_next_year,
)

if TYPE_CHECKING:
    pass


class AShareProvider(BaseProvider):
    """Akshare data provider for A股 (Chinese A-shares)

    .. deprecated::
        此类基于 AKShare 实现，已被废弃。
        请使用 TushareProvider 作为 A 股数据源替代。
        将在未来版本中移除。
    """

    def __init__(self, cache, market: str = "A", **kwargs):
        """Initialize AShareProvider

        Args:
            cache: Cache instance
            market: Market type (default: "A")
            **kwargs: Additional arguments passed to BaseProvider

        .. deprecated::
            此类已被废弃，请使用 TushareProvider。
        """
        warnings.warn(
            "AShareProvider 基于 AKShare 实现，已被废弃。请使用 TushareProvider 作为 A 股数据源。"
            "将在未来版本中移除。",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(cache, **kwargs)
        self._market = market

    def get_stock_info(self, stock_code: str, force_refresh: bool = False) -> pd.DataFrame:
        """Get A股 stock info

        .. deprecated:: 使用 TushareProvider.get_stock_info() 替代
        """
        import akshare as ak  # type: ignore[import-untyped]

        cache_key = f"info_{stock_code}"

        if force_refresh:
            self._cache.invalidate(cache_key)

        cached = self._cache.get(cache_key)
        if cached is not None:
            return cast(pd.DataFrame, cached)

        data = ak.stock_individual_info_em(symbol=stock_code)
        self._cache.set(cache_key, data, ttl=get_ttl_until_next_midnight())
        return data

    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "hfq",
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get A股 historical data

        .. deprecated:: 使用 TushareProvider.get_historical_data() 替代
        """
        import akshare as ak  # type: ignore[import-untyped]

        end_date_normalized = self._normalize_date(end_date) if end_date else None
        start_date_normalized = self._normalize_date(start_date) if start_date else None

        cache_key = f"hist_{stock_code}_{adjust}"

        def fetch_full_data() -> pd.DataFrame:
            tx_symbol = stock_code
            if not stock_code.startswith(("sh", "sz")):
                if stock_code.startswith(("00", "30")):
                    tx_symbol = f"sz{stock_code}"
                else:
                    tx_symbol = f"sh{stock_code}"

            data = ak.stock_zh_a_hist_tx(
                symbol=tx_symbol,
                start_date="19700101",
                end_date=end_date or "",
                adjust=adjust,
            )
            data = data.rename(columns={
                "date": "日期", "open": "开盘", "close": "收盘",
                "high": "最高", "low": "最低", "amount": "成交量",
            })
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
        """Get A股 balance sheet

        .. deprecated:: 使用 TushareProvider.get_balance_sheet() 替代
        """
        import akshare as ak  # type: ignore[import-untyped]

        if end_year is None:
            end_year = datetime.now().year

        cache_key = f"balance_sheet_a_{stock_code}"

        def fetch():
            full_symbol = self._format_stock_symbol(stock_code)
            return ak.stock_balance_sheet_by_yearly_em(symbol=full_symbol)

        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(cast(pd.DataFrame, df), end_year)

    def get_income_statement(
        self, stock_code: str, end_year: int | None = None, start_year: int | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        """Get A股 income statement

        .. deprecated:: 使用 TushareProvider.get_income_statement() 替代
        """
        import akshare as ak  # type: ignore[import-untyped]

        if end_year is None:
            end_year = datetime.now().year

        cache_key = f"profit_sheet_a_{stock_code}"

        def fetch():
            full_symbol = self._format_stock_symbol(stock_code)
            return ak.stock_profit_sheet_by_yearly_em(symbol=full_symbol)

        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(cast(pd.DataFrame, df), end_year)

    def get_cash_flow_statement(
        self, stock_code: str, end_year: int | None = None, start_year: int | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        """Get A股 cash flow statement

        .. deprecated:: 使用 TushareProvider.get_cash_flow_statement() 替代
        """
        import akshare as ak  # type: ignore[import-untyped]

        if end_year is None:
            end_year = datetime.now().year

        cache_key = f"cashflow_sheet_a_{stock_code}"

        def fetch():
            full_symbol = self._format_stock_symbol(stock_code)
            return ak.stock_cash_flow_sheet_by_yearly_em(symbol=full_symbol)

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

    def _format_stock_symbol(self, symbol: str) -> str:
        """Format stock symbol with exchange prefix"""
        if symbol.startswith(("SH", "SZ")):
            return symbol
        if symbol.startswith(("00", "30")):
            return f"SZ{symbol}"
        return f"SH{symbol}"

    def _filter_by_year(self, df: pd.DataFrame, end_year: int) -> pd.DataFrame:
        """Filter DataFrame by end_year"""
        if df.empty:
            return df

        year_col = None
        for col in ["REPORT", "year", "REPORT_DATE_NAME", "REPORT_DATE", "FISCAL_YEAR"]:
            if col in df.columns:
                year_col = col
                break

        if year_col is None:
            return df

        df = df.copy()
        try:
            if year_col == "REPORT_DATE_NAME":
                df["_year"] = pd.to_numeric(
                    df[year_col].astype(str).str.extract(r"(\d{4})")[0], errors="coerce"
                )
            elif df[year_col].dtype.kind in ['O', 'U']:
                df["_year"] = pd.to_datetime(df[year_col].astype(str), errors="coerce").dt.year
            else:
                df["_year"] = pd.to_numeric(df[year_col], errors="coerce")

            result = cast(pd.DataFrame, df[df["_year"] <= end_year].drop(columns=["_year"]))
        except Exception:
            result = df

        return result
