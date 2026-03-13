"""股票 Scanner - 用于批量获取和筛选股票数据

为 Agent 提供简单易用的 API 来获取全市场股票数据并进行筛选。
"""
from __future__ import annotations

import hashlib
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional
import pandas as pd
import tushare as ts

from value_investment.core.container import Container, get_financial_provider
from value_investment.core.rate_limiter import RateLimiter
from value_investment.indicators.registry import IndicatorRegistry, register_defaults


def _generate_filter_hash(filter_text: str) -> str:
    """生成过滤条件的稳定 hash

    Args:
        filter_text: 过滤条件文本

    Returns:
        8位十六进制 hash 字符串
    """
    # 使用 MD5 生成稳定 hash，取前8位
    hash_obj = hashlib.md5(filter_text.encode('utf-8'))
    return hash_obj.hexdigest()[:8]


def _generate_scan_cache_key(filter_text: str, fields: List[str], years: int, market: str) -> str:
    """生成扫描结果的缓存键

    Args:
        filter_text: 过滤条件文本
        fields: 查询字段列表
        years: 查询年数
        market: 市场标识 (A/HK)

    Returns:
        缓存键字符串
    """
    filter_hash = _generate_filter_hash(filter_text)
    # 字段排序后用下划线连接
    fields_str = "_".join(sorted(fields))
    return f"scan_result_{filter_hash}_{fields_str}_{years}_{market}"


class Scanner:
    """股票数据扫描器

    提供获取全市场股票列表和批量财务数据的功能，内置速率限制和缓存。

    Example:
        >>> from value_investment import Scanner
        >>> scanner = Scanner(market="A")
        >>> stocks = scanner.get_stock_list()
        >>> financials = scanner.get_financial_data(stocks['symbol'].tolist(), fields=['roe'], years=5)
    """

    def __init__(self, market: str = "A", cache_dir: Optional[str] = None):
        """初始化 Scanner

        Args:
            market: 市场类型，"A" 表示 A 股，"HK" 表示港股
            cache_dir: 缓存目录路径，默认使用项目缓存
        """
        # 注册默认指标（确保字段映射可用）
        register_defaults()

        self.market = market

        # 使用 Container 管理依赖
        self._container = Container()
        if cache_dir:
            self._container.config.cache_dir.from_value(cache_dir)

        # 从 Container 获取 provider
        self._provider = get_financial_provider(self._container, market)
        self._cache = self._container.cache()

        # 速率限制器
        self._rate_limiter = RateLimiter(max_calls_per_minute=200)

        # 指标注册表
        self._registry = IndicatorRegistry.get_instance()

        # A 股使用 Tushare API（港股使用 AKShareProvider）
        if market == "A":
            import os
            token = os.getenv("TUSHARE_TOKEN", "")
            if not token:
                raise ValueError("TUSHARE_TOKEN environment variable is required")
            ts.set_token(token)
            self._api = ts.pro_api()
        else:
            self._api = None

    def get_stock_list(self) -> pd.DataFrame:
        """获取全市场股票列表

        Returns:
            DataFrame with columns: ts_code, symbol, name, area, industry, list_date
        """
        # 港股：从 akshare 动态获取（缓存到次年 6 月底）
        if self.market == "HK":
            cache_key = "scanner_hk_stocks"
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached
            
            # 从 akshare 获取港股列表
            from value_investment.scanner.data.hk_shares import get_hk_stock_list_from_akshare
            df = get_hk_stock_list_from_akshare()
            
            if df is not None and not df.empty:
                # 缓存到次年 6 月底
                from value_investment.data.providers.base_provider import get_ttl_until_june_next_year
                self._cache.set(cache_key, df, ttl=get_ttl_until_june_next_year(datetime.now().year))
                return df
            
            # Fallback: 如果 akshare 失败，返回空的 DataFrame
            return pd.DataFrame()

        # A 股：使用 Tushare API
        cache_key = "scanner_aa_stocks"  # 全 A 股（排除北交所）
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        self._rate_limiter.wait_if_needed()
        df = self._api.stock_basic(
            exchange='',
            list_status='L',
            fields='ts_code,symbol,name,area,industry,list_date'
        )

        if df is not None and not df.empty:
            # 过滤掉北交所股票（8、9 开头）
            mask = ~df['symbol'].str.startswith(('8', '9'))
            df = df.loc[mask].copy()

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
            fields: 需要的字段列表（使用标准字段名，如 ['roe', 'gross_profit_margin']）
            years: 获取年数，默认最近 5 年

        Returns:
            DataFrame with financial data in standard format
        """
        # 港股：使用 AKShareProvider
        if self.market == "HK":
            return self._get_hk_financial_data(stocks, fields, years)
        
        # A 股：使用 Tushare API
        ts_fields = self._to_ts_fields(fields)

        ts_codes = [self._to_ts_code(s) for s in stocks]
        df = self._get_financial_data_batch(ts_codes, ts_fields, years)

        # 将 Tushare 字段名映射回标准字段名
        if not df.empty:
            df = self._map_to_standard_fields(df, fields)

        return df
    
    def scan(
        self,
        stocks: List[str],
        fields: List[str],
        filters: Any,
        years: int = 5,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """获取数据并应用过滤条件

        这是 get_financial_data + 过滤的便捷方法。

        Args:
            stocks: 股票代码列表
            fields: 需要的字段列表
            filters: FilterBuilder 构建的过滤条件
            years: 获取年数，默认 5 年
            use_cache: 是否使用缓存，默认 True

        Returns:
            过滤后的 DataFrame

        Example:
            >>> from value_investment.scanner.pipeline import FilterBuilder
            >>>
            >>> # 构建过滤条件
            >>> fb = FilterBuilder()
            >>> fb.add_filter('latest_year', field='roe', min_value=15)
            >>> fb.add_filter('consecutive_years', field='gross_profit_margin', min_value=30, years=5)
            >>>
            >>> # 扫描并过滤
            >>> scanner = Scanner(market='A')
            >>> result = scanner.scan(stocks=['600519', '000858'], fields=['roe'], filters=fb)
        """
        # 获取财务数据
        df = self.get_financial_data(stocks, fields, years)

        if df.empty:
            return df

        # 应用过滤条件（使用显式方法，遵循 ISP 原则）
        # 如果 filters 有 set_cache 和 set_market 方法，使用它们
        if hasattr(filters, 'set_cache') and hasattr(filters, 'set_market'):
            filters.set_cache(self._cache).set_market(self.market)
        
        result = filters.execute(df, use_cache=use_cache)

        return result

    def cache_scan_result(
        self,
        filter_text: str,
        fields: List[str],
        years: int,
        result: pd.DataFrame
    ) -> None:
        """缓存扫描结果

        Args:
            filter_text: 过滤条件文本
            fields: 查询字段列表
            years: 查询年数
            result: 扫描结果 DataFrame
        """
        cache_key = _generate_scan_cache_key(filter_text, fields, years, self.market)
        # 使用 1 天 TTL
        self._cache.set(cache_key, result, ttl=86400)

    def get_cached_scan_result(
        self,
        filter_text: str,
        fields: List[str],
        years: int
    ) -> Optional[pd.DataFrame]:
        """获取缓存的扫描结果

        Args:
            filter_text: 过滤条件文本
            fields: 查询字段列表
            years: 查询年数

        Returns:
            缓存的 DataFrame，如果不存在则返回 None
        """
        cache_key = _generate_scan_cache_key(filter_text, fields, years, self.market)
        return self._cache.get(cache_key)

    def list_cached_scan_results(self) -> List[str]:
        """列出所有缓存的扫描结果键

        Returns:
            缓存键列表
        """
        all_keys = self._cache.list_keys()
        return [k for k in all_keys if k.startswith("scan_result_")]
    
    def _get_hk_financial_data(
        self,
        stocks: List[str],
        fields: List[str],
        years: int
    ) -> pd.DataFrame:
        """获取港股财务数据（从三表计算）

        使用港股三表数据计算财务指标，支持多年历史数据。
        """
        from value_investment.data.providers.base_provider import get_ttl_until_june_next_year
        from value_investment.indicators.hk import (
            calculate_hk_roe,
            calculate_hk_roic,
            calculate_hk_gross_profit_margin,
            calculate_hk_net_profit_margin,
            merge_hk_financial_data
        )

        all_data = []

        for i, stock_code in enumerate(stocks):
            if i % 50 == 0 and i > 0:
                print(f"  已处理 {i}/{len(stocks)} 只")

            # 标准化为 5 位代码
            hk_code = self._normalize_hk_code(stock_code)

            # 检查缓存
            cache_key = f"scanner_hk_finind_{hk_code}_{years}"
            cached = self._cache.get(cache_key)

            if cached is not None:
                all_data.append(cached)
                continue

            try:
                # 获取三表数据
                balance = self._provider.get_balance_sheet(hk_code)
                income = self._provider.get_profit_sheet(hk_code)
                cashflow = self._provider.get_cashflow_sheet(hk_code)

                if balance is None or balance.empty:
                    continue

                # 合并三表
                merged = merge_hk_financial_data(balance, income, cashflow)

                # 只保留最近 N 年的数据
                if 'year' in merged.columns:
                    merged = merged.sort_values('year', ascending=False).head(years)

                # 根据请求的字段计算指标
                result_rows = []

                for _, row in merged.iterrows():
                    year = row.get('year', 0)
                    if year:
                        end_date = f"{int(year)}1231"
                    else:
                        continue

                    row_data = {
                        'stock_code': hk_code,
                        'end_date': end_date,
                    }

                    # ROE
                    if 'roe' in [f.lower() for f in fields]:
                        roe_df = calculate_hk_roe(income, balance)
                        roe_value = roe_df[roe_df['year'] == year]['roe'].values
                        if len(roe_value) > 0:
                            row_data['roe'] = roe_value[0]

                    # ROIC
                    if 'roic' in [f.lower() for f in fields]:
                        roic_df = calculate_hk_roic(income, balance)
                        roic_value = roic_df[roic_df['year'] == year]['roic'].values
                        if len(roic_value) > 0:
                            row_data['roic'] = roic_value[0]

                    # 毛利率
                    if 'gross_profit_margin' in [f.lower() for f in fields]:
                        gpm_df = calculate_hk_gross_profit_margin(income)
                        gpm_value = gpm_df[gpm_df['year'] == year]['gross_profit_margin'].values
                        if len(gpm_value) > 0:
                            row_data['gross_profit_margin'] = gpm_value[0]

                    # 净利率
                    if 'net_profit_margin' in [f.lower() for f in fields]:
                        npm_df = calculate_hk_net_profit_margin(income)
                        npm_value = npm_df[npm_df['year'] == year]['net_profit_margin'].values
                        if len(npm_value) > 0:
                            row_data['net_profit_margin'] = npm_value[0]

                    result_rows.append(row_data)

                if result_rows:
                    df = pd.DataFrame(result_rows)
                    all_data.append(df)

                    # 缓存
                    self._cache.set(cache_key, df, ttl=get_ttl_until_june_next_year(datetime.now().year))

            except Exception as e:
                print(f"  获取 {hk_code} 失败：{e}")
                continue

        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            return result
        return pd.DataFrame()
    
    def _normalize_hk_code(self, stock_code: str) -> str:
        """标准化港股代码为 5 位格式"""
        digits = ''.join(c for c in stock_code if c.isdigit())
        if len(digits) < 5:
            digits = digits.zfill(5)
        return digits

    def _to_ts_fields(self, fields: List[str]) -> List[str]:
        """将标准字段名转换为 Tushare 字段名"""
        ts_fields = []
        for field in fields:
            indicator = self._registry.get(field)
            if indicator and indicator.market_fields:
                # 使用 'A股' 作为 key（与 registry 中定义一致）
                ts_field = indicator.market_fields.get('A股', field)
                ts_fields.append(ts_field)
            else:
                # 如果没有注册，直接使用原字段名
                ts_fields.append(field)
        return ts_fields

    def _map_to_standard_fields(self, df: pd.DataFrame, standard_fields: List[str]) -> pd.DataFrame:
        """将 Tushare 字段名映射回标准字段名"""
        df = df.copy()
        ts_fields = self._to_ts_fields(standard_fields)

        rename_map = {}
        for standard, ts_field in zip(standard_fields, ts_fields):
            if ts_field in df.columns and standard != ts_field:
                rename_map[ts_field] = standard

        if rename_map:
            df = df.rename(columns=rename_map)

        return df

    def _get_financial_data_batch(
        self,
        ts_codes: List[str],
        fields: List[str],
        years: int
    ) -> pd.DataFrame:
        """内部方法：批量获取财务指标数据"""
        # 年报通常在次年 4 月发布，所以使用 current_year - 2 作为最新年报年份
        # 例如：2026 年 3 月，最新年报是 2024 年
        current_year = datetime.now().year
        current_month = datetime.now().month

        # 如果是 1-3 月，最新年报是前年的；4 月及以后，最新年报是去年的
        if current_month < 4:
            end_year = current_year - 2
        else:
            end_year = current_year - 1

        start_year = end_year - years + 1

        # 将 fields 排序后加入缓存 key，确保相同股票不同字段不会冲突
        fields_key = "_".join(sorted(fields))

        all_data = []

        # 预检查：获取所有缓存键，尝试批量匹配
        all_cache_keys = set(self._cache.list_keys())
        
        # 构建缓存键前缀
        cache_prefix = f"scanner_finind_"
        cache_suffix = f"_{fields_key}_{start_year}_{end_year}"
        
        # 如果缓存命中率足够高，直接批量处理
        cache_hit_count = 0
        missing_codes = []
        
        for ts_code in ts_codes:
            cache_key = f"{cache_prefix}{ts_code}{cache_suffix}"
            if cache_key in all_cache_keys:
                cached = self._cache.get(cache_key)
                if cached is not None and not cached.empty:
                    all_data.append(cached)
                    cache_hit_count += 1
                    continue
            missing_codes.append(ts_code)
        
        # 如果缓存命中率 >= 90%，跳过 API 调用（避免速率限制）
        cache_hit_rate = cache_hit_count / len(ts_codes) if ts_codes else 0
        
        if cache_hit_rate >= 0.90 and missing_codes:
            print(f"  缓存命中率 {cache_hit_rate:.1%}，跳过 {len(missing_codes)} 只未缓存股票")
            if all_data:
                return pd.concat(all_data, ignore_index=True)
            return pd.DataFrame()
        
        if cache_hit_rate >= 0.90 and not missing_codes:
            # 所有数据都在缓存中，直接返回
            if all_data:
                return pd.concat(all_data, ignore_index=True)
            return pd.DataFrame()
        
        # 否则继续逐个处理未命中的股票（这通常是首次运行）
        for i, ts_code in enumerate(missing_codes):
            # 每 50 只报告进度
            if i % 50 == 0 and i > 0:
                status = self._rate_limiter.get_status()
                print(f"  已处理 {i}/{len(missing_codes)} 只，剩余配额 {status['remaining']}")

            cache_key = f"{cache_prefix}{ts_code}{cache_suffix}"
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
                    # 过滤 update_flag：优先使用 update_flag=1（更新过的数据）
                    if 'update_flag' in df.columns:
                        df = df.sort_values('update_flag', ascending=False).drop_duplicates(subset=['end_date'], keep='first')

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
