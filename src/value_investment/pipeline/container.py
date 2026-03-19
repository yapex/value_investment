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
from value_investment.pipeline.data.hk_provider import HKProvider
from value_investment.pipeline.data.us_provider import USProvider
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
    # HK Provider - 使用 AkShare
    hk_provider = providers.Singleton(
        HKProvider,
        cache=cache,
    )
    hk_stock_statement_handler = providers.Singleton(
        HKStockStatementHandler,
        provider=hk_provider,
    )
    hk_stock_indicator_handler = providers.Singleton(
        HKStockIndicatorHandler,
        provider=hk_provider,
    )
    hk_stock_market_handler = providers.Singleton(
        HKStockMarketHandler,
        provider=hk_provider,
    )

    # === 美股 Handlers ===
    # US Provider - 使用 AkShare 东财美股数据
    us_provider = providers.Singleton(
        USProvider,
        cache=cache,
    )
    us_stock_statement_handler = providers.Singleton(
        USStockStatementHandler,
        provider=us_provider,
    )
    us_stock_indicator_handler = providers.Singleton(
        USStockIndicatorHandler,
        provider=us_provider,
    )
    us_stock_market_handler = providers.Singleton(
        USStockMarketHandler,
        provider=us_provider,
    )

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
