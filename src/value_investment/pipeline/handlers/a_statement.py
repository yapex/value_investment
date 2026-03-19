"""A 股财务报表 Handler (资产负债表 + 利润表 + 现金流量表)"""
from typing import TYPE_CHECKING

from value_investment.pipeline.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.pipeline.bus.message import Message


# A 股财务报表字段（来自 balance_sheet + income_statement + cash_flow）
A_STOCK_STATEMENT_FIELDS: set[str] = {
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


class AStockStatementHandler(BaseHandler):
    """A 股财务三表 Handler

    处理资产负债表、利润表、现金流量表数据。
    不处理指标数据（roe/gross_margin 等）和市值数据（market_cap/pe_ratio）。
    """

    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_STOCK_STATEMENT_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        """处理 A 股财务报表请求"""
        if not self._provider:
            return

        # 获取该 Handler 能处理的字段（supported_fields ∩ provider.supported_fields ∩ message.require）
        to_handle = message.require & self.can_handle
        if not to_handle:
            return

        # 调用 provider 获取数据
        data = self._provider.fetch_financial_data(
            stock_code=message.symbol,
            fields=to_handle,
            end_year=int(message.end[:4]),
            years=message.years,
        )

        # 添加结果（add_result 会从 require 中移除字段）
        for field, values in data.items():
            if values:
                message.add_result(field, values)
