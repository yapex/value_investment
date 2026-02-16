"""Field mapping and market configuration for multi-market support"""
from dataclasses import dataclass
from typing import Dict, Optional

# Field mapping from common indicator name to market-specific field names
FIELD_MAPPING: Dict[str, Dict[str, str]] = {
    "revenue": {
        "A股": "营业总收入",
        "港股": "收益",
        "美股": "totalRevenue",
    },
    "net_profit": {
        "A股": "净利润",
        "港股": "期内溢利",
        "美股": "netIncome",
    },
    "total_assets": {
        "A股": "资产总计",
        "港股": "资产总值",
        "美股": "totalAssets",
    },
    "total_equity": {
        "A股": "股东权益合计",
        "港股": "权益总额",
        "美股": "totalStockholdersEquity",
    },
    "operating_income": {
        "A股": "营业利润",
        "港股": "营业溢利",
        "美股": "operatingIncome",
    },
    "cash_flow": {
        "A股": "现金流量净额",
        "港股": "现金流量净额",
        "美股": "operatingCashFlow",
    },
}


def get_mapped_field(indicator_name: str, market: str) -> Optional[str]:
    """Get field name for indicator in specific market

    Args:
        indicator_name: Common indicator name (e.g., "revenue")
        market: Market name ("A股", "港股", "美股")

    Returns:
        Market-specific field name or None if not found
    """
    if indicator_name in FIELD_MAPPING:
        return FIELD_MAPPING[indicator_name].get(market)
    return None


@dataclass
class MarketConfig:
    """Configuration for a specific market"""

    market: str
    indicator_prefix: str
    year_field: str
    data_source: str

    def get_field_mapping(self, indicator_name: str) -> Optional[Dict[str, str]]:
        """Get all market field mappings for an indicator"""
        return FIELD_MAPPING.get(indicator_name)
