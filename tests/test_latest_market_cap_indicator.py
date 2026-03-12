"""Test LatestMarketCapIndicator"""
import pytest
from value_investment.indicators.valuation import LatestMarketCapIndicator


def test_indicator_has_name():
    """LatestMarketCapIndicator should have name 'latest_market_cap'"""
    indicator = LatestMarketCapIndicator()
    assert indicator.name == "latest_market_cap"


def test_indicator_has_description():
    """LatestMarketCapIndicator should have description"""
    indicator = LatestMarketCapIndicator()
    assert indicator.description is not None
    assert len(indicator.description) > 0


def test_hk_market_cap_from_financial_indicator():
    """Should get market cap from hk_market_cap field for HK stocks"""
    import pandas as pd
    from value_investment.indicators.valuation import LatestMarketCapIndicator
    
    indicator = LatestMarketCapIndicator()
    
    # 模拟港股财务指标数据
    finind = pd.DataFrame({
        'hk_market_cap': [4151041376020.0],  # 腾讯市值
    })
    
    result = indicator.calculate(
        pd.DataFrame(),
        financial_indicator=finind,
        stock_code='00700'
    )
    
    # 市值会被转换为人民币，所以值会不同
    assert result.value > 0
    assert '市值' in result.description


def test_a_market_cap_from_financial_indicator():
    """Should get market cap for A-shares"""
    import pandas as pd
    from value_investment.indicators.valuation import LatestMarketCapIndicator
    
    indicator = LatestMarketCapIndicator()
    
    finind = pd.DataFrame({
        'a_market_cap': [2000000000000.0],  # 茅台市值
    })
    
    result = indicator.calculate(
        pd.DataFrame(),
        financial_indicator=finind,
        stock_code='600519'
    )
    
    assert result.value == 2000000000000.0
    assert '市值' in result.description


def test_us_market_cap_from_financial_indicator():
    """Should get market cap for US stocks"""
    import pandas as pd
    from value_investment.indicators.valuation import LatestMarketCapIndicator
    
    indicator = LatestMarketCapIndicator()
    
    finind = pd.DataFrame({
        'us_market_cap': [3000000000000.0],  # 苹果市值
    })
    
    result = indicator.calculate(
        pd.DataFrame(),
        financial_indicator=finind,
        stock_code='AAPL'
    )
    
    # 市值会被转换为人民币，所以值会不同
    assert result.value > 0
    assert '市值' in result.description


def test_market_cap_registered_in_factory():
    """latest_market_cap should be available via factory"""
    from value_investment.indicators.factory import IndicatorFactory
    
    factory = IndicatorFactory()
    indicator = factory.get('latest_market_cap')
    
    assert indicator is not None
    assert indicator.name == 'latest_market_cap'
