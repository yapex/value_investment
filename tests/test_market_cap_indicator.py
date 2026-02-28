"""Test MarketCapIndicator"""
import pytest
from value_investment.indicators.market_cap import MarketCapIndicator


def test_indicator_has_name():
    """MarketCapIndicator should have name 'market_cap'"""
    indicator = MarketCapIndicator()
    assert indicator.name == "market_cap"


def test_indicator_has_description():
    """MarketCapIndicator should have description"""
    indicator = MarketCapIndicator()
    assert indicator.description is not None
    assert len(indicator.description) > 0


def test_hk_market_cap_from_financial_indicator():
    """Should get market cap from hk_market_cap field for HK stocks"""
    import pandas as pd
    from value_investment.indicators.market_cap import MarketCapIndicator
    
    indicator = MarketCapIndicator()
    
    # 模拟港股财务指标数据
    finind = pd.DataFrame({
        'hk_market_cap': [4151041376020.0],  # 腾讯市值
    })
    
    result = indicator.calculate(
        pd.DataFrame(),
        financial_indicator=finind,
        stock_code='00700'
    )
    
    assert result.value == 4151041376020.0
    assert '港元' in result.description or 'HK' in result.description or '港股' in result.description
