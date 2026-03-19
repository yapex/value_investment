"""Tushare data provider for A 股 market

Uses TushareFieldMapper as single source of truth for field mappings.
"""
from datetime import datetime
from typing import Any

import pandas as pd

from value_investment.pipeline.data.provider import DataProvider
from value_investment.pipeline.data.tushare_mapper import TushareFieldMapper
from value_investment.pipeline.fields import IFRSFields


class TushareProvider(DataProvider):
    """Tushare data provider for A 股 market

    Uses TushareFieldMapper to map Tushare column names to standard field names.
    """

    def __init__(self, cache, token: str):
        """Initialize Tushare provider

        Args:
            cache: SmartCache instance
            token: Tushare API token
        """
        self._cache = cache
        self._token = token
        self._mapper = TushareFieldMapper()

        # Initialize Tushare API
        import tushare as ts

        ts.set_token(token)
        self._api = ts.pro_api()

    @property
    def supported_fields(self) -> set[str]:
        return self._mapper.supported_fields

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

    def _filter_latest_by_update_flag(self, df: pd.DataFrame, date_col: str = "end_date") -> pd.DataFrame:
        """Filter to keep only the latest records by update_flag
        
        For annual analysis, we need to:
        1. Filter to annual reports only (end_date ends with 1231)
        2. For same end_date, keep the one with update_flag=1 (final version)
        """
        if df.empty:
            return df

        result: pd.DataFrame = df.copy()
        
        # Filter to annual reports only (end_date = YYYY1231)
        if date_col == "end_date" and "end_date" in result.columns:
            mask = result["end_date"].str.endswith("1231")
            result = result.loc[mask]

        # For same date_col, keep update_flag=1 (final version)
        if "update_flag" in result.columns:
            result = result.sort_values(["update_flag"], ascending=False)
            result = result.drop_duplicates(subset=[date_col], keep="first")

        return result

    def _extract_year(self, df: pd.DataFrame, date_col: str = "end_date") -> pd.DataFrame:
        """Extract year from date column
        
        Uses end_date (report period end date) to determine fiscal year,
        not ann_date (announcement date), to avoid mixing quarterly reports.
        """
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

        # Determine which statement types to fetch based on requested fields
        balance_fields = fields & self._get_balance_fields()
        income_fields = fields & self._get_income_fields()
        cash_flow_fields = fields & self._get_cash_flow_fields()

        results: dict[str, dict[int, Any]] = {}

        # Fetch balance sheet data
        if balance_fields:
            balance_df = self._fetch_balance_sheet(ts_code, start_year, end_year)
            # DataFrame is already mapped to standard fields by _fetch method
            for field in balance_fields:
                if field in balance_df.columns:
                    results[field] = dict(
                        zip(balance_df["year"].astype(int), balance_df[field])
                    )

        # Fetch income statement data
        if income_fields:
            income_df = self._fetch_income_statement(ts_code, start_year, end_year)
            for field in income_fields:
                if field in income_df.columns:
                    results[field] = dict(
                        zip(income_df["year"].astype(int), income_df[field])
                    )

        # Fetch cash flow data
        if cash_flow_fields:
            cash_df = self._fetch_cash_flow(ts_code, start_year, end_year)
            for field in cash_flow_fields:
                if field in cash_df.columns:
                    results[field] = dict(
                        zip(cash_df["year"].astype(int), cash_df[field])
                    )

        return results

    def _get_balance_fields(self) -> set[str]:
        """Get standard fields mapped from balance sheet"""
        return set(self._mapper.reverse.balance_sheet.keys())

    def _get_income_fields(self) -> set[str]:
        """Get standard fields mapped from income statement"""
        return set(self._mapper.reverse.income_statement.keys())

    def _get_cash_flow_fields(self) -> set[str]:
        """Get standard fields mapped from cash flow"""
        return set(self._mapper.reverse.cash_flow.keys())

    def _fetch_balance_sheet(self, ts_code: str, start_year: int, end_year: int) -> pd.DataFrame:
        """Fetch balance sheet data from Tushare
        
        Returns DataFrame with standard field names as columns.
        """
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

        # Map to standard field names using TushareFieldMapper
        df = self._mapper.map_dataframe(df, "balance_sheet")

        # Cache for future use
        self._cache.set(cache_key, df, ttl=self._get_ttl_until_june_next_year())

        # Filter by year range
        if "year" in df.columns:
            df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    def _fetch_income_statement(self, ts_code: str, start_year: int, end_year: int) -> pd.DataFrame:
        """Fetch income statement data from Tushare
        
        Returns DataFrame with standard field names as columns.
        """
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

        # Map to standard field names using TushareFieldMapper
        df = self._mapper.map_dataframe(df, "income_statement")

        # Cache for future use
        self._cache.set(cache_key, df, ttl=self._get_ttl_until_june_next_year())

        # Filter by year range
        if "year" in df.columns:
            df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    def _fetch_cash_flow(self, ts_code: str, start_year: int, end_year: int) -> pd.DataFrame:
        """Fetch cash flow statement data from Tushare
        
        Returns DataFrame with standard field names as columns.
        """
        cache_key = f"pipeline:cashflow:{ts_code}"

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

        df = self._api.cashflow(
            ts_code=ts_code,
            start_date=f"{start_year}0101",
            end_date=today,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = self._filter_latest_by_update_flag(df)
        df = self._extract_year(df)

        # Map to standard field names using TushareFieldMapper
        df = self._mapper.map_dataframe(df, "cash_flow")

        # Cache for future use
        self._cache.set(cache_key, df, ttl=self._get_ttl_until_june_next_year())

        # Filter by year range
        if "year" in df.columns:
            df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    def fetch_indicators(
        self,
        stock_code: str,
        fields: set[str],
        end_year: int,
        years: int = 10,
    ) -> dict[str, dict[int, Any]]:
        """Fetch pre-calculated financial indicators from fina_indicator API

        Args:
            stock_code: Stock code (6-digit)
            fields: Set of standard indicator fields to fetch
            end_year: End year
            years: Number of years to fetch

        Returns:
            {field: {year: value}}
        """
        ts_code = self._to_ts_code(stock_code)
        start_year = end_year - years + 1

        # Get indicator fields that we can fetch
        indicator_fields = fields & set(self._mapper.reverse.indicators.keys())

        if not indicator_fields:
            return {}

        results: dict[str, dict[int, Any]] = {}

        # Fetch indicators data
        indicator_df = self._fetch_financial_indicators(ts_code, start_year, end_year)

        for field in indicator_fields:
            if field in indicator_df.columns:
                results[field] = dict(
                    zip(indicator_df["year"].astype(int), indicator_df[field])
                )

        return results

    def _get_indicator_fields(self) -> set[str]:
        """Get standard fields mapped from financial indicators"""
        return set(self._mapper.reverse.indicators.keys())

    def _fetch_financial_indicators(
        self, ts_code: str, start_year: int, end_year: int
    ) -> pd.DataFrame:
        """Fetch financial indicators from Tushare fina_indicator API

        Returns DataFrame with standard field names as columns.
        """
        cache_key = f"pipeline:indicators:{ts_code}"

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

        df = self._api.fina_indicator(
            ts_code=ts_code,
            start_date=f"{start_year}0101",
            end_date=today,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        # Filter to annual reports only (end_date = YYYY1231)
        # fina_indicator returns quarterly and annual data
        df = df[df["end_date"].str.endswith("1231")]

        # 去重：按 ann_date 降序排序，保留第一条（即 ann_date 最大的）
        df = df.sort_values("ann_date", ascending=False)  # type: ignore[assignment]
        df = df.drop_duplicates(subset="end_date", keep="first")

        df = self._extract_year(df)

        # Map to standard field names using TushareFieldMapper
        df = self._mapper.map_dataframe(df, "indicators")

        # Cache for future use
        self._cache.set(cache_key, df, ttl=self._get_ttl_until_june_next_year())

        # Filter by year range
        if "year" in df.columns:
            df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    def fetch_market_data(
        self,
        stock_code: str,
        fields: set[str],
    ) -> dict[str, Any]:
        """Fetch current market data (市值、PE、PB等) from daily_basic API

        Args:
            stock_code: Stock code (6-digit)
            fields: Set of market fields to fetch

        Returns:
            {field: value} 单个时间点的值
        """
        ts_code = self._to_ts_code(stock_code)

        # 获取需要的市场字段
        market_fields = fields & self._get_market_fields()

        if not market_fields:
            return {}

        # 获取市场数据
        df = self._fetch_daily_basic(ts_code)

        if df.empty:
            return {}

        # 转换为标准字段名
        df = self._mapper.map_dataframe(df, "market")

        # 提取单个值 (取最新一条)
        results: dict[str, Any] = {}
        for field in market_fields:
            if field in df.columns:
                # 取最新一条记录的值
                value = df[field].iloc[0]
                results[field] = value

        return results

    def _get_market_fields(self) -> set[str]:
        """Get standard fields from market data (daily_basic)"""
        return set(self._mapper.reverse.market.keys())

    def _fetch_daily_basic(self, ts_code: str) -> pd.DataFrame:
        """Fetch daily basic data from Tushare

        Returns DataFrame with standard field names as columns.
        """
        from datetime import timedelta

        cache_key = f"pipeline:market:{ts_code}"

        # Check cache first (短期缓存，因为是当日数据)
        cached = self._cache.get(cache_key)
        if cached is not None and not cached.empty:
            return cached

        # Fetch from Tushare - 查询最近一周的数据，取最新一条
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")

        df = self._api.daily_basic(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            fields="ts_code,trade_date,total_mv,circ_mv,total_share,circ_share,pe_ttm,pb",
        )

        if df is None or df.empty:
            return pd.DataFrame()

        # 取最新一条记录
        df = df.sort_values("trade_date", ascending=False).head(1)

        # 缓存到当日收盘 (当天不再更新)
        # TTL: 到今天 23:59:59
        now = datetime.now()
        ttl = int((datetime(now.year, now.month, now.day, 23, 59, 59) - now).total_seconds())
        self._cache.set(cache_key, df, ttl=max(ttl, 3600))

        return df
