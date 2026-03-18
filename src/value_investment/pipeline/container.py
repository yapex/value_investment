"""Dependency Injection Container for Pipeline"""
from dependency_injector import containers, providers

from value_investment.pipeline.bus.message_bus import MessageBus
from value_investment.pipeline.handlers.a_stock import AStockHandler
from value_investment.pipeline.handlers.hk_stock import HKStockHandler
from value_investment.pipeline.handlers.us_stock import USStockHandler
from value_investment.pipeline.data.tushare_provider import TushareProvider
from value_investment.pipeline.fields import validate_fields


class Container(containers.DeclarativeContainer):
    """DI Container for Pipeline"""

    # Cache - 复用现有的 SmartCache
    cache = providers.Singleton(
        lambda: __import__("value_investment.data.cache", fromlist=["SmartCache"]).SmartCache()
    )

    # Tushare token from environment
    tushare_token = providers.Singleton(
        lambda: __import__("os").environ.get("TUSHARE_TOKEN", "")
    )

    # Data providers
    tushare_provider = providers.Singleton(
        TushareProvider,
        cache=cache,
        token=tushare_token,
    )

    # 消息总线
    bus = providers.Singleton(MessageBus)

    # Handlers - 注入 provider
    a_stock_handler = providers.Singleton(
        AStockHandler,
        provider=tushare_provider,
    )
    hk_stock_handler = providers.Singleton(HKStockHandler)
    us_stock_handler = providers.Singleton(USStockHandler)

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
