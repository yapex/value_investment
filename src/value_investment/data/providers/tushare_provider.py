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

from value_investment.core.constants import (
    HISTORICAL_DATA_TTL,
    SHANGHAI_SUFFIX,
    SHENZHEN_SUFFIX,
)
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
    HISTORICAL_DATA_TTL = HISTORICAL_DATA_TTL

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
                return f"{stock_code}{SHENZHEN_SUFFIX}"  # 深圳
            elif stock_code.startswith("6"):
                return f"{stock_code}{SHANGHAI_SUFFIX}"  # 上海

        # Return as-is if format is unknown
        return stock_code
    
    def get_balance_sheet(self, stock_code: str, end_year: int, start_year: int | None = None) -> pd.DataFrame:
        """Get balance sheet data

        Args:
            stock_code: Stock code (6-digit like "600519" or ts_code like "600519.SH")
            end_year: End year (e.g., 2023)
            start_year: Start year (optional, defaults to end_year - 15)

        Returns:
            DataFrame with balance sheet data (standard field names)
        """
        if start_year is None:
            start_year = end_year - 15

        ts_code = self._to_ts_code(stock_code)
        cache_key = self._get_cache_key("balance", stock_code, str(start_year), str(end_year))
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Fetch from tushare (不指定 fields，返回所有字段)
        df = self._api.balancesheet(
            ts_code=ts_code,
            start_date=f"{start_year}0101",
            end_date=f"{end_year}1231",
        )

        # Apply field mapping
        result = self._apply_mapping(df, "balance")

        if result is not None and not result.empty:
            ttl = get_ttl_until_june_next_year(end_year)
            self._set_to_cache(cache_key, result, ttl=ttl)
            return result

        return pd.DataFrame()

    def get_income_statement(self, stock_code: str, end_year: int, start_year: int | None = None) -> pd.DataFrame:
        """Get income statement data

        Args:
            stock_code: Stock code (6-digit like "600519" or ts_code like "600519.SH")
            end_year: End year
            start_year: Start year (optional, defaults to end_year - 15)

        Returns:
            DataFrame with income statement data
        """
        if start_year is None:
            start_year = end_year - 15

        ts_code = self._to_ts_code(stock_code)
        cache_key = self._get_cache_key("income", stock_code, str(start_year), str(end_year))
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Fetch from tushare (不指定 fields，返回所有字段)
        df = self._api.income(
            ts_code=ts_code,
            start_date=f"{start_year}0101",
            end_date=f"{end_year}1231",
        )

        # Apply field mapping
        result = self._apply_mapping(df, "income")

        if result is not None and not result.empty:
            ttl = get_ttl_until_june_next_year(end_year)
            self._set_to_cache(cache_key, result, ttl=ttl)
            return result

        return pd.DataFrame()

    def get_cash_flow_statement(self, stock_code: str, end_year: int, start_year: int | None = None) -> pd.DataFrame:
        """Get cash flow statement data

        Args:
            stock_code: Stock code (6-digit like "600519" or ts_code like "600519.SH")
            end_year: End year
            start_year: Start year (optional, defaults to end_year - 15)

        Returns:
            DataFrame with cash flow statement data
        """
        if start_year is None:
            start_year = end_year - 15

        ts_code = self._to_ts_code(stock_code)
        cache_key = self._get_cache_key("cashflow", stock_code, str(start_year), str(end_year))
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # Fetch from tushare (不指定 fields，返回所有字段)
        df = self._api.cashflow(
            ts_code=ts_code,
            start_date=f"{start_year}0101",
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
            ttl = HISTORICAL_DATA_TTL
            self._set_to_cache(cache_key, result, ttl=ttl)
            return result

        return pd.DataFrame()

    def get_quarterly_indicator(self, stock_code: str, force_refresh: bool = False) -> pd.DataFrame:
        """Get quarterly financial indicators (单季度数据)

        返回季度财务指标数据，用于计算 PE-TTM 等指标。

        Args:
            stock_code: Stock code (6-digit like "600519" or ts_code like "600519.SH")
            force_refresh: If True, force refresh from data source

        Returns:
            DataFrame with quarterly financial indicators
        """
        from datetime import datetime

        ts_code = self._to_ts_code(stock_code)
        current_year = datetime.now().year
        start_year = current_year - 10

        cache_key = self._get_cache_key("quarterly", stock_code, str(start_year), str(current_year))

        if force_refresh:
            self._cache.invalidate(cache_key)

        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # 直接调用 Tushare API 获取财务指标数据
        df = self._api.fina_indicator(
            ts_code=ts_code,
            start_date=f"{start_year}0101",
            end_date=f"{current_year}1231",
        )

        if df is None or df.empty:
            return pd.DataFrame()

        # 过滤出季度数据（end_date 不是 1231 的）
        # end_date 格式为 YYYYMMDD，年度报告是 YYYY1231
        quarterly = df[~df['end_date'].astype(str).str.endswith('1231')].copy()

        if quarterly.empty:
            return pd.DataFrame()

        # 保留 end_date 字段，映射其他字段
        from value_investment.data.mapper import DataMapper
        result = DataMapper.map_financial_indicator(pd.DataFrame(quarterly), market='A')

        # 确保 end_date 被保留（DataMapper 可能会丢弃它）
        if 'end_date' not in result.columns and 'end_date' in quarterly.columns:
            result['end_date'] = quarterly['end_date'].values

        if not result.empty:
            self._set_to_cache(cache_key, result, ttl=HISTORICAL_DATA_TTL)
            return result

        return pd.DataFrame()

    def get_daily_basic(self, stock_code: str, trade_date: str | None = None, force_refresh: bool = False) -> pd.DataFrame:
        """Get daily basic indicators (市值、股本等)

        Args:
            stock_code: Stock code (6-digit like "600519" or ts_code like "600519.SH")
            trade_date: Trade date (YYYYMMDD), defaults to latest available
            force_refresh: If True, force refresh from data source

        Returns:
            DataFrame with daily basic indicators (total_mv, total_share, etc.)
        """
        from datetime import datetime, timedelta

        ts_code = self._to_ts_code(stock_code)

        # 如果没有指定日期，获取最近的数据
        if trade_date is None:
            # 使用 ts_code 查询，获取最近一个交易日的数据
            cache_key = self._get_cache_key("daily_basic_latest", stock_code)
        else:
            cache_key = self._get_cache_key("daily_basic", stock_code, trade_date)

        if force_refresh:
            self._cache.invalidate(cache_key)

        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached

        # 调用 Tushare API
        if trade_date:
            df = self._api.daily_basic(
                ts_code=ts_code,
                trade_date=trade_date,
                fields='ts_code,trade_date,total_mv,circ_mv,total_share,circ_share,pe,pe_ttm,pb'
            )
        else:
            # 获取最近的数据：查询过去一周的数据，取最新一条
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y%m%d")
            df = self._api.daily_basic(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields='ts_code,trade_date,total_mv,circ_mv,total_share,circ_share,pe,pe_ttm,pb'
            )
            if df is not None and not df.empty:
                df = df.sort_values('trade_date', ascending=False).head(1)

        if df is None or df.empty:
            return pd.DataFrame()

        # 内部标准字段映射
        result = df.rename(columns={
            'ts_code': 'stock_code',
            'total_mv': 'total_market_cap',  # 单位：万元
            'circ_mv': 'circ_market_cap',
            'total_share': 'total_shares',  # 单位：万股
            'circ_share': 'circ_shares',
            'pe_ttm': 'pe_ttm',
        })

        # 转换单位：万 -> 个
        if 'total_shares' in result.columns:
            result['total_shares'] = result['total_shares'] * 10000
        if 'circ_shares' in result.columns:
            result['circ_shares'] = result['circ_shares'] * 10000
        if 'total_market_cap' in result.columns:
            result['total_market_cap'] = result['total_market_cap'] * 10000
        if 'circ_market_cap' in result.columns:
            result['circ_market_cap'] = result['circ_market_cap'] * 10000

        if not result.empty:
            self._set_to_cache(cache_key, result, ttl=HISTORICAL_DATA_TTL)
            return result

        return pd.DataFrame()
