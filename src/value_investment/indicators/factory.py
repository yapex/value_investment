"""Indicator factory module"""

from typing import TYPE_CHECKING, Dict

from value_investment.indicators.base import BaseIndicator
from value_investment.indicators.profitability import (
    ROEIndicator,
    ROAIndicator,
    GrossMarginIndicator,
    NetProfitMarginIndicator,
)
from value_investment.indicators.solvency import (
    CurrentRatioIndicator,
    QuickRatioIndicator,
    DebtRatioIndicator,
)
from value_investment.indicators.efficiency import (
    AssetTurnoverIndicator,
    InventoryTurnoverIndicator,
    ReceivableTurnoverIndicator,
    PayableTurnoverIndicator,
    ExpenseRatioIndicator,
    FeeRateIndicator,
    FixedAssetTurnoverIndicator,
)
from value_investment.indicators.cashflow import (
    CfoToNetprofitIndicator,
    FcfToRevenueIndicator,
    CfoToNetprofitSumIndicator,
)
from value_investment.indicators.growth import (
    ROICIndicator,
    CAGRIndicator,
)
from value_investment.indicators.safety import (
    CashToDebtIndicator,
    DebtRatioTotalIndicator,
)
from value_investment.indicators.valuation import (
    LatestMarketCapIndicator,
    ImpliedGrowthIndicator,
    PEPercentileIndicator,
)
from value_investment.indicators.market_cap import MarketCapIndicator

if TYPE_CHECKING:
    from value_investment.data.providers.akshare_provider import AkshareProvider


class IndicatorFactory:
    """Factory for creating and managing indicators"""

    def __init__(self, provider: "AkshareProvider | None" = None):
        self._provider = provider
        self._indicators: Dict[str, BaseIndicator] = {}
        self._register_default_indicators()

    def _register_default_indicators(self) -> None:
        """Register all default indicators"""
        from value_investment.indicators.profitability import (
            ROEIndicator,
            ROAIndicator,
            GrossMarginIndicator,
            NetProfitMarginIndicator,
        )
        from value_investment.indicators.solvency import (
            CurrentRatioIndicator,
            QuickRatioIndicator,
            DebtRatioIndicator,
        )
        from value_investment.indicators.efficiency import (
            AssetTurnoverIndicator, InventoryTurnoverIndicator,
            ReceivableTurnoverIndicator, PayableTurnoverIndicator,
            ExpenseRatioIndicator, FeeRateIndicator, FixedAssetTurnoverIndicator,
        )
        from value_investment.indicators.cashflow import (
            CfoToNetprofitIndicator,
            FcfToRevenueIndicator,
            CfoToNetprofitSumIndicator,
        )
        from value_investment.indicators.growth import (
            ROICIndicator,
            CAGRIndicator,
        )
        from value_investment.indicators.valuation import (
            LatestMarketCapIndicator,
            ImpliedGrowthIndicator,
            PEPercentileIndicator,
        )
        from value_investment.indicators.market_cap import MarketCapIndicator
        from value_investment.indicators.safety import (
            CashToDebtIndicator,
            DebtRatioTotalIndicator,
        )

        indicators = [
            ROEIndicator(),
            ROAIndicator(),
            GrossMarginIndicator(),
            NetProfitMarginIndicator(),
            CurrentRatioIndicator(),
            AssetTurnoverIndicator(),
            InventoryTurnoverIndicator(),
            QuickRatioIndicator(),
            DebtRatioIndicator(),
            ReceivableTurnoverIndicator(),
            PayableTurnoverIndicator(),
            ExpenseRatioIndicator(),
            FeeRateIndicator(),
            FixedAssetTurnoverIndicator(),
            CfoToNetprofitIndicator(),
            FcfToRevenueIndicator(),
            CfoToNetprofitSumIndicator(),
            LatestMarketCapIndicator(),
            MarketCapIndicator(),
            ROICIndicator(),
            CAGRIndicator(),
            ImpliedGrowthIndicator(),
            CashToDebtIndicator(),
            DebtRatioTotalIndicator(),
            PEPercentileIndicator(),
        ]
        for indicator in indicators:
            self.register(indicator)

    def register(self, indicator: BaseIndicator) -> None:
        """Register an indicator"""
        self._indicators[indicator.name] = indicator

    def get(self, name: str) -> BaseIndicator:
        """Get an indicator by name"""
        if name not in self._indicators:
            raise ValueError(f"Unknown indicator: {name}")
        return self._indicators[name]

    def list_indicators(self) -> list:
        """List all registered indicators"""
        return list(self._indicators.keys())
