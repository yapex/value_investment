"""美股 Pipeline Data Provider

使用 BaseProvider Template Method 模式，自动包裹缓存逻辑。
只需实现 _fetch_* 四个方法即可。

继承关系:
    BaseProvider (Template Method) → USProvider (实现 fetch 方法)
"""
from __future__ import annotations

import warnings
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

import akshare as ak  # noqa: F401 - 模块级 import 以便测试 mock
import pandas as pd

from value_investment.core.constants import HISTORICAL_DATA_TTL
# TODO (Task 7): Update import to value_investment.mapper after restructuring
from value_investment.data.mapper import (
    FINANCIAL_INDICATOR_MAPPING,
    DataMapper,
)
from value_investment.providers.base import BaseProvider, get_ttl_until_june_next_year

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


# US Provider 支持的字段集合
US_PROVIDER_SUPPORTED_FIELDS: set[str] = {
    # === 利润表 ===
    "total_revenue",
    "net_profit",
    "operating_profit",
    "gross_profit",
    "operating_cost",
    "parent_net_profit",
    # === 资产负债表 ===
    "total_assets",
    "total_liabilities",
    "total_equity",
    "current_assets",
    "current_liabilities",
    "cash_and_equivalents",
    "inventory",
    "accounts_receivable",
    "accounts_payable",
    "fixed_assets",
    # === 现金流量表 ===
    "operating_cash_flow",
    "investing_cash_flow",
    "financing_cash_flow",
    "capital_expenditure",
    # === 财务指标 ===
    "roe",
    "roa",
    # === 市场数据 ===
    "market_cap",
    "pe_ratio",
    "pb_ratio",
    "total_shares",
    "gross_margin",
    "net_profit_margin",
    # === 每股指标 ===
    "basic_eps",
    "diluted_eps",
    "book_value_per_share",
}


class USProvider(BaseProvider):
    """美股 Pipeline Data Provider

    使用 AkShare 东财美股数据源：
    - stock_financial_us_report_em: 三大报表（年报/季报）
    - stock_financial_us_analysis_indicator_em: 财务指标

    使用 BaseProvider 的 Template Method 模式：
    - 缓存逻辑自动包裹
    - 只需实现 _fetch_* 四个方法
    """

    def __init__(self, cache: "SmartCache") -> None:
        """初始化 US Provider

        Args:
            cache: SmartCache 实例
        """
        super().__init__(cache)
        self._ak = ak

    @property
    def supported_fields(self) -> set[str]:
        """该 Provider 支持的字段集合"""
        return US_PROVIDER_SUPPORTED_FIELDS

    # ========================================================================
    # BaseProvider 抽象方法实现
    # ========================================================================

    def _fetch_balance_sheet(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取资产负债表"""
        try:
            df = self._ak.stock_financial_us_report_em(
                stock=stock_code, symbol="资产负债表", indicator="年报"
            )
            if df is None or df.empty:
                return pd.DataFrame()
            wide_df = self._transform_financial_df(df)
            mapped = DataMapper.map_balance_sheet(wide_df)
            return mapped if mapped is not None else wide_df
        except Exception:
            return pd.DataFrame()

    def _fetch_income_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取利润表"""
        try:
            df = self._ak.stock_financial_us_report_em(
                stock=stock_code, symbol="综合损益表", indicator="年报"
            )
            if df is None or df.empty:
                return pd.DataFrame()
            wide_df = self._transform_financial_df(df)
            mapped = DataMapper.map_income_statement(wide_df)
            return mapped if mapped is not None else wide_df
        except Exception:
            return pd.DataFrame()

    def _fetch_cash_flow(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取现金流量表"""
        try:
            df = self._ak.stock_financial_us_report_em(
                stock=stock_code, symbol="现金流量表", indicator="年报"
            )
            if df is None or df.empty:
                return pd.DataFrame()
            wide_df = self._transform_financial_df(df)
            mapped = DataMapper.map_cash_flow(wide_df)
            return mapped if mapped is not None else wide_df
        except Exception:
            return pd.DataFrame()

    def _fetch_indicators(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取财务指标"""
        try:
            return self._ak.stock_financial_us_analysis_indicator_em(symbol=stock_code)
        except Exception:
            return pd.DataFrame()

    def _get_date_column(self, data_type: str) -> str:
        """US Provider 使用 year 列作为日期列"""
        return "year"

    def _get_financial_ttl(self, end_year: int) -> int:
        """财务数据缓存到次年 6 月底"""
        return get_ttl_until_june_next_year(end_year)

    def _fetch_with_cache(
        self,
        data_type: str,
        stock_code: str,
        end_year: int,
        start_year: int | None,
        force_refresh: bool,
        fetch_method,
    ) -> pd.DataFrame:
        """US Provider 的年份过滤方式（重写基类方法）

        US 数据使用整数年份，不适用 pd.to_datetime 过滤。
        """
        if start_year is None:
            start_year = end_year - 10 + 1

        cache_key = self._get_cache_key(data_type, stock_code)

        if force_refresh:
            self._invalidate_cache(cache_key)

        def fetch_and_filter():
            df = fetch_method(stock_code, end_year, start_year)
            if df is None or df.empty:
                return df
            if "year" not in df.columns:
                return df
            # 整数年份过滤
            result = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
            return result

        result = self._cache.get_or_fetch(
            cache_key, fetch_and_filter, ttl=self._get_financial_ttl(end_year)
        )
        return result if result is not None else pd.DataFrame()

    # ========================================================================
    # DataProvider Protocol 方法
    # ========================================================================

    def fetch_financial_data(
        self,
        stock_code: str,
        fields: set[str],
        end_year: int,
        years: int = 10,
    ) -> dict[str, dict[int, Any]]:
        """获取财务报表数据（多年）

        Pipeline Protocol 方法。

        Returns:
            {field: {year: value}}
        """
        start_year = end_year - years + 1
        results: dict[str, dict[int, Any]] = {}

        balance_fields = self._get_balance_fields()
        income_fields = self._get_income_fields()
        cashflow_fields = self._get_cashflow_fields()

        needed = fields & (balance_fields | income_fields | cashflow_fields)
        if not needed:
            return results

        # 使用继承的 Template Method 获取数据
        if needed & balance_fields:
            df = self.get_balance_sheet(stock_code, end_year, start_year)
            self._df_add_results(df, results, needed & balance_fields)

        if needed & (income_fields - {"gross_profit", "operating_profit"}):
            df = self.get_income_statement(stock_code, end_year, start_year)
            self._df_add_results(df, results, needed & income_fields)

        if needed & cashflow_fields:
            df = self.get_cash_flow_statement(stock_code, end_year, start_year)
            self._df_add_results(df, results, needed & cashflow_fields)

        self._warn_missing_fields(fields, results)
        return results

    def fetch_indicators(
        self,
        stock_code: str,
        fields: set[str],
        end_year: int,
        years: int = 10,
    ) -> dict[str, dict[int, Any]]:
        """获取财务指标数据

        Pipeline Protocol 方法。

        Returns:
            {field: {year: value}}
        """
        hk_code = stock_code  # US uses ticker directly
        cache_key = self._get_cache_key("us_indicators", hk_code)
        ttl = get_ttl_until_june_next_year(datetime.now().year)
        results: dict[str, dict[int, Any]] = {}

        try:
            df = self._cache.get_or_fetch(
                cache_key,
                lambda: self._ak.stock_financial_us_analysis_indicator_em(symbol=hk_code),
                ttl=ttl,
            )
            if df is None or df.empty:
                return results

            current_year = datetime.now().year
            market_mapping = FINANCIAL_INDICATOR_MAPPING.get("US", {})

            for field in fields:
                # 先尝试直接在 df.columns 中查找（某些字段可能直接同名）
                if field in df.columns:
                    value = df[field].iloc[0]
                    if pd.notna(value):
                        results[field] = {current_year: value}
                    continue

                # 尝试通过映射查找
                us_field = self._find_us_field(field, market_mapping)
                if us_field and us_field in df.columns:
                    value = df[us_field].iloc[0]
                    if pd.notna(value):
                        results[field] = {current_year: value}

        except Exception:
            pass

        return results

    def fetch_market_data(
        self,
        stock_code: str,
        fields: set[str],
    ) -> dict[str, Any]:
        """获取市值数据

        Pipeline Protocol 方法。

        Returns:
            {field: value}
        """
        results: dict[str, Any] = {}

        market_fields = {
            "market_cap",
            "pe_ratio",
            "pb_ratio",
            "total_shares",
        }
        needed_fields = fields & market_fields
        if not needed_fields:
            return results

        try:
            # 尝试从 indicators API 获取
            df = self._ak.stock_financial_us_analysis_indicator_em(symbol=stock_code)
            if df is not None and not df.empty:
                for field in needed_fields:
                    if field in df.columns:
                        value = df[field].iloc[0]
                        if pd.notna(value):
                            results[field] = value
        except Exception:
            pass

        return results

    # ========================================================================
    # 私有方法
    # ========================================================================

    def _get_balance_fields(self) -> set[str]:
        return {
            "total_assets",
            "total_liabilities",
            "total_equity",
            "current_assets",
            "current_liabilities",
            "cash_and_equivalents",
            "inventory",
            "accounts_receivable",
            "accounts_payable",
            "fixed_assets",
        }

    def _get_income_fields(self) -> set[str]:
        return {
            "total_revenue",
            "parent_net_profit",
            "operating_profit",
            "operating_cost",
            "basic_eps",
            "diluted_eps",
        }

    def _get_cashflow_fields(self) -> set[str]:
        return {
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "capital_expenditure",
        }

    def _find_us_field(
        self, standard_field: str, mapping: dict[str, str]
    ) -> str | None:
        """从映射中查找 US 字段名"""
        for us_field, std_field in mapping.items():
            if std_field == standard_field:
                return us_field
        return None

    def _transform_financial_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """转换长表为宽表"""
        if df.empty:
            return df

        item_col = None
        for col in ["STD_ITEM_NAME", "ITEM_NAME"]:
            if col in df.columns:
                item_col = col
                break

        if item_col is None or "AMOUNT" not in df.columns:
            return df

        if "REPORT_DATE" in df.columns:
            df = df.copy()
            # 处理美股日期格式（如 "2023-09-30"）
            df["year"] = pd.to_datetime(df["REPORT_DATE"]).dt.year

        try:
            wide_df = df.pivot_table(
                index="year",
                columns=item_col,
                values="AMOUNT",
                aggfunc="first",
            )
            return wide_df.reset_index()  # type: ignore[return-value]
        except Exception:
            return df

    def _df_add_results(
        self,
        df: pd.DataFrame | None,
        results: dict[str, dict[int, Any]],
        fields: set[str],
    ) -> None:
        """DataFrame → {field: {year: value}}"""
        if df is None or df.empty or "year" not in df.columns:
            return

        for _, row in df.iterrows():
            year = int(row["year"])
            for field in fields:
                if field in df.columns:
                    value = row.get(field)
                    if value is not None and not isinstance(value, pd.Series):
                        try:
                            if pd.notna(value):
                                results.setdefault(field, {})[year] = float(value)
                        except (ValueError, TypeError):
                            pass

    def _warn_missing_fields(
        self,
        requested_fields: set[str],
        results: dict[str, dict[int, Any]],
    ) -> None:
        """警告缺失字段"""
        requested = set()
        for field_group in [
            self._get_balance_fields(),
            self._get_income_fields(),
            self._get_cashflow_fields(),
        ]:
            requested |= field_group

        missing = requested_fields & requested - set(results.keys())
        if missing:
            warnings.warn(
                f"以下字段无数据: {sorted(missing)}",
                UserWarning,
                stacklevel=3,
            )
