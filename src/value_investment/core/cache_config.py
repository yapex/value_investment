from dataclasses import dataclass

from value_investment.core.constants import (
    ONE_DAY_SECONDS,
    ONE_YEAR_SECONDS,
    SIX_MONTHS_SECONDS,
    TWO_YEARS_SECONDS,
)


@dataclass
class CacheStrategy:
    """Cache strategy for a specific data type"""
    ttl: int  # seconds
    stale_while_revalidate: bool = True

    @classmethod
    def for_data_type(cls, data_type: str) -> 'CacheStrategy':
        strategies = {
            'stock_info': cls(ttl=ONE_DAY_SECONDS),  # 1 day - expires next morning
            'historical': cls(ttl=ONE_YEAR_SECONDS),  # 1 year
            'quarterly': cls(ttl=SIX_MONTHS_SECONDS),  # 6 months
            'financial': cls(ttl=TWO_YEARS_SECONDS),  # 2 years - expires June next year
        }
        return strategies.get(data_type, cls(ttl=0))

@dataclass
class CacheConfig:
    """Cache configuration - centralizes TTL settings"""
    stock_info_ttl: int = ONE_DAY_SECONDS
    historical_ttl: int = ONE_YEAR_SECONDS
    financial_ttl: int = TWO_YEARS_SECONDS
    quarterly_ttl: int = SIX_MONTHS_SECONDS

    def get_ttl(self, data_type: str) -> int:
        """Get TTL for data type"""
        mapping = {
            'stock_info': self.stock_info_ttl,
            'historical': self.historical_ttl,
            'quarterly': self.quarterly_ttl,
            'financial': self.financial_ttl,
        }
        return mapping.get(data_type, 0)
