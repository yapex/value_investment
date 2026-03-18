"""美股数据处理者"""
from value_investment.pipeline.handlers.base import Handler


class USStockHandler(Handler):
    """Handler for 美股 (US shares) financial data"""

    def __init__(self, cache=None):
        self.cache = cache
        from value_investment.data.mapper import CORE_FIELD_MAPPING

        self._can_handle = set()
        for field, market_map in CORE_FIELD_MAPPING.items():
            if "美股" in market_map:
                self._can_handle.add(field)

    @property
    def can_handle(self) -> set[str]:
        return self._can_handle

    async def handle(self, message) -> None:
        pass
