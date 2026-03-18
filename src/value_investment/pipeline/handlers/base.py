"""Handler base class for message processing"""
from abc import ABC, abstractmethod
from typing import Any


class Handler(ABC):
    """Handler base class for message processing"""

    @property
    @abstractmethod
    def can_handle(self) -> set[str]:
        """Fields this handler can provide"""
        pass

    @abstractmethod
    async def handle(self, message) -> None:
        """Handle the message"""
        pass
