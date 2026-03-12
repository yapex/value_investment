"""股票 Scanner - 用于批量获取和筛选股票数据

为 Agent 提供简单易用的 API 来获取全市场股票数据并进行筛选。
"""
import os
from datetime import datetime
from typing import List, Optional
import pandas as pd
import tushare as ts
from value_investment.core.rate_limiter import RateLimiter
from value_investment.data.cache import SmartCache


class Scanner:
    """股票数据扫描器

    提供获取全市场股票列表和批量财务数据的功能，内置速率限制和缓存。

    Example:
        >>> from value_investment import Scanner
        >>> scanner = Scanner(market="A")
        >>> stocks = scanner.get_stock_list()
        >>> financials = scanner.get_financial_data(stocks['code'], fields=['roe'], years=5)
    """

    def __init__(self, market: str = "A", cache_dir: Optional[str] = None):
        """初始化 Scanner

        Args:
            market: 市场类型，"A" 表示 A 股
            cache_dir: 缓存目录路径，默认使用项目缓存
        """
        self.market = market
        self._cache = SmartCache(cache_dir=cache_dir or "./.cache")
        self._rate_limiter = RateLimiter(max_calls_per_minute=200)

        # 初始化 Tushare
        token = os.getenv("TUSHARE_TOKEN", "")
        if not token:
            raise ValueError("TUSHARE_TOKEN environment variable is required")
        ts.set_token(token)
        self._api = ts.pro_api()

    def get_stock_list(self) -> pd.DataFrame:
        """获取全市场股票列表

        Returns:
            DataFrame with columns: ts_code, symbol, name, area, industry, list_date
        """
        cache_key = "scanner_all_stocks"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        self._rate_limiter.wait_if_needed()
        df = self._api.stock_basic(
            exchange='',
            list_status='L',  # 上市
            fields='ts_code,symbol,name,area,industry,list_date'
        )

        if df is not None and not df.empty:
            # 缓存到次年 6 月底 - 与财务数据缓存统一过期时间，避免碎片化
            from value_investment.data.providers.base_provider import get_ttl_until_june_next_year
            self._cache.set(cache_key, df, ttl=get_ttl_until_june_next_year(datetime.now().year))

        return df

    def get_financial_data(
        self,
        stocks: List[str],
        fields: List[str],
        years: int = 5
    ) -> pd.DataFrame:
        """批量获取股票财务数据

        Args:
            stocks: 股票代码列表（6 位数字格式，如 ['600519', '000001']）
            fields: 需要的字段列表（如 ['roe', 'gross_margin']）
            years: 获取年数，默认最近 5 年

        Returns:
            DataFrame with financial data, columns include: stock_code, end_date, and requested fields
        """
        # 转换为 Tushare 格式
        ts_codes = [self._to_ts_code(s) for s in stocks]
        return self._get_financial_data_batch(ts_codes, fields, years)

    def _get_financial_data_batch(
        self,
        ts_codes: List[str],
        fields: List[str],
        years: int
    ) -> pd.DataFrame:
        """内部方法：批量获取财务指标数据"""
        from datetime import datetime

        end_year = datetime.now().year
        start_year = end_year - years + 1

        all_data = []

        for i, ts_code in enumerate(ts_codes):
            # 每 50 只报告进度
            if i % 50 == 0 and i > 0:
                status = self._rate_limiter.get_status()
                print(f"  已处理 {i}/{len(ts_codes)} 只，剩余配额 {status['remaining']}")

            # 检查缓存
            cache_key = f"scanner_finind_{ts_code}_{start_year}_{end_year}"
            cached = self._cache.get(cache_key)

            if cached is not None:
                all_data.append(cached)
                continue

            # 速率限制
            self._rate_limiter.wait_if_needed()

            try:
                df = self._api.fina_indicator(
                    ts_code=ts_code,
                    start_date=f"{start_year}0101",
                    end_date=f"{end_year}1231"
                )

                if df is not None and not df.empty:
                    # 只保留年报数据
                    annual = df[df['end_date'].astype(str).str.endswith('1231')].copy()
                    if not annual.empty:
                        # 添加标准化股票代码
                        annual['stock_code'] = ts_code.replace('.SH', '').replace('.SZ', '')

                        # 只保留需要的字段
                        keep_cols = ['stock_code', 'end_date'] + fields
                        available_cols = [c for c in keep_cols if c in annual.columns]
                        annual = annual[available_cols]

                        all_data.append(annual)

                        # 缓存
                        from value_investment.data.providers.base_provider import get_ttl_until_june_next_year
                        self._cache.set(cache_key, annual, ttl=get_ttl_until_june_next_year(end_year))

            except Exception as e:
                print(f"  获取 {ts_code} 失败：{e}")
                continue

        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()

    def _to_ts_code(self, stock_code: str) -> str:
        """转换为 Tushare 代码格式"""
        if "." in stock_code:
            return stock_code

        if len(stock_code) == 6 and stock_code.isdigit():
            if stock_code.startswith(("0", "3")):
                return f"{stock_code}.SZ"
            elif stock_code.startswith("6"):
                return f"{stock_code}.SH"

        return stock_code
