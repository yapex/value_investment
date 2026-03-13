"""缓存接口定义 - 遵循 DIP 原则

定义 ICache 接口，FilterBuilder 依赖抽象而非具体实现。
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ICache(Protocol):
    """缓存接口 - 遵循依赖倒置原则
    
    FilterBuilder 依赖此抽象接口，而非具体实现（SmartCache）。
    便于测试和扩展不同的缓存实现。
    """
    
    def get(self, key: str) -> Any:
        """获取缓存值
        
        Args:
            key: 缓存键
            
        Returns:
            缓存值，如果不存在返回 None
        """
        ...
    
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），可选
        """
        ...
    
    def list_keys(self) -> list[str]:
        """列出所有缓存键
        
        Returns:
            缓存键列表
        """
        ...
