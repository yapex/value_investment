"""Dependency Injection Container for Pipeline"""
from dependency_injector import containers, providers

from value_investment.pipeline.bus import MessageBus
from value_investment.handlers.a_share import (
    AShareStatementHandler,
    AShareIndicatorHandler,
    AShareMarketHandler,
)
from value_investment.handlers.hk_share import (
    HKShareStatementHandler,
    HKShareIndicatorHandler,
    HKShareMarketHandler,
)
from value_investment.handlers.us_share import (
    USShareStatementHandler,
    USShareIndicatorHandler,
    USShareMarketHandler,
)
from value_investment.providers.a_share import TushareProvider
from value_investment.providers.hk_share import HKProvider
from value_investment.providers.us_share import USProvider
from value_investment.domain.calculators import ALL_CALCULATORS


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
    a_share_statement_handler = providers.Singleton(
        AShareStatementHandler,
        provider=tushare_provider,
    )
    a_share_indicator_handler = providers.Singleton(
        AShareIndicatorHandler,
        provider=tushare_provider,
    )
    a_share_market_handler = providers.Singleton(
        AShareMarketHandler,
        provider=tushare_provider,
    )

    # === 港股 Handlers ===
    # HK Provider - 使用 AkShare
    hk_provider = providers.Singleton(
        HKProvider,
        cache=cache,
    )
    hk_share_statement_handler = providers.Singleton(
        HKShareStatementHandler,
        provider=hk_provider,
    )
    hk_share_indicator_handler = providers.Singleton(
        HKShareIndicatorHandler,
        provider=hk_provider,
    )
    hk_share_market_handler = providers.Singleton(
        HKShareMarketHandler,
        provider=hk_provider,
    )

    # === 美股 Handlers ===
    # US Provider - 使用 AkShare 东财美股数据
    us_provider = providers.Singleton(
        USProvider,
        cache=cache,
    )
    us_share_statement_handler = providers.Singleton(
        USShareStatementHandler,
        provider=us_provider,
    )
    us_share_indicator_handler = providers.Singleton(
        USShareIndicatorHandler,
        provider=us_provider,
    )
    us_share_market_handler = providers.Singleton(
        USShareMarketHandler,
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
            container.bus().register(container.a_share_statement_handler())
            container.bus().register(container.a_share_indicator_handler())
            container.bus().register(container.a_share_market_handler())
            # 港股
            container.bus().register(container.hk_share_statement_handler())
            container.bus().register(container.hk_share_indicator_handler())
            container.bus().register(container.hk_share_market_handler())
            # 美股
            container.bus().register(container.us_share_statement_handler())
            container.bus().register(container.us_share_indicator_handler())
            container.bus().register(container.us_share_market_handler())
            cls._instance = container
        return cls._instance
