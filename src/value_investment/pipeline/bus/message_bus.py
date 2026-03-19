"""MessageBus for processing messages through handlers"""
from typing import Any


class MessageBus:
    """Message bus for processing messages through registered handlers"""

    def __init__(self):
        self.handlers: list = []

    def register(self, handler) -> None:
        """Register a handler to the bus"""
        self.handlers.append(handler)

    async def process(self, message) -> Any:
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
