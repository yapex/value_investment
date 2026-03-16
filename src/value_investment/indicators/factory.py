"""Indicator factory module"""

from typing import TYPE_CHECKING

from value_investment.indicators.base import BaseIndicator
from value_investment.indicators.cashflow import (
    CfoToNetprofitIndicator,
    CfoToNetprofitSumIndicator,
    FcfToRevenueIndicator,
)
from value_investment.indicators.efficiency import (
    AccountsReceivableRatioIndicator,
    ExpenseRatioIndicator,
    FeeRateIndicator,
    FeeToGrossProfitRatioIndicator,
    FixedAssetToRevenueIndicator,
    FixedAssetTurnoverIndicator,
    PayableTurnoverIndicator,
    ProductionAssetRatioIndicator,
    ReceivablesToAssetsRatioIndicator,
    ReturnOnProductionAssetsIndicator,
)
from value_investment.indicators.growth import (
    CAGRIndicator,
    NetAssetGrowthIndicator,
    OperatingProfitGrowthIndicator,
    RevenueGrowthIndicator,
    ROICIndicator,
    TotalAssetGrowthIndicator,
)
from value_investment.indicators.calculated import (
    AssetTurnoverIndicator,
    EquityMultiplierIndicator,
    GrossMarginIndicator,
    NetProfitMarginIndicator,
    OperatingCashFlowIndicator,
    ROAIndicator,
    ROEIndicator,
    TotalAssetsIndicator,
    TotalAssetsTurnoverIndicator,
    TotalEquityIndicator,
)
from value_investment.indicators.profitability import OperatingProfitMarginIndicator
from value_investment.indicators.safety import (
    CashToDebtIndicator,
    DebtRatioTotalIndicator,
)
from value_investment.indicators.valuation import (
    ImpliedGrowthIndicator,
    LatestMarketCapIndicator,
    PEPercentileIndicator,
)

if TYPE_CHECKING:
    from value_investment.data.providers.akshare_provider import AkshareProvider

class IndicatorFactory:
    """Factory for creating and managing indicators"""

    def __init__(self, provider: "AkshareProvider | None" = None):
        self._provider = provider
        self._indicators: dict[str, BaseIndicator] = {}
        self._register_default_indicators()

    def _register_default_indicators(self) -> None:
        """Register all default indicators"""

        indicators = [
            # Profitability
            OperatingProfitMarginIndicator(),
            # HK Missing Indicators (DuPont Analysis)
            TotalAssetsTurnoverIndicator(),
            EquityMultiplierIndicator(),
            AssetTurnoverIndicator(),
            TotalAssetsIndicator(),
            TotalEquityIndicator(),
            GrossMarginIndicator(),
            OperatingCashFlowIndicator(),
            NetProfitMarginIndicator(),
            ROEIndicator(),
            ROAIndicator(),
            # Efficiency
            PayableTurnoverIndicator(),
            ExpenseRatioIndicator(),
            FeeRateIndicator(),
            FixedAssetTurnoverIndicator(),
            FixedAssetToRevenueIndicator(),
            FeeToGrossProfitRatioIndicator(),
            AccountsReceivableRatioIndicator(),
            ProductionAssetRatioIndicator(),
            ReturnOnProductionAssetsIndicator(),
            ReceivablesToAssetsRatioIndicator(),
            # Cashflow
            CfoToNetprofitIndicator(),
            FcfToRevenueIndicator(),
            CfoToNetprofitSumIndicator(),
            # Valuation
            LatestMarketCapIndicator(),
            ROICIndicator(),
            CAGRIndicator(),
            ImpliedGrowthIndicator(),
            PEPercentileIndicator(),
            # Growth
            RevenueGrowthIndicator(),
            OperatingProfitGrowthIndicator(),
            NetAssetGrowthIndicator(),
            TotalAssetGrowthIndicator(),
            # Safety
            CashToDebtIndicator(),
            DebtRatioTotalIndicator(),
        ]
        for indicator in self._deduplicate(indicators):
            self.register(indicator)

    def _deduplicate(self, indicators: list) -> list:
        """Remove duplicate indicators by name"""
        seen = set()
        result = []
        for ind in indicators:
            if ind.name not in seen:
                seen.add(ind.name)
                result.append(ind)
        return result

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
