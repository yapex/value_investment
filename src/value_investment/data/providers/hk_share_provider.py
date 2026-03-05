"""港股 data provider"""
from datetime import datetime
from typing import TYPE_CHECKING

import akshare as ak
import pandas as pd

from value_investment.data.providers.base_provider import BaseProvider, _get_ttl_until_june_next_year

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


class HKShareProvider(BaseProvider):
    """Akshare data provider for 港股 (Hong Kong stocks)"""

    def get_stock_info(self, symbol: str, force_refresh: bool = False) -> pd.DataFrame:
        """Get 港股 stock info"""
        cache_key = f"info_{symbol}"
        
        if force_refresh:
            self._cache.invalidate(cache_key)
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Normalize to 5-digit format
        hk_code = self._normalize_hk_code(symbol)
        
        # Fetch from akshare
        data = ak.stock_hk_company_profile_em(symbol=hk_code)
        
        # Convert wide format to item/value format
        items = ["股票代码"]
        values = [symbol]
        
        for col in data.columns:
            items.append(col)
            val = data.iloc[0][col]
            values.append(val)
        
        result = pd.DataFrame({"item": items, "value": values})
        
        self._cache.set(
            cache_key, result, ttl=_get_ttl_until_june_next_year(datetime.now().year)
        )
        return result

    def _normalize_hk_code(self, symbol: str) -> str:
        """Normalize HK stock code to 5-digit format"""
        if not symbol:
            return symbol
        digits = ''.join(c for c in symbol if c.isdigit())
        if len(digits) < 5:
            digits = digits.zfill(5)
        return digits

    def get_historical_data(
        self,
        symbol: str,
        end_date: str,
        start_date: str | None = None,
        adjust: str = "hfq",
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get 港股 historical data"""
        end_date_normalized = self._normalize_date(end_date)
        start_date_normalized = self._normalize_date(start_date) if start_date else None
        
        cache_key = f"hist_{symbol}_{adjust}"
        
        def fetch_full_data() -> pd.DataFrame:
            hk_code = self._normalize_hk_code(symbol)
            data = ak.stock_hk_daily(symbol=hk_code)
            data = data.rename(columns={
                "date": "日期", "open": "开盘", "close": "收盘",
                "high": "最高", "low": "最低", "volume": "成交量",
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
        
        hk_code = self._normalize_hk_code(symbol)
        cache_key = f"balance_sheet_hk_{hk_code}"
        
        def fetch():
            df = ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="资产负债表", indicator="年度"
            )
            return self._transform_hk_financial_data(df)
        
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
        
        hk_code = self._normalize_hk_code(symbol)
        cache_key = f"profit_sheet_hk_{hk_code}"
        
        def fetch():
            df = ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="利润表", indicator="年度"
            )
            return self._transform_hk_financial_data(df)
        
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
        
        hk_code = self._normalize_hk_code(symbol)
        cache_key = f"cashflow_sheet_hk_{hk_code}"
        
        def fetch():
            df = ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="现金流量表", indicator="年度"
            )
            return self._transform_hk_financial_data(df)
        
        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=_get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(df, end_year)

    def _transform_hk_financial_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform 港股 financial data from long to wide format"""
        if df.empty:
            return df
        
        item_col = 'STD_ITEM_NAME' if 'STD_ITEM_NAME' in df.columns else 'ITEM_NAME'
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
        df = df[df['year'] <= end_year]
        return df
