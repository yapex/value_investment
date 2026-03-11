import pytest


def test_income_statement_method_exists():
    """Providers should have get_income_statement method per IStockProvider"""
    from value_investment.core.interfaces import IFinancialStatementProvider
    
    # Check Protocol definition expects get_income_statement
    assert hasattr(IFinancialStatementProvider, 'get_income_statement')
    assert hasattr(IFinancialStatementProvider, 'get_cash_flow_statement')


def test_new_providers_implement_interface():
    """New market-specific providers should implement IFinancialStatementProvider"""
    from value_investment.data.providers.a_share_provider import AShareProvider
    from value_investment.data.providers.hk_share_provider import HKShareProvider
    from value_investment.data.providers.us_share_provider import USShareProvider
    
    # Verify they have the correct method names
    assert hasattr(AShareProvider, 'get_income_statement')
    assert hasattr(AShareProvider, 'get_cash_flow_statement')
    assert hasattr(HKShareProvider, 'get_income_statement')
    assert hasattr(HKShareProvider, 'get_cash_flow_statement')
    assert hasattr(USShareProvider, 'get_income_statement')
    assert hasattr(USShareProvider, 'get_cash_flow_statement')
