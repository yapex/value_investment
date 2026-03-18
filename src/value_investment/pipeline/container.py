"""Dependency Injection Container for Pipeline"""
from dependency_injector import containers, providers

from value_investment.pipeline.bus.message_bus import MessageBus
from value_investment.pipeline.handlers.a_stock import AStockHandler
from value_investment.pipeline.handlers.hk_stock import HKStockHandler
from value_investment.pipeline.handlers.us_stock import USStockHandler
from value_investment.pipeline.fields import validate_fields


class Container(containers.DeclarativeContainer):
    """DI Container for Pipeline"""

    # SmartCache 复用现有实现
    cache = providers.Singleton(
        lambda: __import__("value_investment.data.cache", fromlist=["SmartCache"]).SmartCache()
    )

    # 消息总线
    bus = providers.Singleton(MessageBus)

    # Handlers
    a_stock_handler = providers.Singleton(AStockHandler)
    hk_stock_handler = providers.Singleton(HKStockHandler)
    us_stock_handler = providers.Singleton(USStockHandler)

    # 组装：注册 handlers 到 bus（在初始化时调用）
    @classmethod
    def create(cls) -> "Container":
        """Create container and register handlers"""
        container = cls()
        
        # 校验所有 Calculator 的字段
        from value_investment.pipeline.calculators.roic import ROICCalculator
        validate_fields(ROICCalculator)
        
        # 注册 handlers 到 bus
        container.bus().register(container.a_stock_handler())
        container.bus().register(container.hk_stock_handler())
        container.bus().register(container.us_stock_handler())
        
        return container
