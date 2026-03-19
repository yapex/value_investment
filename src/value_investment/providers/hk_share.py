"""港股 Pipeline Data Provider - IoC 模式

职责：
- 从 AKShare API 获取原始数据
- 声明 FIELD_MAPPINGS（由 Handler 执行映射）
- 缓存逻辑暂时保留在 Provider

继承关系:
    BaseProvider (Template Method) → HKProvider (实现 fetch 方法)
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





class HKProvider(BaseProvider):
    """港股数据 Provider - IoC 模式

    职责：
    - 从 AKShare API 获取原始数据
    - 声明 FIELD_MAPPINGS（由 Handler 执行映射）
    - 缓存逻辑暂时保留
    """

    # 字段映射声明 (Handler 执行映射)
    # 结构: {statement_type: {native_field: standard_field}}
    FIELD_MAPPINGS: dict[str, dict[str, str]] = {
        "balance_sheet": {
            "资产总值": "total_assets",
            "总负债": "total_liabilities",
            "权益总额": "total_equity",
            "流动资产合计": "current_assets",
            "非流动资产合计": "non_current_assets",
            "流动负债合计": "current_liabilities",
            "非流动负债合计": "non_current_liabilities",
            "现金及等价物": "cash_and_equivalents",
            "应收帐款": "accounts_receivable",
            "存货": "inventory",
            "固定资产": "fixed_assets",
            "物业厂房及设备": "fixed_assets",
            "无形资产": "intangible_assets",
            "短期贷款": "short_term_debt",
            "长期贷款": "long_term_debt",
            "应付帐款": "accounts_payable",
            "股东权益": "shareholders_equity",
            "股本": "share_capital",
            "股本溢价": "share_premium",
            "保留溢利(累计亏损)": "retained_earnings",
            "在建工程": "construction_in_progress",
            "联营公司权益": "investment_in_associates",
            "合营公司权益": "investment_in_joint_ventures",
            "预付款项": "prepayment",
            "合同资产": "contract_assets",
            "合同负债": "contract_liab",
            "预收款项": "adv_receipts",
        },
        "income_statement": {
            "收益": "total_revenue",
            "营业额": "total_revenue",
            "经营溢利": "operating_profit",
            "毛利": "gross_profit",
            "除税前溢利": "profit_before_tax",
            "除税后溢利": "profit_after_tax",
            "股东应占溢利": "parent_net_profit",
            "行政开支": "administrative_expenses",
            "销售及分销费用": "selling_distribution_expenses",
            "融资成本": "finance_cost",
            "利息收入": "interest_income",
            "折旧及摊销": "depreciation_amortization",
        },
        "cash_flow": {
            "经营业务现金净额": "operating_cash_flow",
            "投资业务现金净额": "investing_cash_flow",
            "融资业务现金净额": "financing_cash_flow",
            "购建固定资产": "capital_expenditure",
            "购建无形资产及其他资产": "capital_expenditure_intangible",
            "已付利息(经营)": "interest_paid_operating",
            "已付利息(融资)": "interest_paid_financing",
            "已付税项": "taxes_paid",
            "已收利息(投资)": "interest_received",
            "已收股息(投资)": "dividend_received",
            "期初现金": "cash_begin",
            "期末现金": "cash_end",
            "现金净额": "net_cash_change",
        },
        "indicators": {
            # AKShare stock_hk_financial_indicator_em 返回字段 -> 标准字段名
            "总市值(港元)": "hk_market_cap",
            "港股市值(港元)": "hk_market_cap",
            "基本每股收益(元)": "basic_eps",
            "每股净资产(元)": "book_value_per_share",
            "每股经营现金流(元)": "operating_cash_flow_per_share",
            "每股股息TTM(港元)": "hk_dividend_per_share",
            "股东权益回报率(%)": "roe",
            "销售净利率(%)": "net_profit_margin",
            "总资产回报率(%)": "roa",
            "市盈率": "pe_ratio",
            "市净率": "pb_ratio",
            "股息率TTM(%)": "hk_dividend_yield_ttm",
            "营业总收入滚动环比增长(%)": "hk_total_revenue_growth_qoq",
            "净利润滚动环比增长(%)": "hk_net_profit_growth_qoq",
            "派息比率(%)": "hk_dividend_payout_ratio",
            # 标准字段也支持
            "营业总收入": "total_revenue",
            "净利润": "net_profit",
        },
        "market": {
            # AKShare stock_hk_financial_indicator_em 市值相关字段 -> 标准字段名
            "总市值(港元)": "market_cap",
            "港股市值(港元)": "market_cap",
            "市盈率": "pe_ratio",
            "市净率": "pb_ratio",
            "股息率TTM(%)": "hk_dividend_yield_ttm",
            "派息比率(%)": "hk_dividend_payout_ratio",
            "每股股息TTM(港元)": "hk_dividend_per_share",
        },
    }

    # Provider 支持的字段集合
    SUPPORTED_FIELDS: set[str] = {
        # 利润表
        "total_revenue",
        "net_profit",
        "operating_profit",
        "gross_profit",
        "operating_cost",
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
        "non_current_assets",
        "non_current_liabilities",
        "short_term_debt",
        "long_term_debt",
        "intangible_assets",
        "shareholders_equity",
        "share_capital",
        "share_premium",
        "retained_earnings",
        "construction_in_progress",
        "investment_in_associates",
        "investment_in_joint_ventures",
        "prepayment",
        "contract_assets",
        "contract_liab",
        "adv_receipts",
        # 现金流量表
        "operating_cash_flow",
        "investing_cash_flow",
        "financing_cash_flow",
        "capital_expenditure",
        "capital_expenditure_intangible",
        # 财务指标
        "roe",
        "roa",
        "gross_margin",
        "net_profit_margin",
        # 市场数据
        "market_cap",
        "pe_ratio",
        "pb_ratio",
        "total_shares",
        "hk_dividend_per_share",
        "hk_dividend_yield_ttm",
        "hk_dividend_payout_ratio",
        "hk_total_revenue_growth_qoq",
        "hk_net_profit_growth_qoq",
    }

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
        hk_code = self._normalize_hk_code(stock_code)
        try:
            df = self._ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="资产负债表", indicator="年度"
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
        hk_code = self._normalize_hk_code(stock_code)
        try:
            df = self._ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="利润表", indicator="年度"
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
        hk_code = self._normalize_hk_code(stock_code)
        try:
            df = self._ak.stock_financial_hk_report_em(
                stock=hk_code, symbol="现金流量表", indicator="年度"
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
        # 调用 fetch_raw_* 获取原始数据，然后手动映射
        df = self.fetch_raw_balance_sheet(stock_code, end_year, start_year)
        if df is None or df.empty:
            return pd.DataFrame()

        # 手动应用映射
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
            mapping = self.FIELD_MAPPINGS.get("indicators", {})

            for field in fields:
                # 反向查找：从 standard_field 找 native_field
                native_field = self._find_mapped_field(field, mapping)
                if native_field is None:
                    # 字段名相同的情况
                    if field in df.columns:
                        value = df[field].iloc[0]
                        if pd.notna(value):
                            results[field] = {current_year: value}
                    continue

                if native_field in df.columns:
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

            mapping = self.FIELD_MAPPINGS.get("market", {})

            for field in needed_fields:
                # 反向查找：从 standard_field 找 native_field
                native_field = self._find_mapped_field(field, mapping)
                if native_field is None:
                    if field in df.columns:
                        value = df[field].iloc[0]
                        if pd.notna(value):
                            results[field] = value
                    continue

                if native_field in df.columns:
                    value = df[native_field].iloc[0]
                    if pd.notna(value):
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
        return {
            "total_revenue",
            "net_profit",
            "parent_net_profit",
            "operating_profit",
            "gross_profit",
            "operating_cost",
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
