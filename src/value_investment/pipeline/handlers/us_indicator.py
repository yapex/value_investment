"""美股财务指标 Handler"""
from typing import TYPE_CHECKING

from value_investment.pipeline.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.pipeline.bus.message import Message


# 美股财务指标字段
US_STOCK_INDICATOR_FIELDS: set[str] = {
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


class USStockIndicatorHandler(BaseHandler):
    """美股财务指标 Handler

    TODO: 待 US Provider 实现 fetch_indicators 方法。
    """

    def __init__(self, provider=None):
        super().__init__(provider, "美股", US_STOCK_INDICATOR_FIELDS)

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
