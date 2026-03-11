import pytest
from typing import Protocol


def test_imarket_data_provider_has_required_methods():
    """IMarketDataProvider should define get_historical_data"""
    from value_investment.core.interfaces import IMarketDataProvider
    required = ['get_historical_data']
    for method in required:
        assert hasattr(IMarketDataProvider, method), f"Missing method: {method}"


def test_company_info_provider_has_required_methods():
    """ICompanyInfoProvider should define get_stock_info"""
    from value_investment.core.interfaces import ICompanyInfoProvider
    required = ['get_stock_info']
    for method in required:
        assert hasattr(ICompanyInfoProvider, method), f"Missing method: {method}"


def test_ifinancial_statement_provider_has_required_methods():
    """IFinancialStatementProvider should define balance/income/cashflow methods"""
    from value_investment.core.interfaces import IFinancialStatementProvider
    required = ['get_balance_sheet', 'get_income_statement', 'get_cash_flow_statement']
    for method in required:
        assert hasattr(IFinancialStatementProvider, method), f"Missing method: {method}"
