"""Tushare data provider for A 股 market

Tushare API documentation: https://tushare.pro/document/2

Required environment variable:
    TUSHARE_TOKEN: Your tushare API token

Usage:
    from value_investment.data.providers.tushare_provider import TushareProvider

    provider = TushareProvider(cache=cache, token="your_token")
    df = provider.get_balance_sheet("000001.SZ", 2023)
"""
import pandas as pd
import tushare as ts  # type: ignore

from value_investment.data.providers.base_provider import (
    BaseProvider,
    get_ttl_until_june_next_year,
    get_ttl_until_next_midnight,
)


class TushareProvider(BaseProvider):
    """Tushare provider for A 股 financial and market data

    Implements:
    - get_balance_sheet() - 资产负债表
    - get_income_statement() - 利润表
    - get_cash_flow_statement() - 现金流量表
    - get_historical_data() - 历史行情
    - get_stock_info() - 股票基本信息
    """

    # 缓存 TTL 常量
    HISTORICAL_DATA_TTL = 86400  # 1 天

    def __init__(self, cache, field_mappings=None, token=""):
        """Initialize Tushare provider

        Args:
            cache: Cache instance
            field_mappings: Field name mappings (from config)
            token: Tushare API token (required)
        """
        super().__init__(cache, field_mappings, token=token)

        if not token:
            raise ValueError("Tushare token is required. Set TUSHARE_TOKEN environment variable.")

        # Initialize tushare
        ts.set_token(token)
        self._api = ts.pro_api()

    def _to_ts_code(self, stock_code: str) -> str:
        """Convert 6-digit stock code to ts_code format

        Args:
            stock_code: 6-digit code (e.g., "600519", "000001") or already formatted code (e.g., "600519.SH")

        Returns:
            ts_code format (e.g., "600519.SH", "000001.SZ")
        """
        # Already in ts_code format
        if "." in stock_code:
            return stock_code

        # 6-digit code conversion
        if len(stock_code) == 6 and stock_code.isdigit():
            if stock_code.startswith(("0", "3")):
                return f"{stock_code}.SZ"  # 深圳
            elif stock_code.startswith("6"):
                return f"{stock_code}.SH"  # 上海

        # Return as-is if format is unknown
        return stock_code
    
    def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get balance sheet data

        Args:
            stock_code: Stock code (6-digit like "600519" or ts_code like "600519.SH")
            end_year: End year (e.g., 2023)

        Returns:
            DataFrame with balance sheet data (standard field names)
        """
        ts_code = self._to_ts_code(stock_code)
        cache_key = self._get_cache_key("balance", stock_code, str(end_year))
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Fetch from tushare (不指定 fields，返回所有字段)
        df = self._api.balancesheet(
            ts_code=ts_code,
            start_date=f"{end_year - 5}0101",
            end_date=f"{end_year}1231",
        )

        # Apply field mapping
        result = self._apply_mapping(df, "balance")

        if result is not None and not result.empty:
            ttl = get_ttl_until_june_next_year(end_year)
            self._set_to_cache(cache_key, result, ttl=ttl)
            return result

        return pd.DataFrame()
    
    def get_income_statement(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get income statement data

        Args:
            stock_code: Stock code (6-digit like "600519" or ts_code like "600519.SH")
            end_year: End year

        Returns:
            DataFrame with income statement data
        """
        ts_code = self._to_ts_code(stock_code)
        cache_key = self._get_cache_key("income", stock_code, str(end_year))
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Fetch from tushare (不指定 fields，返回所有字段)
        df = self._api.income(
            ts_code=ts_code,
            start_date=f"{end_year - 5}0101",
            end_date=f"{end_year}1231",
        )

        # Apply field mapping
        result = self._apply_mapping(df, "income")

        if result is not None and not result.empty:
            ttl = get_ttl_until_june_next_year(end_year)
            self._set_to_cache(cache_key, result, ttl=ttl)
            return result

        return pd.DataFrame()
    
    def get_cash_flow_statement(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get cash flow statement data

        Args:
            stock_code: Stock code (6-digit like "600519" or ts_code like "600519.SH")
            end_year: End year

        Returns:
            DataFrame with cash flow statement data
        """
        ts_code = self._to_ts_code(stock_code)
        cache_key = self._get_cache_key("cashflow", stock_code, str(end_year))
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Fetch from tushare (不指定 fields，返回所有字段)
        df = self._api.cashflow(
            ts_code=ts_code,
            start_date=f"{end_year - 5}0101",
            end_date=f"{end_year}1231",
        )

        # Apply field mapping
        result = self._apply_mapping(df, "cashflow")

        if result is not None and not result.empty:
            ttl = get_ttl_until_june_next_year(end_year)
            self._set_to_cache(cache_key, result, ttl=ttl)
            return result

        return pd.DataFrame()
    
    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "",
    ) -> pd.DataFrame:
        """Get historical market data (daily prices)

        Args:
            stock_code: Stock code (6-digit like "600519" or ts_code like "600519.SH")
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            adjust: Adjustment type ("", "qfq", "hfq")

        Returns:
            DataFrame with historical data (open, high, low, close, volume)
        """
        ts_code = self._to_ts_code(stock_code)
        cache_key = self._get_cache_key(
            "market", stock_code,
            start_date or "all",
            end_date or "latest",
            adjust or "none"
        )
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # 使用 ts.pro_bar() 获取历史数据
        adj_param = adjust if adjust in ("qfq", "hfq") else None

        df = ts.pro_bar(
            ts_code=ts_code,
            start_date=start_date or "20100101",
            end_date=end_date or "20991231",
            adj=adj_param,
        )

        # 如果 pro_bar 失败，回退到 daily 接口（无复权）
        if df is None or df.empty:
            df = self._api.daily(
                ts_code=ts_code,
                start_date=start_date or "20100101",
                end_date=end_date or "20991231",
            )

        # Apply field mapping
        result = self._apply_mapping(df, "market")

        if result is not None and not result.empty:
            self._set_to_cache(cache_key, result, ttl=self.HISTORICAL_DATA_TTL)
            return result

        return pd.DataFrame()
    
    def get_stock_info(self, stock_code: str) -> pd.DataFrame:
        """Get stock basic information

        Args:
            stock_code: Stock code (6-digit like "600519" or ts_code like "600519.SH")

        Returns:
            DataFrame with stock info
        """
        ts_code = self._to_ts_code(stock_code)
        cache_key = self._get_cache_key("info", stock_code)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Fetch from tushare (不指定 fields，返回所有字段)
        df = self._api.stock_basic(
            ts_code=ts_code,
        )

        # Apply field mapping
        result = self._apply_mapping(df, "info")

        if result is not None and not result.empty:
            ttl = get_ttl_until_next_midnight()
            self._set_to_cache(cache_key, result, ttl=ttl)
            return result

        return pd.DataFrame()

    def get_financial_indicator(self, stock_code: str, start_year: int = 2018, end_year: int | None = None, force_refresh: bool = False) -> pd.DataFrame:
        """Get financial indicators from Tushare fina_indicator API

        Tushare fina_indicator provides 137 financial indicator fields including:
        - Per share metrics (eps, bps, cfps, etc.)
        - Profitability ratios (roe, roa, gross_margin, etc.)
        - Solvency ratios (current_ratio, quick_ratio, debt_to_assets, etc.)
        - Efficiency ratios (inventory_turnover, receivables_turnover, etc.)
        - Cash flow metrics (ebit, ebitda, fcff, fcfe, etc.)
        - Growth indicators (yoy, qoq)

        Args:
            stock_code: Stock code (6-digit like "600519" or ts_code like "600519.SH")
            start_year: Start year for data retrieval (default: 2018)
            end_year: End year for data retrieval (default: current year)

        Returns:
            DataFrame with financial indicator data (standard field names via mapping)
        """
        ts_code = self._to_ts_code(stock_code)
        if end_year is None:
            from datetime import datetime
            end_year = datetime.now().year

        cache_key = self._get_cache_key("finind", stock_code, str(start_year), str(end_year))
        
        if force_refresh:
            self._cache.invalidate(cache_key)
        
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Fetch from tushare fina_indicator API
        df = self._api.fina_indicator(
            ts_code=ts_code,
            start_date=f"{start_year}0101",
            end_date=f"{end_year}1231",
        )

        if df is None or df.empty:
            return pd.DataFrame()

        # Apply field mapping using DataMapper (A 股市场)
        from value_investment.data.mapper import DataMapper
        result = DataMapper.map_financial_indicator(df, market='A')

        if result is not None and not result.empty:
            # 缓存1年
            ttl = 86400 * 365
            self._set_to_cache(cache_key, result, ttl=ttl)
            return result

        return pd.DataFrame()
