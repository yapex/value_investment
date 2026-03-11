"""Provider factory for creating market-specific providers

注意: A股的 AShareProvider 已被废弃，请使用 TushareProvider。
"""
from typing import TYPE_CHECKING

from value_investment.data.providers.a_share_provider import AShareProvider
from value_investment.data.providers.hk_share_provider import HKShareProvider
from value_investment.data.providers.us_share_provider import USShareProvider

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


class ProviderFactory:
    """Factory for creating market-specific stock data providers

    注意: A股的 AShareProvider 已被废弃，请使用 TushareProvider。
    """

    _PROVIDER_MAP = {
        "A": AShareProvider,  # DEPRECATED: Use TushareProvider for A-shares
        "HK": HKShareProvider,
        "US": USShareProvider,
    }

    @classmethod
    def create_provider(cls, cache: "SmartCache", market: str = "A"):
        """
        Create a provider instance for the specified market

        Args:
            cache: SmartCache instance
            market: Market type - "A" (A股), "HK" (港股), "US" (美股)

        Returns:
            Provider instance for the specified market

        Raises:
            ValueError: If market is not supported

        注意: market="A" 的 AShareProvider 已被废弃，请使用 TushareProvider。
        """
        provider_class = cls._PROVIDER_MAP.get(market.upper())
        if provider_class is None:
            raise ValueError(f"Unsupported market: {market}. Supported: {list(cls._PROVIDER_MAP.keys())}")
        return provider_class(cache=cache, market=market)
