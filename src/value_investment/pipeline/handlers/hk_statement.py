"""港股财务报表 Handler (资产负债表 + 利润表 + 现金流量表)"""
from typing import TYPE_CHECKING

from value_investment.pipeline.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.pipeline.bus.message import Message


# 港股财务报表字段（来自 CORE_FIELD_MAPPING 中 港股的映射）
HK_STOCK_STATEMENT_FIELDS: set[str] = {
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


class HKStockStatementHandler(BaseHandler):
    """港股财务三表 Handler

    处理资产负债表、利润表、现金流量表数据。
    Provider 待实现：需实现 fetch_financial_data 方法。
    """

    def __init__(self, provider=None):
        super().__init__(provider, "港股", HK_STOCK_STATEMENT_FIELDS)

    async def _handle_impl(self, message: "Message") -> None:
        """处理港股财务报表请求

        TODO: 待 HK Provider 实现 fetch_financial_data 后完善此方法
        """
        if not self._provider:
            return

        to_handle = message.require & self.can_handle
        if not to_handle:
            return

        # 临时实现：尝试调用 provider 的通用方法
        # TODO: 等 HK Provider 实现 fetch_financial_data 后改为:
        # data = self._provider.fetch_financial_data(...)
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
        else:
            # 旧 Provider：使用独立方法
            await self._handle_with_legacy_provider(message, to_handle)

    async def _handle_with_legacy_provider(
        self, message: "Message", to_handle: set[str]
    ) -> None:
        """使用旧 Provider 接口（get_balance_sheet 等）"""
        import pandas as pd

        # 判断需要哪些报表
        balance_fields = {
            "total_assets", "total_liabilities", "total_equity",
            "current_assets", "current_liabilities", "cash_and_equivalents",
            "inventory", "accounts_receivable", "accounts_payable",
            "contract_assets", "prepayment", "adv_receipts", "contract_liab",
            "fixed_assets",
        }
        income_fields = {
            "total_revenue", "net_profit", "operating_profit",
            "gross_profit", "operating_cost",
        }
        cash_flow_fields = {
            "operating_cash_flow", "investing_cash_flow",
            "financing_cash_flow", "capital_expenditure",
        }
        per_share_fields = {"basic_eps", "diluted_eps", "book_value_per_share"}

        end_year = int(message.end[:4])
        stock_code = message.symbol
        results: dict[str, dict[int, float]] = {}

        # 获取各报表数据
        if to_handle & balance_fields:
            df = self._provider.get_balance_sheet(stock_code, end_year=end_year)
            for _, row in df.iterrows():
                year = int(row.get("year", 0))
                for field in to_handle & balance_fields:
                    if field in row.index and pd.notna(row[field]):
                        results.setdefault(field, {})[year] = float(row[field])

        if to_handle & (income_fields | per_share_fields):
            df = self._provider.get_income_statement(stock_code, end_year=end_year)
            fields_to_fetch = to_handle & (income_fields | per_share_fields)
            for _, row in df.iterrows():
                year = int(row.get("year", 0))
                for field in fields_to_fetch:
                    if field in row.index and pd.notna(row[field]):
                        results.setdefault(field, {})[year] = float(row[field])

        if to_handle & cash_flow_fields:
            df = self._provider.get_cash_flow_statement(stock_code, end_year=end_year)
            for _, row in df.iterrows():
                year = int(row.get("year", 0))
                for field in to_handle & cash_flow_fields:
                    if field in row.index and pd.notna(row[field]):
                        results.setdefault(field, {})[year] = float(row[field])

        for field, values in results.items():
            if values:
                message.add_result(field, values)
