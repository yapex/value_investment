import pytest
import pandas as pd


def test_base_indicator_has_find_column():
    """BaseIndicator should have _find_column method"""
    from value_investment.indicators.base import BaseIndicator
    assert hasattr(BaseIndicator, '_find_column')


def test_roe_indicator_uses_base_find_column():
    """ROEIndicator should use BaseIndicator._find_column"""
    from value_investment.indicators.base import BaseIndicator
    from value_investment.indicators.profitability import ROEIndicator
    
    # Check that ROEIndicator uses the inherited method
    assert ROEIndicator._find_column is BaseIndicator._find_column


def test_roa_indicator_uses_base_find_column():
    """ROAIndicator should use BaseIndicator._find_column"""
    from value_investment.indicators.base import BaseIndicator
    from value_investment.indicators.profitability import ROAIndicator
    
    assert ROAIndicator._find_column is BaseIndicator._find_column


def test_cash_to_debt_indicator_uses_base_find_column():
    """CashToDebtIndicator should use BaseIndicator._find_column"""
    from value_investment.indicators.base import BaseIndicator
    from value_investment.indicators.safety import CashToDebtIndicator
    
    assert CashToDebtIndicator._find_column is BaseIndicator._find_column
