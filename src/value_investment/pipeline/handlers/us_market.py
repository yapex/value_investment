"""美股市值数据 Handler"""
from typing import TYPE_CHECKING

from value_investment.pipeline.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.pipeline.bus.message import Message


# 美股市值数据字段
US_STOCK_MARKET_FIELDS: set[str] = {
    "market_cap",
    "pe_ratio",
    "pb_ratio",
    "total_shares",
}


class USStockMarketHandler(BaseHandler):
    """美股市值数据 Handler

    TODO: 待 US Provider 实现 fetch_market_data 方法。
    """

    def __init__(self, provider=None):
        super().__init__(provider, "美股", US_STOCK_MARKET_FIELDS)

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
