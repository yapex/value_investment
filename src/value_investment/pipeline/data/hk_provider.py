"""港股 Pipeline Data Provider

使用 BaseProvider Template Method 模式，自动包裹缓存逻辑。
只需实现 _fetch_* 四个方法即可。

继承关系:
    BaseProvider (Template Method) → HKProvider (实现 fetch 方法)
                                → TushareProvider (实现 fetch 方法)
"""
from __future__ import annotations

import warnings
from datetime import datetime
from typing import TYPE_CHECKING, Any, cast

import akshare as ak  # noqa: F401 - 模块级 import 以便测试 mock
import pandas as pd

from value_investment.core.constants import HISTORICAL_DATA_TTL
from value_investment.data.mapper import (
    FINANCIAL_INDICATOR_MAPPING,
    DataMapper,
)
from value_investment.data.providers.base_provider import (
    BaseProvider,
    get_ttl_until_june_next_year,
)
from value_investment.pipeline.data.provider import DataProvider

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


# HK Provider 支持的字段集合
HK_PROVIDER_SUPPORTED_FIELDS: set[str] = {
    # === 利润表 ===
    "total_revenue",
    "net_profit",
    "operating_profit",
    "gross_profit",
    "operating_cost",
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
    "gross_margin",
    "net_profit_margin",
    # === 市场数据 ===
    "market_cap",
    "pe_ratio",
    "pb_ratio",
    "total_shares",
    "basic_eps",
    "diluted_eps",
    "book_value_per_share",
    # === 港股特有 ===
    "hk_market_cap",
    "hk_dividend_per_share",
    "hk_dividend_yield_ttm",
    "hk_dividend_payout_ratio",
    "hk_total_revenue_growth_qoq",
    "hk_net_profit_growth_qoq",
}


class HKProvider(BaseProvider, DataProvider):
    """港股 Pipeline Data Provider

    使用 BaseProvider 的 Template Method 模式：
    - 缓存逻辑自动包裹
    - 只需实现 _fetch_* 四个方法
    """

    def __init__(self, cache: "SmartCache") -> None:
        """初始化 HK Provider

        Args:
            cache: SmartCache 实例
        """
        super().__init__(cache)
        self._ak = ak

    @property
    def supported_fields(self) -> set[str]:
        """该 Provider 支持的字段集合"""
        return HK_PROVIDER_SUPPORTED_FIELDS

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
        hk_code = self._normalize_hk_code(stock_code)
        try:
            df = self._ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="资产负债表", indicator="年度"
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
        hk_code = self._normalize_hk_code(stock_code)
        try:
            df = self._ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="利润表", indicator="年度"
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
        hk_code = self._normalize_hk_code(stock_code)
        try:
            df = self._ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="现金流量表", indicator="年度"
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
        """获取财务指标（仅当年）"""
        hk_code = self._normalize_hk_code(stock_code)
        try:
            return self._ak.stock_hk_financial_indicator_em(symbol=hk_code)
        except Exception:
            return pd.DataFrame()

    def _get_date_column(self, data_type: str) -> str:
        """HK Provider 使用 year 列作为日期列"""
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
        """HK Provider 的年份过滤方式（重写基类方法）

        HK 数据使用整数年份，不适用 pd.to_datetime 过滤。
        """
        if start_year is None:
            start_year = end_year - 10 + 1  # DEFAULT_CACHE_YEARS

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
    # 可选方法实现
    # ========================================================================

    def get_stock_info(self, stock_code: str) -> pd.DataFrame:
        """获取股票基本信息（带缓存）"""
        hk_code = self._normalize_hk_code(stock_code)
        cache_key = self._get_cache_key("hk_stock_info", hk_code)
        ttl = get_ttl_until_june_next_year(datetime.now().year)

        def fetch() -> pd.DataFrame:
            return self._ak.stock_hk_company_profile_em(symbol=hk_code)

        result = self._cache.get_or_fetch(cache_key, fetch, ttl=ttl)
        return cast(pd.DataFrame, result)

    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = "",
    ) -> pd.DataFrame:
        """获取历史交易数据（带缓存）

        .. deprecated::
            港股历史交易数据建议使用 yfinance (YFinanceProvider)。
        """
        warnings.warn(
            "港股历史交易数据建议使用 YFinanceProvider。"
            "AKShare 的港股历史数据接口不够稳定。",
            DeprecationWarning,
            stacklevel=2,
        )
        hk_code = self._normalize_hk_code(stock_code)
        cache_key = self._get_cache_key("hk_historical", hk_code, adjust or "none")

        def fetch() -> pd.DataFrame:
            data = self._ak.stock_hk_daily(symbol=hk_code)
            return data.rename(
                columns={
                    "date": "日期",
                    "open": "开盘",
                    "close": "收盘",
                    "high": "最高",
                    "low": "最低",
                    "volume": "成交量",
                }
            )

        result = self._cache.get_or_fetch(cache_key, fetch, ttl=HISTORICAL_DATA_TTL)
        return cast(pd.DataFrame, result)

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
        """获取财务指标数据（仅当年）

        Pipeline Protocol 方法。

        Returns:
            {field: {year: value}}
        """
        warnings.warn(
            f"AkShare 港股财务指标 API 只返回最新一年数据，"
            f"多年历史指标请使用 Calculator 计算",
            UserWarning,
            stacklevel=2,
        )

        hk_code = self._normalize_hk_code(stock_code)
        cache_key = self._get_cache_key("hk_indicators", hk_code)
        ttl = get_ttl_until_june_next_year(datetime.now().year)
        results: dict[str, dict[int, Any]] = {}

        try:
            df = self._cache.get_or_fetch(
                cache_key,
                lambda: self._ak.stock_hk_financial_indicator_em(symbol=hk_code),
                ttl=ttl,
            )
            if df is None or df.empty:
                return results

            current_year = datetime.now().year
            market_mapping = FINANCIAL_INDICATOR_MAPPING.get("HK", {})

            for field in fields:
                hk_field = self._find_hk_field(field, market_mapping)
                if hk_field is None:
                    if field in df.columns:
                        value = df[field].iloc[0]
                        if pd.notna(value):
                            results[field] = {current_year: value}
                    continue

                if hk_field in df.columns:
                    value = df[hk_field].iloc[0]
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
        hk_code = self._normalize_hk_code(stock_code)
        results: dict[str, Any] = {}

        market_fields = {
            "market_cap",
            "hk_market_cap",
            "pe_ratio",
            "pb_ratio",
            "total_shares",
            "hk_dividend_yield_ttm",
            "hk_dividend_payout_ratio",
            "hk_dividend_per_share",
        }
        needed_fields = fields & market_fields
        if not needed_fields:
            return results

        cache_key = self._get_cache_key("hk_indicators", hk_code)
        ttl = get_ttl_until_june_next_year(datetime.now().year)

        try:
            df = self._cache.get_or_fetch(
                cache_key,
                lambda: self._ak.stock_hk_financial_indicator_em(symbol=hk_code),
                ttl=ttl,
            )
            if df is None or df.empty:
                return results

            market_mapping = FINANCIAL_INDICATOR_MAPPING.get("HK", {})

            for field in needed_fields:
                # Special handling for market_cap: use 总市值(港元) directly
                if field == "market_cap":
                    if "总市值(港元)" in df.columns:
                        value = df["总市值(港元)"].iloc[0]
                        if pd.notna(value):
                            results["market_cap"] = value
                    continue

                hk_field = self._find_hk_field(field, market_mapping)
                if hk_field is None:
                    if field in df.columns:
                        value = df[field].iloc[0]
                        if pd.notna(value):
                            results[field] = value
                    continue

                if hk_field in df.columns:
                    value = df[hk_field].iloc[0]
                    if pd.notna(value):
                        if field == "hk_market_cap":
                            results["market_cap"] = value
                        else:
                            results[field] = value

        except Exception:
            pass

        return results

    # ========================================================================
    # 私有方法
    # ========================================================================

    def _normalize_hk_code(self, symbol: str) -> str:
        """标准化港股代码为 5 位数字格式"""
        if not symbol:
            return symbol
        digits = "".join(c for c in symbol if c.isdigit())
        if len(digits) < 5:
            digits = digits.zfill(5)
        return digits

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
        """港股净利润对应 parent_net_profit"""
        return {
            "total_revenue",
            "parent_net_profit",
            "operating_profit",
            "operating_cost",
        }

    def _get_cashflow_fields(self) -> set[str]:
        return {
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "capital_expenditure",
        }

    def _find_hk_field(self, standard_field: str, mapping: dict[str, str]) -> str | None:
        for hk_field, std_field in mapping.items():
            if std_field == standard_field:
                return hk_field
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
