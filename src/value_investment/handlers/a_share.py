"""A 股 (A-Share) Handlers

包含三个 Handler:
- AShareStatementHandler: 财务报表 (资产负债表 + 利润表 + 现金流量表)
- AShareIndicatorHandler: 财务指标 (ROE, 毛利率等)
- AShareMarketHandler: 市场数据 (市值, PE, PB等)
"""
from typing import TYPE_CHECKING

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

    处理资产负债表、利润表、现金流量表数据。
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

        data = self._provider.fetch_financial_data(
            stock_code=message.symbol,
            fields=to_handle,
            end_year=int(message.end[:4]),
            years=message.years,
        )

        for field, values in data.items():
            if values:
                message.add_result(field, values)


class AShareIndicatorHandler(BaseHandler):
    """A 股财务指标 Handler

    处理从 fina_indicator API 获取的预计算财务比率指标。
    """

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
    """A 股市值数据 Handler

    处理从 daily_basic API 获取的市值、市盈率、市净率等市场数据。
    """

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

        # 市场数据是单时间点，转换为 {year: value} 格式
        end_year = int(message.end[:4])
        for field, value in data.items():
            if value is not None:
                message.add_result(field, {end_year: value})
