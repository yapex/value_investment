"""Test Growth Indicators"""
import pytest
import pandas as pd
from value_investment.indicators.growth import (
    RevenueGrowthIndicator,
    ProfitGrowthIndicator,
    AssetGrowthIndicator,
    EquityGrowthIndicator,
)


def test_revenue_growth_indicator():
    """Revenue growth should be calculated correctly"""
    indicator = RevenueGrowthIndicator()
    
    income = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31', '2021-12-31'],
        'OPERATE_INCOME': [1200.0, 1000.0, 800.0],
    })
    
    result = indicator.calculate(pd.DataFrame(), income=income)
    
    assert result.value == 20.0  # (1200-1000)/1000 * 100
    assert '%' in result.unit


def test_profit_growth_indicator():
    """Profit growth should be calculated correctly"""
    indicator = ProfitGrowthIndicator()
    
    income = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31', '2021-12-31'],
        'NETPROFIT': [240.0, 200.0, 160.0],
    })
    
    result = indicator.calculate(pd.DataFrame(), income=income)
    
    assert result.value == 20.0  # (240-200)/200 * 100


def test_asset_growth_indicator():
    """Asset growth should be calculated correctly"""
    indicator = AssetGrowthIndicator()
    
    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31', '2021-12-31'],
        'TOTAL_ASSETS': [1200.0, 1000.0, 800.0],
    })
    
    result = indicator.calculate(pd.DataFrame(), balance=balance)
    
    assert result.value == 20.0


def test_equity_growth_indicator():
    """Equity growth should be calculated correctly"""
    indicator = EquityGrowthIndicator()
    
    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31', '2021-12-31'],
        'TOTAL_EQUITY': [800.0, 700.0, 600.0],
    })
    
    result = indicator.calculate(pd.DataFrame(), balance=balance)
    
    assert result.value == pytest.approx(14.29, 0.1)
