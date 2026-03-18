"""A 股数据处理者"""
from typing import Any

from value_investment.pipeline.handlers.base import Handler
from value_investment.pipeline.data.provider import DataProvider
from value_investment.pipeline.fields import IFRSFields


class AStockHandler(Handler):
    """Handler for A股 (A-shares) financial data"""

    def __init__(self, provider: DataProvider | None = None):
        self._provider = provider
        # 能处理的字段 = provider 支持的字段
        self._can_handle = provider.supported_fields if provider else set()

    @property
    def can_handle(self) -> set[str]:
        return self._can_handle

    async def handle(self, message) -> None:
        """Handle message by fetching data from provider"""
        if message.market != "A股":
            return

        if not self._provider:
            return

        # 找出我能处理且在需求篮子里的字段
        to_handle = self.can_handle & message.require
        if not to_handle:
            return

        # 从数据源获取
        data = self._provider.fetch_financial_data(
            stock_code=message.symbol,
            fields=to_handle,
            end_year=int(message.end[:4]),
            years=message.years,
        )

        # 放入结果篮子
        for field, values in data.items():
            if values:  # 只有非空数据才放入
                message.add_result(field, values)
