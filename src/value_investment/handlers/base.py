"""Handler protocol for message processing"""
from typing import Any, Protocol


class Handler(Protocol):
    """Protocol for message handlers
    
    Any class implementing these methods can be used as a handler.
    No inheritance required - structural subtyping.
    
    Usage:
        class MyHandler:
            @property
            def can_handle(self) -> set[str]:
                return {"field1", "field2"}
            
            async def handle(self, message) -> None:
                # Process message
                pass
    """

    @property
    def can_handle(self) -> set[str]:
        """Fields this handler can provide"""
        ...

    async def handle(self, message: Any) -> None:
        """Handle the message
        
        Args:
            message: Message instance with require and results baskets
        """
        ...
