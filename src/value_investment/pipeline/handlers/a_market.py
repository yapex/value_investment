"""A 股市值数据 Handler (来自 daily_basic API)"""
from typing import TYPE_CHECKING

from value_investment.pipeline.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.pipeline.bus.message import Message


# A 股市值数据字段（来自 daily_basic API）
A_STOCK_MARKET_FIELDS: set[str] = {
    "market_cap",
    "pe_ratio",
    "pb_ratio",
    "total_shares",
    "circ_market_cap",
    "circ_shares",
}


class AStockMarketHandler(BaseHandler):
    """A 股市值数据 Handler

    处理从 daily_basic API 获取的市值、市盈率、市净率等市场数据。
    市场数据是单时间点数据（取 end 参数对应日期的值）。
    """

    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_STOCK_MARKET_FIELDS)

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
