"""Test Safety Indicators - CashToDebt and DebtRatioTotal"""
import pytest
import pandas as pd
from value_investment.indicators.safety import (
    CashToDebtIndicator,
    DebtRatioTotalIndicator,
)


def test_cash_to_debt_indicator():
    """Cash to debt ratio should be calculated correctly (货币资金/有息负债)"""
    indicator = CashToDebtIndicator()
    
    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31'],
        'MONETARYFUNDS': [1000.0, 800.0],  # 货币资金
        'SHORT_LOAN': [200.0, 150.0],      # 短期借款
        'LONG_LOAN': [300.0, 250.0],       # 长期借款
        'BOND_PAYABLE': [100.0, 100.0],    # 应付债券
    })
    
    result = indicator.calculate(balance)
    
    # 有息负债 = short_term_debt + long_term_debt + bonds_payable = 600
    # cash_to_debt = mean([1000/600, 800/500]) = mean([1.667, 1.6]) = 1.633
    assert result.value == pytest.approx(1.633, 0.01)
    assert result.unit == "ratio"
    assert "Cash to Debt" in result.description or "货币资金/有息负债" in result.description


def test_cash_to_debt_with_lease_liability():
    """Cash to debt should include lease liability in interest-bearing debt"""
    indicator = CashToDebtIndicator()
    
    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'MONETARYFUNDS': [500.0],
        'SHORT_LOAN': [100.0],
        'LEASE_LIAB': [50.0],  # 租赁负债
    })
    
    result = indicator.calculate(balance)
    
    # 有息负债 = 100 + 50 = 150
    # cash_to_debt = 500 / 150 = 3.33
    assert result.value == pytest.approx(3.33, 0.01)


def test_cash_to_debt_no_debt():
    """Cash to debt should handle zero debt gracefully"""
    indicator = CashToDebtIndicator()
    
    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'MONETARYFUNDS': [1000.0],
        'SHORT_LOAN': [0.0],
        'LONG_LOAN': [0.0],
    })
    
    result = indicator.calculate(balance)
    
    # When debt is 0, should return a high value or special handling
    assert result.value >= 0  # Should not be negative


def test_debt_ratio_total_indicator():
    """Debt ratio total should be calculated correctly (有息负债/总资产)"""
    indicator = DebtRatioTotalIndicator()
    
    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31'],
        'TOTAL_ASSETS': [5000.0, 4500.0],
        'SHORT_LOAN': [200.0, 150.0],
        'LONG_LOAN': [300.0, 250.0],
        'BOND_PAYABLE': [100.0, 100.0],
    })
    
    result = indicator.calculate(balance)
    
    # 有息负债 = 600 (2023), 550 (2022); 总资产 = 5000, 4500
    # debt_ratio_total = mean([600/5000*100, 550/4500*100]) = mean([12, 12.22]) = 12.11%
    assert result.value == pytest.approx(12.11, 0.1)
    assert result.unit == "%"
    assert "Debt Ratio" in result.description or "有息负债" in result.description


def test_debt_ratio_total_multiple_years():
    """Debt ratio total should calculate average across multiple years"""
    indicator = DebtRatioTotalIndicator()
    
    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31', '2021-12-31'],
        'TOTAL_ASSETS': [10000.0, 9000.0, 8000.0],
        'SHORT_LOAN': [500.0, 400.0, 300.0],
        'LONG_LOAN': [500.0, 400.0, 300.0],
    })
    
    result = indicator.calculate(balance)
    
    # 2023: 1000/10000 = 10%
    # 2022: 800/9000 = 8.89%
    # 2021: 600/8000 = 7.5%
    # Average ≈ 8.8%
    expected_avg = ((1000/10000) + (800/9000) + (600/8000)) / 3 * 100
    assert result.value == pytest.approx(expected_avg, 0.1)


def test_debt_ratio_total_zero_assets():
    """Debt ratio total should handle zero assets gracefully"""
    indicator = DebtRatioTotalIndicator()
    
    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'TOTAL_ASSETS': [0.0],
        'SHORT_LOAN': [100.0],
    })
    
    result = indicator.calculate(balance)
    
    # Should not crash, should return 0 or handle gracefully
    assert result.value >= 0


def test_cash_to_debt_required_fields():
    """CashToDebtIndicator should return required fields"""
    indicator = CashToDebtIndicator()
    fields = indicator.get_required_fields()
    
    assert 'cash_and_equivalents' in fields or 'MONETARYFUNDS' in fields
    assert any('debt' in f.lower() or 'loan' in f.lower() for f in fields)


def test_debt_ratio_total_required_fields():
    """DebtRatioTotalIndicator should return required fields"""
    indicator = DebtRatioTotalIndicator()
    fields = indicator.get_required_fields()
    
    assert 'total_assets' in fields or 'TOTAL_ASSETS' in fields
    assert any('debt' in f.lower() or 'loan' in f.lower() for f in fields)
