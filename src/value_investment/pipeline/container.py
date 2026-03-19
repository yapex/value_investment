"""Dependency Injection Container for Pipeline"""
from dependency_injector import containers, providers

from value_investment.pipeline.bus.message_bus import MessageBus
from value_investment.pipeline.handlers.a_statement import AStockStatementHandler
from value_investment.pipeline.handlers.a_indicator import AStockIndicatorHandler
from value_investment.pipeline.handlers.a_market import AStockMarketHandler
from value_investment.pipeline.handlers.hk_statement import HKStockStatementHandler
from value_investment.pipeline.handlers.hk_indicator import HKStockIndicatorHandler
from value_investment.pipeline.handlers.hk_market import HKStockMarketHandler
from value_investment.pipeline.handlers.us_statement import USStockStatementHandler
from value_investment.pipeline.handlers.us_indicator import USStockIndicatorHandler
from value_investment.pipeline.handlers.us_market import USStockMarketHandler
from value_investment.pipeline.data.tushare_provider import TushareProvider
from value_investment.pipeline.calculators import ALL_CALCULATORS


class Container(containers.DeclarativeContainer):
    """DI Container for Pipeline"""

    _instance = None

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

    # === A 股 Handlers ===
    a_stock_statement_handler = providers.Singleton(
        AStockStatementHandler,
        provider=tushare_provider,
    )
    a_stock_indicator_handler = providers.Singleton(
        AStockIndicatorHandler,
        provider=tushare_provider,
    )
    a_stock_market_handler = providers.Singleton(
        AStockMarketHandler,
        provider=tushare_provider,
    )

    # === 港股 Handlers ===
    # TODO: 待 HK Provider 实现后注入
    hk_stock_statement_handler = providers.Singleton(HKStockStatementHandler)
    hk_stock_indicator_handler = providers.Singleton(HKStockIndicatorHandler)
    hk_stock_market_handler = providers.Singleton(HKStockMarketHandler)

    # === 美股 Handlers ===
    # TODO: 待 US Provider 实现后注入
    us_stock_statement_handler = providers.Singleton(USStockStatementHandler)
    us_stock_indicator_handler = providers.Singleton(USStockIndicatorHandler)
    us_stock_market_handler = providers.Singleton(USStockMarketHandler)

    # Calculators - 派生字段计算器
    calculators = providers.List(*ALL_CALCULATORS)

    @classmethod
    def create(cls) -> "Container":
        """Create or return singleton container"""
        if cls._instance is None:
            container = cls()
            # 注册 9 个 Handler 到 bus
            # A 股 - 使用 Tushare Provider
            container.bus().register(container.a_stock_statement_handler())
            container.bus().register(container.a_stock_indicator_handler())
            container.bus().register(container.a_stock_market_handler())
            # 港股
            container.bus().register(container.hk_stock_statement_handler())
            container.bus().register(container.hk_stock_indicator_handler())
            container.bus().register(container.hk_stock_market_handler())
            # 美股
            container.bus().register(container.us_stock_statement_handler())
            container.bus().register(container.us_stock_indicator_handler())
            container.bus().register(container.us_stock_market_handler())
            cls._instance = container
        return cls._instance
