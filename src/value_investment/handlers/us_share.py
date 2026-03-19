"""美股 (US-Share) Handlers

包含三个 Handler:
- USShareStatementHandler: 财务报表 (资产负债表 + 利润表 + 现金流量表)
- USShareIndicatorHandler: 财务指标 (ROE, 毛利率等)
- USShareMarketHandler: 市场数据 (市值, PE, PB等)
"""
from typing import TYPE_CHECKING

from value_investment.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.core.types import Message


# =============================================================================
# 美股字段常量
# =============================================================================

# 美股财务报表字段
US_SHARE_STATEMENT_FIELDS: set[str] = {
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
    "contract_assets",
    "prepayment",
    "adv_receipts",
    "contract_liab",
    "fixed_assets",
    # 现金流量表
    "operating_cash_flow",
    "investing_cash_flow",
    "financing_cash_flow",
    "capital_expenditure",
    # 每股指标
    "basic_eps",
    "diluted_eps",
    "book_value_per_share",
}

# 美股财务指标字段
US_SHARE_INDICATOR_FIELDS: set[str] = {
    "roe",
    "roa",
    "roic",
    "gross_margin",
    "net_profit_margin",
    "current_ratio",
    "quick_ratio",
    "cash_ratio",
    "debt_ratio",
    "equity_multiplier",
    "asset_turnover",
    "inventory_turnover",
    "receivable_turnover",
    "basic_eps",
    "diluted_eps",
    "book_value_per_share",
}

# 美股市值数据字段
US_SHARE_MARKET_FIELDS: set[str] = {
    "market_cap",
    "pe_ratio",
    "pb_ratio",
    "total_shares",
}


# =============================================================================
# 美股 Handlers
# =============================================================================


class USShareStatementHandler(BaseHandler):
    """美股财务报表 Handler"""

    def __init__(self, provider=None):
        super().__init__(provider, "美股", US_SHARE_STATEMENT_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        """处理美股财务报表请求"""
        if not self._provider:
            return

        to_handle = message.require & self.can_handle
        if not to_handle:
            return

        if hasattr(self._provider, "fetch_financial_data"):
            data = self._provider.fetch_financial_data(
                stock_code=message.symbol,
                fields=to_handle,
                end_year=int(message.end[:4]),
                years=message.years,
            )
            for field, values in data.items():
                if values:
                    message.add_result(field, values)


class USShareIndicatorHandler(BaseHandler):
    """美股财务指标 Handler"""

    def __init__(self, provider=None):
        super().__init__(provider, "美股", US_SHARE_INDICATOR_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        """处理美股财务指标请求"""
        if not self._provider:
            return

        to_handle = message.require & self.can_handle
        if not to_handle:
            return

        if hasattr(self._provider, "fetch_indicators"):
            data = self._provider.fetch_indicators(
                stock_code=message.symbol,
                fields=to_handle,
                end_year=int(message.end[:4]),
                years=message.years,
            )
            for field, values in data.items():
                if values:
                    message.add_result(field, values)


class USShareMarketHandler(BaseHandler):
    """美股市值数据 Handler"""

    def __init__(self, provider=None):
        super().__init__(provider, "美股", US_SHARE_MARKET_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        """处理美股市值数据请求"""
        if not self._provider:
            return

        to_handle = message.require & self.can_handle
        if not to_handle:
            return

        if hasattr(self._provider, "fetch_market_data"):
            data = self._provider.fetch_market_data(
                stock_code=message.symbol,
                fields=to_handle,
            )
            end_year = int(message.end[:4])
            for field, value in data.items():
                if value is not None:
                    message.add_result(field, {end_year: value})
