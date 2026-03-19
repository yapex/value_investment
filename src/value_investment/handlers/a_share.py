"""A 股 (A-Share) Handlers

包含三个 Handler:
- AShareStatementHandler: 财务报表 (资产负债表 + 利润表 + 现金流量表)
- AShareIndicatorHandler: 财务指标 (ROE, 毛利率等)
- AShareMarketHandler: 市场数据 (市值, PE, PB等)

AShareStatementHandler 使用 BaseHandler 的 _standardize() 执行字段映射。
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pandas as pd

from value_investment.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.core.types import Message


# =============================================================================
# A 股字段常量
# =============================================================================

# A 股财务报表字段（来自 balance_sheet + income_statement + cash_flow）
A_SHARE_STATEMENT_FIELDS: set[str] = {
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
    "prepayment",
    "contract_assets",
    "contract_liab",
    "adv_receipts",
    "total_shares",
    # 资产负债表 (Phase 1)
    "goodwill",
    "intangible_assets",
    "long_term_investment",
    "construction_in_progress",
    # 利润表
    "total_revenue",
    "net_profit",
    "operating_profit",
    "operating_cost",
    # 现金流量表
    "operating_cash_flow",
    "investing_cash_flow",
    "financing_cash_flow",
    "capital_expenditure",
}

# A 股财务指标字段（来自 fina_indicator API）
A_SHARE_INDICATOR_FIELDS: set[str] = {
    # 盈利能力
    "roe",
    "roa",
    "roic",
    "gross_margin",
    "net_profit_margin",
    # 偿债能力
    "current_ratio",
    "quick_ratio",
    "cash_ratio",
    "debt_ratio",
    "equity_multiplier",
    # 运营能力
    "asset_turnover",
    "inventory_turnover",
    "receivable_turnover",
    # 每股指标
    "basic_eps",
    "diluted_eps",
    "book_value_per_share",
}

# A 股市值数据字段（来自 daily_basic API）
A_SHARE_MARKET_FIELDS: set[str] = {
    "market_cap",
    "pe_ratio",
    "pb_ratio",
    "total_shares",
    "circ_market_cap",
    "circ_shares",
}


# =============================================================================
# A 股 Handlers
# =============================================================================


class AShareStatementHandler(BaseHandler):
    """A 股财务报表 Handler

    使用 BaseHandler 的 get_* 方法获取数据，自动执行字段映射。
    """

    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_SHARE_STATEMENT_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        """处理 A 股财务报表请求"""
        if not self._provider:
            return

        to_handle = message.require & self.can_handle
        if not to_handle:
            return

        end_year = int(message.end[:4])
        start_year = end_year - message.years + 1

        # 使用 BaseHandler 的 get_* 方法，自动执行字段映射
        balance_fields = to_handle & self._get_balance_fields()
        if balance_fields:
            df = self.get_balance_sheet(message.symbol, end_year, start_year)
            self._add_results_from_df(df, message, balance_fields)

        income_fields = to_handle & self._get_income_fields()
        if income_fields:
            df = self.get_income_statement(message.symbol, end_year, start_year)
            self._add_results_from_df(df, message, income_fields)

        cashflow_fields = to_handle & self._get_cashflow_fields()
        if cashflow_fields:
            df = self.get_cash_flow_statement(message.symbol, end_year, start_year)
            self._add_results_from_df(df, message, cashflow_fields)

    def _add_results_from_df(
        self,
        df: pd.DataFrame,
        message: "Message",
        fields: set[str],
    ) -> None:
        """从 DataFrame 提取结果到 Message"""
        if df.empty or "year" not in df.columns:
            return

        accumulated: dict[str, dict[int, Any]] = {}
        columns = df.columns.tolist()
        for _, row in df.iterrows():
            year = int(row["year"])
            for field in fields:
                if field in columns:
                    value = row.get(field)
                    if value is not None and pd.notna(value):
                        try:
                            accumulated.setdefault(field, {})[year] = float(value)
                        except (ValueError, TypeError):
                            pass

        for field, values in accumulated.items():
            if values:
                message.add_result(field, values)

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
            "prepayment",
            "contract_assets",
            "contract_liab",
            "adv_receipts",
            "total_shares",
            # Phase 1 资产负债表核心字段
            "goodwill",
            "intangible_assets",
            "long_term_investment",
            "construction_in_progress",
        }

    def _get_income_fields(self) -> set[str]:
        return {"total_revenue", "net_profit", "operating_profit", "operating_cost"}

    def _get_cashflow_fields(self) -> set[str]:
        return {
            "operating_cash_flow",
            "investing_cash_flow",
            "financing_cash_flow",
            "capital_expenditure",
        }


class AShareIndicatorHandler(BaseHandler):
    """A 股财务指标 Handler"""

    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_SHARE_INDICATOR_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        """处理 A 股财务指标请求"""
        if not self._provider:
            return

        to_handle = message.require & self.can_handle
        if not to_handle:
            return

        data = self._provider.fetch_indicators(
            stock_code=message.symbol,
            fields=to_handle,
            end_year=int(message.end[:4]),
            years=message.years,
        )

        for field, values in data.items():
            if values:
                message.add_result(field, values)


class AShareMarketHandler(BaseHandler):
    """A 股市值数据 Handler"""

    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_SHARE_MARKET_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        """处理 A 股市值数据请求"""
        if not self._provider:
            return

        to_handle = message.require & self.can_handle
        if not to_handle:
            return

        data = self._provider.fetch_market_data(
            stock_code=message.symbol,
            fields=to_handle,
        )

        end_year = int(message.end[:4])
        for field, value in data.items():
            if value is not None:
                message.add_result(field, {end_year: value})
