"""Indicator Registry for managing financial indicators"""
from typing import Dict, List, Optional
from value_investment.indicators.base import IndicatorMeta, IndicatorType


class IndicatorRegistry:
    """Singleton registry for managing financial indicators"""

    _instance: Optional["IndicatorRegistry"] = None
    _indicators: Dict[str, IndicatorMeta] = {}

    def __init__(self) -> None:
        if IndicatorRegistry._instance is not None:
            raise RuntimeError("Use get_instance() to get singleton")
        self._indicators = {}

    @classmethod
    def get_instance(cls) -> "IndicatorRegistry":
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._indicators = {}
        return cls._instance

    def register(self, meta: IndicatorMeta) -> None:
        """Register an indicator

        Args:
            meta: Indicator metadata
        """
        self._indicators[meta.name] = meta

    def get(self, name: str) -> Optional[IndicatorMeta]:
        """Get indicator by name

        Args:
            name: Indicator name

        Returns:
            Indicator metadata or None if not found
        """
        return self._indicators.get(name)

    def list_all(self) -> List[IndicatorMeta]:
        """List all registered indicators

        Returns:
            List of all indicator metadata
        """
        return list(self._indicators.values())

    def list_by_type(self, indicator_type: IndicatorType) -> List[IndicatorMeta]:
        """List indicators by type

        Args:
            indicator_type: Type of indicators to filter

        Returns:
            List of matching indicators
        """
        return [
            meta
            for meta in self._indicators.values()
            if meta.type == indicator_type
        ]

    def list_by_market(self, market: str) -> List[IndicatorMeta]:
        """List indicators available for a market

        Args:
            market: Market name (e.g., "A股")

        Returns:
            List of indicators available for the market
        """
        return [
            meta
            for meta in self._indicators.values()
            if market in meta.market_fields or not meta.market_fields
        ]

    def clear(self) -> None:
        """Clear all registered indicators (mainly for testing)"""
        self._indicators.clear()


# Default raw financial indicators
DEFAULT_RAW_INDICATORS = [
    {
        "name": "revenue",
        "display_name": "营业收入",
        "field_names": ["营业总收入", "收益", "totalRevenue"],
        "market_fields": {
            "A股": "营业总收入",
            "港股": "收益",
            "美股": "totalRevenue",
        },
        "description": "企业营业收入",
        "unit": "元",
    },
    {
        "name": "net_profit",
        "display_name": "净利润",
        "field_names": ["净利润", "期内溢利", "netIncome"],
        "market_fields": {
            "A股": "净利润",
            "港股": "期内溢利",
            "美股": "netIncome",
        },
        "description": "企业净利润",
        "unit": "元",
    },
    {
        "name": "total_assets",
        "display_name": "总资产",
        "field_names": ["资产总计", "资产总值", "totalAssets"],
        "market_fields": {
            "A股": "资产总计",
            "港股": "资产总值",
            "美股": "totalAssets",
        },
        "description": "企业总资产",
        "unit": "元",
    },
    {
        "name": "total_equity",
        "display_name": "股东权益",
        "field_names": ["股东权益合计", "权益总额", "totalStockholdersEquity"],
        "market_fields": {
            "A股": "股东权益合计",
            "港股": "权益总额",
            "美股": "totalStockholdersEquity",
        },
        "description": "企业股东权益",
        "unit": "元",
    },
    {
        "name": "operating_income",
        "display_name": "营业利润",
        "field_names": ["营业利润", "营业溢利", "operatingIncome"],
        "market_fields": {
            "A股": "营业利润",
            "港股": "营业溢利",
            "美股": "operatingIncome",
        },
        "description": "企业营业利润",
        "unit": "元",
    },
]


def register_defaults() -> None:
    """Register default raw financial indicators"""
    registry = IndicatorRegistry.get_instance()

    for indicator_data in DEFAULT_RAW_INDICATORS:
        meta = IndicatorMeta(
            name=indicator_data["name"],
            display_name=indicator_data["display_name"],
            type=IndicatorType.RAW,
            field_names=indicator_data["field_names"],
            market_fields=indicator_data["market_fields"],
            description=indicator_data["description"],
            unit=indicator_data["unit"],
        )
        registry.register(meta)
