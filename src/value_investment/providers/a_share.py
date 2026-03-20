"""Tushare data provider for A 股 market - IoC 模式

声明 FIELD_MAPPINGS（由 Handler 执行映射）。
所有字段映射已硬编码，不再依赖 TushareFieldMapper。
"""
from datetime import datetime
from typing import Any

import pandas as pd

from value_investment.providers.base import BaseProvider


class TushareProvider(BaseProvider):
    """Tushare data provider for A 股 market - IoC 模式

    职责：
    - 从 Tushare API 获取原始数据
    - 声明 FIELD_MAPPINGS（由 Handler 执行映射）
    - 缓存逻辑暂时保留
    """

    # 所有支持的字段（硬编码，移除了 TushareFieldMapper 依赖）
    # 来源: balance_sheet + income_statement + cash_flow + indicators + market
    SUPPORTED_FIELDS: set[str] = {
        # --- 资产负债表 ---
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
        "prepayment",
        "contract_assets",
        "contract_liab",
        "adv_receipts",
        "total_shares",
        # --- 资产负债表 (Phase 1) ---
        "goodwill",
        "intangible_assets",
        "long_term_investment",
        "construction_in_progress",
        # --- 利润表 ---
        "total_revenue",
        "net_profit",
        "operating_profit",
        "operating_cost",
        "parent_net_profit",
        # --- 现金流量表 ---
        "operating_cash_flow",
        "investing_cash_flow",
        "financing_cash_flow",
        "capital_expenditure",
        # --- 财务指标 (fina_indicator) ---
        "roe",
        "roa",
        "gross_margin",
        "net_profit_margin",
        "current_ratio",
        "quick_ratio",
        "debt_ratio",
        "asset_turnover",
        "receivable_turnover",
        "roic",
        "basic_eps",
        "diluted_eps",
        "book_value_per_share",
        # --- 财务指标 (fina_indicator) - 新增 ---
        "cash_ratio",
        "ocf_to_debt",
        "interest_bearing_debt",
        "ebitda",
        "currentdebt_to_debt",
        "operating_profit_margin",
        "revenue_yoy",
        "net_profit_yoy",
        # --- Phase 2 额外有用字段 ---
        "net_debt",
        "ebit",
        "free_cash_flow_to_firm",
        "free_cash_flow_to_equity",
        "ocf_to_short_debt",
        "debt_to_equity",
        "long_term_debt_ratio",
        "current_assets_ratio",
        "selling_expense_ratio",
        "admin_expense_ratio",
        "finance_expense_ratio",
        "total_assets_yoy",
        "equity_yoy",
        "operating_cash_flow_yoy",
        # --- 市场数据 (daily_basic) ---
        "market_cap",
        "circ_market_cap",
        "circ_shares",
        "pe_ratio",
        "pb_ratio",
    }

    # 市场数据字段（硬编码）
    _MARKET_FIELDS: set[str] = {
        "market_cap",
        "circ_market_cap",
        "circ_shares",
        "pe_ratio",
        "pb_ratio",
        "total_shares",
    }

    # 字段映射声明 (Handler 执行映射)
    # 结构: {statement_type: {native_field: standard_field}}
    FIELD_MAPPINGS: dict[str, dict[str, str]] = {
        "balance_sheet": {
            # Tushare 列名 -> 标准字段名
            "total_assets": "total_assets",
            "total_liab": "total_liabilities",
            "total_hldr_eqy_exc_min_int": "total_equity",
            "total_cur_liab": "current_liabilities",
            "money_cap": "cash_and_equivalents",
            "inventories": "inventory",
            "accounts_receiv": "accounts_receivable",
            "fix_assets": "fixed_assets",
            "total_cur_assets": "current_assets",
            "accounts_pay": "accounts_payable",
            "prepayment": "prepayment",
            "contract_assets": "contract_assets",
            "contract_liab": "contract_liab",
            "adv_receipts": "adv_receipts",
            "total_share": "total_shares",
            # Phase 1 资产负债表核心字段
            "goodwill": "goodwill",
            "intan_assets": "intangible_assets",
            "lt_eqt_invest": "long_term_investment",
            "cip": "construction_in_progress",
            # Phase 1 资产负债表补充字段
            "time_deposit": "time_deposits",
            "bonds_payable": "bonds_payable",
            "other_recv": "other_receivables",
            "total_hldr_eqy_exc_min_int": "net_assets",
        },
        "income_statement": {
            # Tushare 列名与标准字段名相同
            "total_revenue": "total_revenue",
            "n_income": "net_profit",
            "operate_profit": "operating_profit",
            "oper_cost": "operating_cost",
            "n_income_attr_p": "parent_net_profit",
        },
        "cash_flow": {
            "n_cashflow_act": "operating_cash_flow",
            "n_cashflow_inv_act": "investing_cash_flow",
            "n_cash_flows_fnc_act": "financing_cash_flow",
            "c_pay_acq_const_fiolta": "capital_expenditure",
        },
        "indicators": {
            # Tushare fina_indicator 列名 -> 标准字段名
            "roe": "roe",
            "roa": "roa",
            # 注意: Tushare 的 gross_margin 是毛利润金额(元)，grossprofit_margin 才是毛利率(%)
            "grossprofit_margin": "gross_margin",
            "netprofit_margin": "net_profit_margin",
            "current_ratio": "current_ratio",
            "quick_ratio": "quick_ratio",
            "debt_to_assets": "debt_ratio",
            "assets_turn": "asset_turnover",
            "ar_turn": "receivable_turnover",
            "roic": "roic",
            "eps": "basic_eps",
            "dt_eps": "diluted_eps",
            "bps": "book_value_per_share",
            # --- fina_indicator 新增字段 (数据验证通过) ---
            "cash_ratio": "cash_ratio",
            "ocf_to_debt": "ocf_to_debt",
            "interestdebt": "interest_bearing_debt",
            "ebitda": "ebitda",
            "currentdebt_to_debt": "currentdebt_to_debt",
            "op_of_gr": "operating_profit_margin",
            "tr_yoy": "revenue_yoy",
            "netprofit_yoy": "net_profit_yoy",
            # --- Phase 2: 额外有用字段 ---
            "netdebt": "net_debt",
            "ebit": "ebit",
            "fcff": "free_cash_flow_to_firm",
            "fcfe": "free_cash_flow_to_equity",
            "ocf_to_shortdebt": "ocf_to_short_debt",
            "debt_to_eqt": "debt_to_equity",
            "longdeb_to_debt": "long_term_debt_ratio",
            "ca_to_assets": "current_assets_ratio",
            "saleexp_to_gr": "selling_expense_ratio",
            "adminexp_of_gr": "admin_expense_ratio",
            "finaexp_of_gr": "finance_expense_ratio",
            "assets_yoy": "total_assets_yoy",
            "eqt_yoy": "equity_yoy",
            "ocf_yoy": "operating_cash_flow_yoy",
        },
        "market": {
            # Tushare daily_basic 列名 -> 标准字段名
            "total_mv": "market_cap",
            "circ_mv": "circ_market_cap",
            "float_share": "circ_shares",
            "pe_ttm": "pe_ratio",
            "pb": "pb_ratio",
            "total_share": "total_shares",
        },
    }

    def __init__(self, cache, token: str):
        """Initialize Tushare provider

        Args:
            cache: SmartCache instance
            token: Tushare API token
        """
        self._cache = cache
        self._token = token

        # Initialize Tushare API
        import tushare as ts

        ts.set_token(token)
        self._api = ts.pro_api()

    @property
    def supported_fields(self) -> set[str]:
        return self.SUPPORTED_FIELDS

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
        indicator_fields = fields & {
            "roe",
            "roa",
            "gross_margin",
            "net_profit_margin",
            "current_ratio",
            "quick_ratio",
            "debt_ratio",
            "asset_turnover",
            "receivable_turnover",
            "roic",
            "basic_eps",
            "diluted_eps",
            "book_value_per_share",
            # --- fina_indicator 新增字段 (数据验证通过) ---
            "cash_ratio",
            "ocf_to_debt",
            "interest_bearing_debt",
            "ebitda",
            "currentdebt_to_debt",
            "operating_profit_margin",
            "revenue_yoy",
            "net_profit_yoy",
            # --- Phase 2 额外有用字段 ---
            "net_debt",
            "ebit",
            "free_cash_flow_to_firm",
            "free_cash_flow_to_equity",
            "ocf_to_short_debt",
            "debt_to_equity",
            "long_term_debt_ratio",
            "current_assets_ratio",
            "selling_expense_ratio",
            "admin_expense_ratio",
            "finance_expense_ratio",
            "total_assets_yoy",
            "equity_yoy",
            "operating_cash_flow_yoy",
        }

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
        mapping = self.FIELD_MAPPINGS.get("market", {})
        rename_map = {
            native: std for native, std in mapping.items() if native in df.columns
        }
        if rename_map:
            df = df.rename(columns=rename_map)

        # 提取单个值 (取最新一条)
        # 单位转换: Tushare 返回的市值单位是万元，需要乘以 10000 转换成元
        market_cap_fields = {"market_cap", "circ_market_cap"}
        results: dict[str, Any] = {}
        for field in market_fields:
            if field in df.columns:
                # 取最新一条记录的值
                value = df[field].iloc[0]
                # 市值字段单位转换: 万元 -> 元
                if field in market_cap_fields:
                    value = value * 10000
                results[field] = value

        return results

    def _get_balance_fields(self) -> set[str]:
        """Get standard fields from balance sheet"""
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
            "prepayment",
            "contract_assets",
            "contract_liab",
            "adv_receipts",
            "total_shares",
        }

    def _get_income_fields(self) -> set[str]:
        """Get standard fields from income statement"""
        return {
            "total_revenue",
            "net_profit",
            "operating_profit",
            "operating_cost",
            "parent_net_profit",
        }

    def _get_cash_flow_fields(self) -> set[str]:
        """Get standard fields from cash flow"""
        return {
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "capital_expenditure",
        }

    def _get_market_fields(self) -> set[str]:
        """Get standard fields from market data (daily_basic)"""
        return self._MARKET_FIELDS

    # ========================================================================
    # 原始数据获取方法 (供 Handler 调用 - 无映射)
    # ========================================================================

    def fetch_raw_balance_sheet(self, ts_code: str, start_year: int, end_year: int) -> pd.DataFrame:
        """获取原始资产负债表数据（不做映射，返回 Tushare 原始列名）"""
        stock_code = self._to_ts_code(ts_code)
        cache_key = f"pipeline:raw:balance:{stock_code}"

        cached = self._cache.get(cache_key)
        if cached is not None and not cached.empty:
            if "year" in cached.columns:
                return cached[(cached["year"] >= start_year) & (cached["year"] <= end_year)]
            return cached

        today = datetime.now().strftime("%Y%m%d")
        df = self._api.balancesheet(
            ts_code=stock_code,
            start_date=f"{start_year}0101",
            end_date=today,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = self._filter_latest_by_update_flag(df)
        df = self._extract_year(df)
        self._cache.set(cache_key, df, ttl=self._get_ttl_until_june_next_year())

        if "year" in df.columns:
            df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    def fetch_raw_income_statement(self, ts_code: str, start_year: int, end_year: int) -> pd.DataFrame:
        """获取原始利润表数据（不做映射，返回 Tushare 原始列名）"""
        stock_code = self._to_ts_code(ts_code)
        cache_key = f"pipeline:raw:income:{stock_code}"

        cached = self._cache.get(cache_key)
        if cached is not None and not cached.empty:
            if "year" in cached.columns:
                return cached[(cached["year"] >= start_year) & (cached["year"] <= end_year)]
            return cached

        today = datetime.now().strftime("%Y%m%d")
        df = self._api.income(
            ts_code=stock_code,
            start_date=f"{start_year}0101",
            end_date=today,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = self._filter_latest_by_update_flag(df)
        df = self._extract_year(df)
        self._cache.set(cache_key, df, ttl=self._get_ttl_until_june_next_year())

        if "year" in df.columns:
            df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    def fetch_raw_cash_flow(self, ts_code: str, start_year: int, end_year: int) -> pd.DataFrame:
        """获取原始现金流量表数据（不做映射，返回 Tushare 原始列名）"""
        stock_code = self._to_ts_code(ts_code)
        cache_key = f"pipeline:raw:cashflow:{stock_code}"

        cached = self._cache.get(cache_key)
        if cached is not None and not cached.empty:
            if "year" in cached.columns:
                return cached[(cached["year"] >= start_year) & (cached["year"] <= end_year)]
            return cached

        today = datetime.now().strftime("%Y%m%d")
        df = self._api.cashflow(
            ts_code=stock_code,
            start_date=f"{start_year}0101",
            end_date=today,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = self._filter_latest_by_update_flag(df)
        df = self._extract_year(df)
        self._cache.set(cache_key, df, ttl=self._get_ttl_until_june_next_year())

        if "year" in df.columns:
            df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    # ========================================================================
    # BaseProvider 抽象方法实现 (保留映射逻辑，向后兼容)
    # ========================================================================

    def _fetch_balance_sheet(self, ts_code: str, start_year: int, end_year: int) -> pd.DataFrame:
        """获取资产负债表（带映射）"""
        df = self.fetch_raw_balance_sheet(ts_code, start_year, end_year)
        return self._apply_field_mapping(df, "balance_sheet")

    def _fetch_income_statement(self, ts_code: str, start_year: int, end_year: int) -> pd.DataFrame:
        """获取利润表（带映射）"""
        df = self.fetch_raw_income_statement(ts_code, start_year, end_year)
        return self._apply_field_mapping(df, "income_statement")

    def _fetch_cash_flow(self, ts_code: str, start_year: int, end_year: int) -> pd.DataFrame:
        """获取现金流量表（带映射）"""
        df = self.fetch_raw_cash_flow(ts_code, start_year, end_year)
        return self._apply_field_mapping(df, "cash_flow")

    def _fetch_indicators(
        self, stock_code: str, end_year: int, start_year: int
    ) -> pd.DataFrame:
        """Fetch financial indicators (implements abstract method from BaseProvider)"""
        ts_code = self._to_ts_code(stock_code)
        return self._fetch_financial_indicators(ts_code, start_year, end_year)

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

        # Fix: Tushare's fina_indicator returns both 'gross_margin' (毛利润金额)
        # and 'grossprofit_margin' (毛利率). We want only 'gross_margin' (毛利率).
        # Drop the original 'gross_margin' column before mapping so the rename
        # from 'grossprofit_margin' -> 'gross_margin' won't conflict.
        if "gross_margin" in df.columns and "grossprofit_margin" in df.columns:
            df = df.drop(columns=["gross_margin"])

        # Map to standard field names using FIELD_MAPPINGS
        mapping = self.FIELD_MAPPINGS.get("indicators", {})
        rename_map = {
            native: std for native, std in mapping.items() if native in df.columns
        }
        if rename_map:
            df = df.rename(columns=rename_map)

        # Cache for future use
        self._cache.set(cache_key, df, ttl=self._get_ttl_until_june_next_year())

        # Filter by year range
        if "year" in df.columns:
            df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]

        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

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
            fields="ts_code,trade_date,total_mv,circ_mv,total_share,float_share,pe_ttm,pb",
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
