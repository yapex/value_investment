"""Base provider with field mapping and cache support

提供 Template Method 模式，自动包裹缓存逻辑。
子类只需实现 _fetch_* 四个方法。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

import pandas as pd


def get_ttl_until_june_next_year(end_year: int) -> int:
    """Get TTL in seconds until June 30th of the next year

    This gives sufficient time for financial reports to be published.

    Args:
        end_year: The end year of the financial data

    Returns:
        TTL in seconds until next year June 30th
    """
    now = datetime.now()
    # June 30th of next year
    june_next_year = datetime(now.year + 1, 6, 30, 23, 59, 59)
    return int((june_next_year - now).total_seconds())


class BaseProvider(ABC):
    """Abstract base class for all data providers

    Template Method 模式：自动包裹缓存逻辑，子类只需实现 _fetch_* 方法。

    Features:
    - Field mapping support (native fields → standard fields)
    - Cache integration with Template Method pattern
    - Common helper methods

    Subclass Usage:
        class MyProvider(BaseProvider):
            def _fetch_balance_sheet(self, stock_code, end_year, start_year):
                # 实现实际的 API 调用
                return my_api.balance_sheet(stock_code)

            def _fetch_income_statement(self, stock_code, end_year, start_year):
                return my_api.income_statement(stock_code)

            def _fetch_cash_flow(self, stock_code, end_year, start_year):
                return my_api.cash_flow(stock_code)

            def _fetch_indicators(self, stock_code, end_year, start_year):
                return my_api.indicators(stock_code)

            def _get_financial_ttl(self):
                return get_ttl_until_june_next_year(end_year)

        # 缓存逻辑自动包裹
        provider = MyProvider(cache)
        df = provider.get_balance_sheet("600519", 2024)  # 自动缓存
    """

    # 子类可覆盖的缓存年数
    DEFAULT_CACHE_YEARS = 10

    def __init__(
        self,
        cache: Any,
        field_mappings: dict[str, dict[str, str]] | None = None,
        **kwargs: Any,
    ):
        """Initialize provider

        Args:
            cache: Cache instance (SmartCache or compatible)
            field_mappings: Field name mappings by data type
            **kwargs: Additional provider-specific arguments
        """
        self._cache = cache
        self._field_mappings = field_mappings or {}
        self._init_kwargs = kwargs

    # ========================================================================
    # Template Methods (自动包裹缓存)
    # ========================================================================

    def get_balance_sheet(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """获取资产负债表（自动缓存）

        Template Method: 自动包裹缓存逻辑，子类只需实现 _fetch_balance_sheet

        Args:
            stock_code: 股票代码
            end_year: 结束年份
            start_year: 开始年份（可选，默认 end_year - 10 + 1）
            force_refresh: 是否强制刷新

        Returns:
            DataFrame with balance sheet data
        """
        return self._fetch_with_cache(
            data_type="balance",
            stock_code=stock_code,
            end_year=end_year,
            start_year=start_year,
            force_refresh=force_refresh,
            fetch_method=self._fetch_balance_sheet,
        )

    def get_income_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """获取利润表（自动缓存）

        Template Method: 自动包裹缓存逻辑，子类只需实现 _fetch_income_statement

        Args:
            stock_code: 股票代码
            end_year: 结束年份
            start_year: 开始年份（可选）
            force_refresh: 是否强制刷新

        Returns:
            DataFrame with income statement data
        """
        return self._fetch_with_cache(
            data_type="income",
            stock_code=stock_code,
            end_year=end_year,
            start_year=start_year,
            force_refresh=force_refresh,
            fetch_method=self._fetch_income_statement,
        )

    def get_cash_flow_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """获取现金流量表（自动缓存）

        Template Method: 自动包裹缓存逻辑，子类只需实现 _fetch_cash_flow

        Args:
            stock_code: 股票代码
            end_year: 结束年份
            start_year: 开始年份（可选）
            force_refresh: 是否强制刷新

        Returns:
            DataFrame with cash flow data
        """
        return self._fetch_with_cache(
            data_type="cashflow",
            stock_code=stock_code,
            end_year=end_year,
            start_year=start_year,
            force_refresh=force_refresh,
            fetch_method=self._fetch_cash_flow,
        )

    def get_financial_indicators(
        self,
        stock_code: str,
        end_year: int,
        start_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """获取财务指标（自动缓存）

        Template Method: 自动包裹缓存逻辑，子类只需实现 _fetch_indicators

        Args:
            stock_code: 股票代码
            end_year: 结束年份
            start_year: 开始年份（可选）
            force_refresh: 是否强制刷新

        Returns:
            DataFrame with financial indicators
        """
        return self._fetch_with_cache(
            data_type="indicators",
            stock_code=stock_code,
            end_year=end_year,
            start_year=start_year,
            force_refresh=force_refresh,
            fetch_method=self._fetch_indicators,
        )

    def _fetch_with_cache(
        self,
        data_type: str,
        stock_code: str,
        end_year: int,
        start_year: int | None,
        force_refresh: bool,
        fetch_method,
    ) -> pd.DataFrame:
        """Template Method 核心：自动包裹缓存逻辑

        Args:
            data_type: 数据类型（balance/income/cashflow/indicators）
            stock_code: 股票代码
            end_year: 结束年份
            start_year: 开始年份
            force_refresh: 是否强制刷新
            fetch_method: 子类实现的 fetch 方法

        Returns:
            DataFrame
        """
        if start_year is None:
            start_year = end_year - self.DEFAULT_CACHE_YEARS + 1

        cache_key = self._get_cache_key(data_type, stock_code)

        if force_refresh:
            self._invalidate_cache(cache_key)

        # 使用 get_or_fetch_with_range 自动按日期过滤
        result = self._cache.get_or_fetch_with_range(
            key=cache_key,
            date_column=self._get_date_column(data_type),
            fetch_func=lambda: fetch_method(stock_code, end_year, start_year),
            start_date=f"{start_year}-01-01",
            end_date=f"{end_year}-12-31",
            ttl=self._get_financial_ttl(end_year),
        )

        return result if result is not None else pd.DataFrame()

    # ========================================================================
    # 子类必须实现的方法
    # ========================================================================

    @abstractmethod
    def _fetch_balance_sheet(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取资产负债表（子类实现）

        Args:
            stock_code: 股票代码
            end_year: 结束年份
            start_year: 开始年份

        Returns:
            DataFrame with balance sheet data
        """
        pass

    @abstractmethod
    def _fetch_income_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取利润表（子类实现）

        Args:
            stock_code: 股票代码
            end_year: 结束年份
            start_year: 开始年份

        Returns:
            DataFrame with income statement data
        """
        pass

    @abstractmethod
    def _fetch_cash_flow(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取现金流量表（子类实现）

        Args:
            stock_code: 股票代码
            end_year: 结束年份
            start_year: 开始年份

        Returns:
            DataFrame with cash flow data
        """
        pass

    @abstractmethod
    def _fetch_indicators(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取财务指标（子类实现）

        Args:
            stock_code: 股票代码
            end_year: 结束年份
            start_year: 开始年份

        Returns:
            DataFrame with financial indicators
        """
        pass

    # ========================================================================
    # 子类可覆盖的方法
    # ========================================================================

    def _get_financial_ttl(self, end_year: int) -> int:
        """获取财务数据缓存 TTL

        子类可覆盖自定义 TTL

        Args:
            end_year: 数据结束年份

        Returns:
            TTL 秒数
        """
        return get_ttl_until_june_next_year(end_year)

    def _get_date_column(self, data_type: str) -> str:
        """获取日期列名

        子类可覆盖自定义列名

        Args:
            data_type: 数据类型

        Returns:
            日期列名
        """
        return "report_date"

    # ========================================================================
    # 辅助方法
    # ========================================================================

    def _apply_field_mapping(
        self,
        df: pd.DataFrame | None,
        statement_type: str,
    ) -> pd.DataFrame:
        """应用字段映射（使用 FIELD_MAPPINGS）

        三个 Provider 的 _fetch_* 方法调用此方法完成字段映射。

        Args:
            df: 原始数据 DataFrame
            statement_type: statement 类型 (balance_sheet/income_statement/cash_flow)

        Returns:
            映射后的 DataFrame
        """
        if df is None or df.empty:
            return pd.DataFrame()

        # 优先使用类属性 FIELD_MAPPINGS（三个 Provider 使用）
        if hasattr(self, "FIELD_MAPPINGS"):
            mapping = self.FIELD_MAPPINGS.get(statement_type, {})
        else:
            mapping = self._field_mappings.get(statement_type, {})

        rename_map = {
            native: std for native, std in mapping.items() if native in df.columns
        }
        if rename_map:
            df = df.rename(columns=rename_map)
        return df

    def get_field_mapping(self, data_type: str) -> dict[str, str]:
        """Get field mapping for a specific data type"""
        return self._field_mappings.get(data_type, {})

    def standardize_columns(
        self,
        df: pd.DataFrame | None,
        data_type: str,
    ) -> pd.DataFrame | None:
        """Standardize column names using field_mappings"""
        if df is None or df.empty:
            return df

        mapping = self.get_field_mapping(data_type)
        if not mapping:
            return df

        rename_map = {
            native: standard
            for native, standard in mapping.items()
            if native in df.columns
        }

        if rename_map:
            return df.rename(columns=rename_map)
        return df

    def _apply_mapping(
        self,
        df: pd.DataFrame | None,
        data_type: str,
    ) -> pd.DataFrame | None:
        """Apply field mapping (alias for standardize_columns)"""
        return self.standardize_columns(df, data_type)

    def get_supported_fields(self, data_type: str) -> list[str]:
        """Get list of supported standard field names for a data type"""
        mapping = self.get_field_mapping(data_type)
        return list(mapping.values())

    def _filter_latest_by_update_flag(
        self,
        df: pd.DataFrame | None,
        date_col: str = "report_date",
    ) -> pd.DataFrame | None:
        """Filter to keep only the latest records by update_flag"""
        if df is None or df.empty:
            return df

        df = df.copy()

        if "update_flag" in df.columns:
            df = df.sort_values(["update_flag"], ascending=False)
            df = df.drop_duplicates(subset=[date_col], keep="first")

        return df

    def _get_from_cache(self, key: str) -> Any | None:
        """Get data from cache"""
        try:
            return self._cache.get(key)
        except Exception:
            return None

    def _set_to_cache(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set data to cache"""
        try:
            self._cache.set(key, value, ttl=ttl)
        except Exception:
            pass

    def _invalidate_cache(self, key: str) -> None:
        """Invalidate cache entry"""
        try:
            self._cache.invalidate(key)
        except Exception:
            pass

    def _get_cache_key(self, *parts: str) -> str:
        """Build cache key from parts"""
        return ":".join(str(p) for p in parts)

    # ========================================================================
    # 可选方法（默认抛出 NotImplementedError）
    # ========================================================================

    def get_stock_info(self, stock_code: str) -> pd.DataFrame:
        """Get stock basic information"""
        raise NotImplementedError("Provider does not support stock info")

    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "",
    ) -> pd.DataFrame:
        """Get historical market data (prices, volumes)"""
        raise NotImplementedError("Provider does not support historical data")
