"""A股 data provider"""
from datetime import datetime
from typing import TYPE_CHECKING

import akshare as ak
import pandas as pd

from value_investment.data.providers.base_provider import BaseProvider, _get_ttl_until_next_midnight, _get_ttl_until_june_next_year

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


class AShareProvider(BaseProvider):
    """Akshare data provider for A股 (Chinese A-shares)"""

    def get_stock_info(self, symbol: str, force_refresh: bool = False) -> pd.DataFrame:
        """Get A股 stock info"""
        cache_key = f"info_{symbol}"
        
        if force_refresh:
            self._cache.invalidate(cache_key)
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        data = ak.stock_individual_info_em(symbol=symbol)
        self._cache.set(cache_key, data, ttl=_get_ttl_until_next_midnight())
        return data

    def get_historical_data(
        self,
        symbol: str,
        end_date: str,
        start_date: str | None = None,
        adjust: str = "hfq",
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get A股 historical data"""
        end_date_normalized = self._normalize_date(end_date)
        start_date_normalized = self._normalize_date(start_date) if start_date else None
        
        cache_key = f"hist_{symbol}_{adjust}"
        
        def fetch_full_data() -> pd.DataFrame:
            tx_symbol = symbol
            if not symbol.startswith(("sh", "sz")):
                if symbol.startswith(("00", "30")):
                    tx_symbol = f"sz{symbol}"
                else:
                    tx_symbol = f"sh{symbol}"
            
            data = ak.stock_zh_a_hist_tx(
                symbol=tx_symbol,
                start_date="19700101",
                end_date=end_date,
                adjust=adjust,
            )
            data = data.rename(columns={
                "date": "日期", "open": "开盘", "close": "收盘",
                "high": "最高", "low": "最低", "amount": "成交量",
            })
            data["日期"] = pd.to_datetime(data["日期"]).dt.strftime("%Y-%m-%d")
            return data
        
        return self._cache.get_or_fetch_with_range(
            key=cache_key, date_column="日期", fetch_func=fetch_full_data,
            start_date=start_date_normalized, end_date=end_date_normalized,
            ttl=86400 * 365, force_refresh=force_refresh,
        )

    def get_balance_sheet(
        self, symbol: str, end_year: int | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        if end_year is None:
            end_year = datetime.now().year
        
        cache_key = f"balance_sheet_a_{symbol}"
        
        def fetch():
            full_symbol = self._format_stock_symbol(symbol)
            return ak.stock_balance_sheet_by_yearly_em(symbol=full_symbol)
        
        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=_get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(df, end_year)

    def get_income_statement(
        self, symbol: str, end_year: int | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        if end_year is None:
            end_year = datetime.now().year
        
        cache_key = f"profit_sheet_a_{symbol}"
        
        def fetch():
            full_symbol = self._format_stock_symbol(symbol)
            return ak.stock_profit_sheet_by_yearly_em(symbol=full_symbol)
        
        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=_get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(df, end_year)

    def get_cash_flow_statement(
        self, symbol: str, end_year: int | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        if end_year is None:
            end_year = datetime.now().year
        
        cache_key = f"cashflow_sheet_a_{symbol}"
        
        def fetch():
            full_symbol = self._format_stock_symbol(symbol)
            return ak.stock_cash_flow_sheet_by_yearly_em(symbol=full_symbol)
        
        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=_get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(df, end_year)

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
            
            result = df[df["_year"] <= end_year].drop(columns=["_year"])
        except Exception:
            result = df
        
        return result
