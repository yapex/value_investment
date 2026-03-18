"""A 股数据处理者"""
from value_investment.pipeline.handlers.base import Handler


class AStockHandler(Handler):
    """Handler for A股 (A-shares) financial data"""

    def __init__(self, cache=None):
        self.cache = cache
        # 从 CORE_FIELD_MAPPING 提取 A 股字段
        from value_investment.data.mapper import CORE_FIELD_MAPPING

        self._can_handle = set()
        for field, market_map in CORE_FIELD_MAPPING.items():
            if "A股" in market_map:
                self._can_handle.add(field)

    @property
    def can_handle(self) -> set[str]:
        return self._can_handle

    async def handle(self, message) -> None:
        # 简单实现：跳过，等待后续完善
        pass
