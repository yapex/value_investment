import pytest
from value_investment.core.cache_config import CacheConfig, CacheStrategy

def test_cache_config_defaults():
    config = CacheConfig()
    assert config.stock_info_ttl > 0
    assert config.historical_ttl > 0
    assert config.financial_ttl > 0

def test_cache_strategy_for_stock_info():
    strategy = CacheStrategy.for_data_type('stock_info')
    assert strategy.ttl > 0

def test_cache_strategy_unknown_type():
    strategy = CacheStrategy.for_data_type('unknown')
    assert strategy.ttl == 0  # No cache for unknown types
