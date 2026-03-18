"""Tushare data provider for A 股 market

Independent implementation for pipeline module.
No dependencies on existing codebase.
"""
from datetime import datetime
from typing import Any

import pandas as pd

from value_investment.pipeline.data.provider import DataProvider
from value_investment.pipeline.fields import IFRSFields


# Field mapping: standard field name -> Tushare field name
TUSHARE_BALANCE_FIELDS = {
    IFRSFields.TOTAL_ASSETS: "total_assets",
    IFRSFields.TOTAL_LIABILITIES: "total_liab",
    IFRSFields.TOTAL_EQUITY: "total_hldr_eqy_exc_min_int",
    IFRSFields.CURRENT_ASSETS: "total_cur_assets",
    IFRSFields.CURRENT_LIABILITIES: "total_cur_liab",
    IFRSFields.CASH_AND_EQUIVALENTS: "monetary_cap",
    IFRSFields.INVENTORY: "inventories",
    IFRSFields.ACCOUNTS_RECEIVABLE: "account_receiv",
    IFRSFields.ACCOUNTS_PAYABLE: "acct_payable",
    IFRSFields.FIXED_ASSETS: "fix_assets",
}

TUSHARE_INCOME_FIELDS = {
    IFRSFields.TOTAL_REVENUE: "total_revenue",
    IFRSFields.NET_PROFIT: "net_profit",
    IFRSFields.OPERATING_PROFIT: "oper_profit",
    IFRSFields.GROSS_PROFIT: "total_profit",
    IFRSFields.OPERATING_COST: "total_oper_cost",
}


class TushareProvider(DataProvider):
    """Tushare data provider for A 股 market

    Independent implementation with no dependencies on existing codebase.
    """

    def __init__(self, cache, token: str):
        """Initialize Tushare provider

        Args:
            cache: SmartCache instance
            token: Tushare API token
        """
        self._cache = cache
        self._token = token

        # Initialize Tushare API
        import tushare as ts

        ts.set_token(token)
        self._api = ts.pro_api()

    @property
    def supported_fields(self) -> set[str]:
        return set(TUSHARE_BALANCE_FIELDS.keys()) | set(TUSHARE_INCOME_FIELDS.keys())

    def _to_ts_code(self, stock_code: str) -> str:
        """Convert 6-digit stock code to ts_code format"""
        if "." in stock_code:
            return stock_code

        if len(stock_code) == 6 and stock_code.isdigit():
            if stock_code.startswith(("0", "3")):
                return f"{stock_code}.SZ"
            elif stock_code.startswith("6"):
                return f"{stock_code}.SH"

        return stock_code

    def _get_ttl_until_june_next_year(self) -> int:
        """Get TTL in seconds until June 30th of the next year"""
        now = datetime.now()
        june_next_year = datetime(now.year + 1, 6, 30, 23, 59, 59)
        return int((june_next_year - now).total_seconds())

    def _filter_latest_by_update_flag(self, df: pd.DataFrame, date_col: str = "ann_date") -> pd.DataFrame:
        """Filter to keep only the latest records by update_flag
        
        Tushare returns data with ann_date (announcement date).
        """
        if df.empty:
            return df

        df = df.copy()
        if "update_flag" in df.columns:
            df = df.sort_values(["update_flag"], ascending=False)
            df = df.drop_duplicates(subset=[date_col], keep="first")

        return df

    def _extract_year(self, df: pd.DataFrame, date_col: str = "ann_date") -> pd.DataFrame:
        """Extract year from date column"""
        if df.empty or date_col not in df.columns:
            return df

        df = df.copy()
        df["year"] = pd.to_datetime(df[date_col]).dt.year
        return df

    def fetch_financial_data(
        self,
        stock_code: str,
        fields: set[str],
        end_year: int,
        years: int = 10,
    ) -> dict[str, dict[int, Any]]:
        """Fetch financial data for specified fields

        Args:
            stock_code: Stock code (6-digit)
            fields: Set of standard field names to fetch
            end_year: End year
            years: Number of years to fetch

        Returns:
            {field: {year: value}}
        """
        ts_code = self._to_ts_code(stock_code)
        start_year = end_year - years + 1

        # Group fields by statement type
        balance_fields = fields & set(TUSHARE_BALANCE_FIELDS.keys())
        income_fields = fields & set(TUSHARE_INCOME_FIELDS.keys())

        results: dict[str, dict[int, Any]] = {}

        # Fetch balance sheet data
        if balance_fields:
            balance_df = self._fetch_balance_sheet(ts_code, start_year, end_year)
            for field in balance_fields:
                tushare_field = TUSHARE_BALANCE_FIELDS.get(field)
                if tushare_field and tushare_field in balance_df.columns:
                    results[field] = dict(
                        zip(balance_df["year"].astype(int), balance_df[tushare_field])
                    )

        # Fetch income statement data
        if income_fields:
            income_df = self._fetch_income_statement(ts_code, start_year, end_year)
            for field in income_fields:
                tushare_field = TUSHARE_INCOME_FIELDS.get(field)
                if tushare_field and tushare_field in income_df.columns:
                    results[field] = dict(
                        zip(income_df["year"].astype(int), income_df[tushare_field])
                    )

        return results

    def _fetch_balance_sheet(self, ts_code: str, start_year: int, end_year: int) -> pd.DataFrame:
        """Fetch balance sheet data from Tushare"""
        cache_key = f"pipeline:balance:{ts_code}"

        # Check cache first
        cached = self._cache.get(cache_key)
        if cached is not None and not cached.empty:
            if "year" in cached.columns:
                return cached[
                    (cached["year"] >= start_year) & (cached["year"] <= end_year)
                ]
            return cached

        # Fetch from Tushare
        today = datetime.now().strftime("%Y%m%d")

        df = self._api.balancesheet(
            ts_code=ts_code,
            start_date=f"{start_year}0101",
            end_date=today,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = self._filter_latest_by_update_flag(df)
        df = self._extract_year(df)

        # Cache for future use
        self._cache.set(cache_key, df, ttl=self._get_ttl_until_june_next_year())

        # Filter by year range
        if "year" in df.columns:
            df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    def _fetch_income_statement(self, ts_code: str, start_year: int, end_year: int) -> pd.DataFrame:
        """Fetch income statement data from Tushare"""
        cache_key = f"pipeline:income:{ts_code}"

        # Check cache first
        cached = self._cache.get(cache_key)
        if cached is not None and not cached.empty:
            if "year" in cached.columns:
                return cached[
                    (cached["year"] >= start_year) & (cached["year"] <= end_year)
                ]
            return cached

        # Fetch from Tushare
        today = datetime.now().strftime("%Y%m%d")

        df = self._api.income(
            ts_code=ts_code,
            start_date=f"{start_year}0101",
            end_date=today,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = self._filter_latest_by_update_flag(df)
        df = self._extract_year(df)

        # Cache for future use
        self._cache.set(cache_key, df, ttl=self._get_ttl_until_june_next_year())

        # Filter by year range
        if "year" in df.columns:
            df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
