"""BaseHandler with fast-reject pattern"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from value_investment.core.types import Message


class BaseHandler(ABC):
    """Handler 基类，实现快速拒绝模式

    每个 Handler 只负责特定市场和数据类型，通过快速拒绝避免无效处理。
    """

    def __init__(
        self,
        provider,
        target_market: str,
        supported_fields: set[str],
    ):
        self._provider = provider
        self.target_market = target_market
        self._supported_fields = supported_fields

    @property
    def can_handle(self) -> set[str]:
        """该 Handler 能处理的字段集合（supported_fields ∩ provider.supported_fields）"""
        return self._supported_fields & (
            self._provider.supported_fields if self._provider else set()
        )

    def _can_handle_market(self, message: "Message") -> bool:
        """快速判断：是否处理该市场"""
        return message.market == self.target_market

    def _can_handle_fields(self, message: "Message") -> bool:
        """快速判断：是否有可处理的字段"""
        return bool(message.require & self.can_handle)

    async def handle(self, message: "Message") -> None:
        """处理消息（模板方法）"""
        # 快速拒绝：市场不匹配
        if not self._can_handle_market(message):
            return
        # 快速拒绝：无支持的字段
        if not self._can_handle_fields(message):
            return

        # 交给子类处理具体逻辑
        await self._handle_impl(message)

    @abstractmethod
    async def _handle_impl(self, message: "Message") -> None:
        """子类实现具体处理逻辑"""
        pass
