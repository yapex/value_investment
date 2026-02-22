from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class CacheStrategy:
    """Cache strategy for a specific data type"""
    ttl: int  # seconds
    stale_while_revalidate: bool = True

    @classmethod
    def for_data_type(cls, data_type: str) -> 'CacheStrategy':
        strategies = {
            'stock_info': cls(ttl=86400),  # 1 day - expires next morning
            'historical': cls(ttl=86400 * 365),  # 1 year
            'quarterly': cls(ttl=86400 * 180),  # 6 months
            'financial': cls(ttl=86400 * 365 * 2),  # 2 years - expires June next year
        }
        return strategies.get(data_type, cls(ttl=0))

@dataclass
class CacheConfig:
    """Cache configuration - centralizes TTL settings"""
    stock_info_ttl: int = 86400
    historical_ttl: int = 86400 * 365
    financial_ttl: int = 86400 * 365 * 2
    quarterly_ttl: int = 86400 * 180

    def get_ttl(self, data_type: str) -> int:
        """Get TTL for data type"""
        mapping = {
            'stock_info': self.stock_info_ttl,
            'historical': self.historical_ttl,
            'quarterly': self.quarterly_ttl,
            'financial': self.financial_ttl,
        }
        return mapping.get(data_type, 0)
