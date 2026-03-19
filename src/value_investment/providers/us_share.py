"""美股 Pipeline Data Provider - IoC 模式

职责：
- 从 AKShare API 获取原始数据
- 声明 FIELD_MAPPINGS（由 Handler 执行映射）
- 缓存逻辑暂时保留在 Provider

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
from value_investment.providers.base import BaseProvider, get_ttl_until_june_next_year

if TYPE_CHECKING:
    from value_investment.core.cache import SmartCache





class USProvider(BaseProvider):
    """美股数据 Provider - IoC 模式

    职责：
    - 从 AKShare API 获取原始数据
    - 声明 FIELD_MAPPINGS（由 Handler 执行映射）
    - 缓存逻辑暂时保留
    """

    # 字段映射声明 (Handler 执行映射)
    FIELD_MAPPINGS: dict[str, dict[str, str]] = {
        "balance_sheet": {
            "总资产": "total_assets",
            "总负债": "total_liabilities",
            "流动资产合计": "current_assets",
            "非流动资产合计": "non_current_assets",
            "流动负债合计": "current_liabilities",
            "非流动负债合计": "non_current_liabilities",
            "现金及现金等价物": "cash_and_equivalents",
            "应收账款": "accounts_receivable",
            "存货": "inventory",
            "物业、厂房及设备": "fixed_assets",
            "无形资产": "intangible_assets",
            "商誉": "goodwill",
            "应付账款": "accounts_payable",
            "短期债务": "short_term_debt",
            "长期负债": "long_term_debt",
            "普通股": "common_stock",
            "优先股": "preferred_stock",
            "留存收益": "retained_earnings",
            "股本溢价": "share_premium",
            "其他综合收益": "other_comprehensive_income",
            "股东权益合计": "total_equity",
        },
        "income_statement": {
            "主营收入": "total_revenue",
            "营业收入": "operating_income",
            "主营成本": "cost_of_revenue",
            "营业成本": "operating_cost",
            "毛利": "gross_profit",
            "营业利润": "operating_profit",
            "持续经营税前利润": "profit_before_tax",
            "所得税": "income_tax",
            "持续经营净利润": "net_profit_from_continuing_operations",
            "净利润": "net_profit",
            "归属于母公司股东净利润": "net_profit",
            "归属于普通股股东净利润": "parent_net_profit",
            "每股股息-普通股": "dividend_per_share",
            "基本每股收益-普通股": "basic_eps",
            "摊薄每股收益-普通股": "diluted_eps",
        },
        "cash_flow": {
            "经营活动产生的现金流量净额": "operating_cash_flow",
            "投资活动产生的现金流量净额": "investing_cash_flow",
            "筹资活动产生的现金流量净额": "financing_cash_flow",
            "购买固定资产": "capital_expenditure",
            "净利润": "net_profit",
            "折旧及摊销": "depreciation_amortization",
        },
        "indicators": {
            # AKShare stock_financial_us_analysis_indicator_em 返回字段 -> 标准字段名
            "OPERATE_INCOME": "total_revenue",
            "GROSS_PROFIT": "gross_profit",
            "PARENT_HOLDER_NETPROFIT": "net_profit",
            "BASIC_EPS": "basic_eps",
            "DILUTED_EPS": "diluted_eps",
            "GROSS_PROFIT_RATIO": "gross_margin",
            "NET_PROFIT_RATIO": "net_profit_margin",
            "ROE_AVG": "roe",
            "ROA": "roa",
            "CURRENT_RATIO": "current_ratio",
            "SPEED_RATIO": "quick_ratio",
            "DEBT_ASSET_RATIO": "debt_ratio",
            "ACCOUNTS_RECE_TR": "receivable_turnover",
            "INVENTORY_TR": "inventory_turnover",
            "TOTAL_ASSETS_TR": "asset_turnover",
        },
        "market": {
            # AKShare stock_financial_us_analysis_indicator_em 市值相关字段 -> 标准字段名
            "MARKET_CAP": "market_cap",
            "PE_TTM": "pe_ratio",
            "PB": "pb_ratio",
            "TOTAL_SHARES": "total_shares",
        },
    }

    # Provider 支持的字段集合
    SUPPORTED_FIELDS: set[str] = {
        # 利润表
        "total_revenue",
        "net_profit",
        "parent_net_profit",
        "operating_profit",
        "gross_profit",
        "operating_cost",
        "basic_eps",
        "diluted_eps",
        # 资产负债表
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
        "intangible_assets",
        "goodwill",
        "short_term_debt",
        "long_term_debt",
        "common_stock",
        "preferred_stock",
        "retained_earnings",
        "share_premium",
        "other_comprehensive_income",
        # 现金流量表
        "operating_cash_flow",
        "investing_cash_flow",
        "financing_cash_flow",
        "capital_expenditure",
        "depreciation_amortization",
        # 财务指标
        "roe",
        "roa",
        "gross_margin",
        "net_profit_margin",
        "current_ratio",
        "quick_ratio",
        "debt_ratio",
        "asset_turnover",
        "receivable_turnover",
        # 市场数据
        "market_cap",
        "pe_ratio",
        "pb_ratio",
        "total_shares",
    }

    def __init__(self, cache: "SmartCache") -> None:
        """初始化 US Provider"""
        super().__init__(cache)
        self._ak = ak

    @property
    def supported_fields(self) -> set[str]:
        """该 Provider 支持的字段集合"""
        return self.SUPPORTED_FIELDS

    # ========================================================================
    # 原始数据获取方法 (供 Handler 调用 - 无映射)
    # ========================================================================

    def fetch_raw_balance_sheet(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取原始资产负债表数据（不做映射，返回原始字段名）"""
        try:
            df = self._ak.stock_financial_us_report_em(
                stock=stock_code, symbol="资产负债表", indicator="年报"
            )
            if df is None or df.empty:
                return pd.DataFrame()
            return self._transform_financial_df(df)
        except Exception:
            return pd.DataFrame()

    def fetch_raw_income_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取原始利润表数据（不做映射，返回原始字段名）"""
        try:
            df = self._ak.stock_financial_us_report_em(
                stock=stock_code, symbol="综合损益表", indicator="年报"
            )
            if df is None or df.empty:
                return pd.DataFrame()
            return self._transform_financial_df(df)
        except Exception:
            return pd.DataFrame()

    def fetch_raw_cash_flow(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取原始现金流量表数据（不做映射，返回原始字段名）"""
        try:
            df = self._ak.stock_financial_us_report_em(
                stock=stock_code, symbol="现金流量表", indicator="年报"
            )
            if df is None or df.empty:
                return pd.DataFrame()
            return self._transform_financial_df(df)
        except Exception:
            return pd.DataFrame()

    # ========================================================================
    # BaseProvider 抽象方法实现 (保留映射逻辑，向后兼容)
    # ========================================================================

    def _fetch_balance_sheet(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取资产负债表（带映射）"""
        df = self.fetch_raw_balance_sheet(stock_code, end_year, start_year)
        if df is None or df.empty:
            return pd.DataFrame()

        mapping = self.FIELD_MAPPINGS.get("balance_sheet", {})
        rename_map = {
            native: std for native, std in mapping.items() if native in df.columns
        }
        if rename_map:
            df = df.rename(columns=rename_map)
        return df

    def _fetch_income_statement(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取利润表（带映射）"""
        df = self.fetch_raw_income_statement(stock_code, end_year, start_year)
        if df is None or df.empty:
            return pd.DataFrame()

        mapping = self.FIELD_MAPPINGS.get("income_statement", {})
        rename_map = {
            native: std for native, std in mapping.items() if native in df.columns
        }
        if rename_map:
            df = df.rename(columns=rename_map)
        return df

    def _fetch_cash_flow(
        self,
        stock_code: str,
        end_year: int,
        start_year: int,
    ) -> pd.DataFrame:
        """获取现金流量表（带映射）"""
        df = self.fetch_raw_cash_flow(stock_code, end_year, start_year)
        if df is None or df.empty:
            return pd.DataFrame()

        mapping = self.FIELD_MAPPINGS.get("cash_flow", {})
        rename_map = {
            native: std for native, std in mapping.items() if native in df.columns
        }
        if rename_map:
            df = df.rename(columns=rename_map)
        return df

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
        """US Provider 的年份过滤方式（重写基类方法）"""
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
        """获取财务报表数据（多年）"""
        start_year = end_year - years + 1
        results: dict[str, dict[int, Any]] = {}

        balance_fields = self._get_balance_fields()
        income_fields = self._get_income_fields()
        cashflow_fields = self._get_cashflow_fields()

        needed = fields & (balance_fields | income_fields | cashflow_fields)
        if not needed:
            return results

        if needed & balance_fields:
            df = self.get_balance_sheet(stock_code, end_year, start_year)
            self._df_add_results(df, results, needed & balance_fields)

        if needed & income_fields:
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
        """获取财务指标数据"""
        cache_key = self._get_cache_key("us_indicators", stock_code)
        ttl = get_ttl_until_june_next_year(datetime.now().year)
        results: dict[str, dict[int, Any]] = {}

        try:
            df = self._cache.get_or_fetch(
                cache_key,
                lambda: self._ak.stock_financial_us_analysis_indicator_em(symbol=stock_code),
                ttl=ttl,
            )
            if df is None or df.empty:
                return results

            current_year = datetime.now().year
            mapping = self.FIELD_MAPPINGS.get("indicators", {})

            for field in fields:
                # 字段名相同的情况
                if field in df.columns:
                    value = df[field].iloc[0]
                    if pd.notna(value):
                        results[field] = {current_year: value}
                    continue

                # 反向查找：从 standard_field 找 native_field
                native_field = self._find_mapped_field(field, mapping)
                if native_field and native_field in df.columns:
                    value = df[native_field].iloc[0]
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
        """获取市值数据"""
        results: dict[str, Any] = {}

        market_fields = {"market_cap", "pe_ratio", "pb_ratio", "total_shares"}
        needed_fields = fields & market_fields
        if not needed_fields:
            return results

        try:
            df = self._ak.stock_financial_us_analysis_indicator_em(symbol=stock_code)
            if df is not None and not df.empty:
                mapping = self.FIELD_MAPPINGS.get("market", {})

                for field in needed_fields:
                    # 字段名相同的情况
                    if field in df.columns:
                        value = df[field].iloc[0]
                        if pd.notna(value):
                            results[field] = value
                        continue

                    # 反向查找：从 standard_field 找 native_field
                    native_field = self._find_mapped_field(field, mapping)
                    if native_field and native_field in df.columns:
                        value = df[native_field].iloc[0]
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
            "net_profit",
            "parent_net_profit",
            "operating_profit",
            "gross_profit",
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

    def _find_mapped_field(self, standard_field: str, mapping: dict[str, str]) -> str | None:
        """从映射表中反向查找 native 字段名

        Args:
            standard_field: 标准字段名
            mapping: {native_field: standard_field} 映射表

        Returns:
            native 字段名或 None
        """
        for native_field, std_field in mapping.items():
            if std_field == standard_field:
                return native_field
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
