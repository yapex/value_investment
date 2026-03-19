"""A 股财务指标 Handler (来自 fina_indicator API)"""
from typing import TYPE_CHECKING

from value_investment.pipeline.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.pipeline.bus.message import Message


# A 股财务指标字段（来自 fina_indicator API）
A_STOCK_INDICATOR_FIELDS: set[str] = {
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


class AStockIndicatorHandler(BaseHandler):
    """A 股财务指标 Handler

    处理从 fina_indicator API 获取的预计算财务比率指标。
    不处理原始财务报表数据和市值数据。
    """

    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_STOCK_INDICATOR_FIELDS)

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
