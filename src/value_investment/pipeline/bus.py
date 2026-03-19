"""Message bus for pipeline"""
from typing import Any

from value_investment.core.types import Message


class MessageBus:
    """Message bus for processing messages through handlers"""

    def __init__(self):
        self.handlers: list = []

    def register(self, handler) -> None:
        """Register a handler to the bus"""
        self.handlers.append(handler)

    async def process(self, message: Message) -> Any:
        """Process message through all handlers

        Multi-round execution: continues until no more fields can be processed
        or requirements are met.
        """
        while message.require:
            before = len(message.require)
            for handler in self.handlers:
                await handler.handle(message)
            after = len(message.require)
            # No progress, exit loop
            if before == after:
                break
        return message
