"""Test Working Capital Indicators"""
import pytest
import pandas as pd
from value_investment.indicators.efficiency import (
    WorkingCapitalIndicator,
    WCToRevenueIndicator,
    RevenuePerEmployeeIndicator,
)


def test_working_capital_indicator():
    """Working capital should be calculated correctly
    WC = 应收 + 预付 + 存货 + 合同资产 - (应付 + 预收 + 合同负债)
    """
    indicator = WorkingCapitalIndicator()

    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'ACCOUNTS_RECE': [1000.0],  # 应收账款
        'PREPAYMENT': [200.0],  # 预付款项
        'INVENTORY': [500.0],  # 存货
        'CONTRACT_ASSETS': [100.0],  # 合同资产
        'ACCOUNTS_PAYABLE': [800.0],  # 应付账款
        'ADV_RECEIPTS': [150.0],  # 预收款项
        'CONTRACT_LIAB': [50.0],  # 合同负债
    })

    result = indicator.calculate(balance)

    # WC = 1000 + 200 + 500 + 100 - (800 + 150 + 50) = 1800 - 1000 = 800
    assert result.value == pytest.approx(800.0, 0.01)
    assert result.unit == "元"
    assert "Working Capital" in result.description or "流动资金" in result.description


def test_working_capital_with_missing_fields():
    """Working capital should handle missing fields gracefully"""
    indicator = WorkingCapitalIndicator()

    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'ACCOUNTS_RECE': [1000.0],
        'INVENTORY': [500.0],
        'ACCOUNTS_PAYABLE': [800.0],
        # 其他字段缺失
    })

    result = indicator.calculate(balance)

    # WC = 1000 + 0 + 500 + 0 - (800 + 0 + 0) = 700
    assert result.value == pytest.approx(700.0, 0.01)


def test_working_capital_required_fields():
    """WorkingCapitalIndicator should report required fields"""
    indicator = WorkingCapitalIndicator()
    fields = indicator.get_required_fields()

    assert 'accounts_receivable' in fields
    assert 'inventory' in fields
    assert 'accounts_payable' in fields


def test_wc_to_revenue_indicator():
    """WC to revenue ratio should be calculated correctly"""
    indicator = WCToRevenueIndicator()

    data = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'ACCOUNTS_RECE': [1000.0],
        'PREPAYMENT': [200.0],
        'INVENTORY': [500.0],
        'CONTRACT_ASSETS': [100.0],
        'ACCOUNTS_PAYABLE': [800.0],
        'ADV_RECEIPTS': [150.0],
        'CONTRACT_LIAB': [50.0],
        'TOTAL_OPERATE_INCOME': [5000.0],  # 营业收入
    })

    result = indicator.calculate(data)

    # WC = 800, Revenue = 5000
    # WC/Revenue = 800 / 5000 = 0.16
    assert result.value == pytest.approx(0.16, 0.01)
    assert result.unit == "ratio"


def test_wc_to_revenue_zero_revenue():
    """WC to revenue should handle zero revenue gracefully"""
    indicator = WCToRevenueIndicator()

    data = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'ACCOUNTS_RECE': [1000.0],
        'INVENTORY': [500.0],
        'ACCOUNTS_PAYABLE': [800.0],
        'TOTAL_OPERATE_INCOME': [0.0],
    })

    result = indicator.calculate(data)

    # Should not crash, return 0 or handle gracefully
    assert result.value >= 0


def test_revenue_per_employee_without_data():
    """Revenue per employee should indicate need for external data"""
    indicator = RevenuePerEmployeeIndicator()

    data = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'TOTAL_OPERATE_INCOME': [5000.0],
    })

    result = indicator.calculate(data)

    # 没有员工数据时应该返回提示
    assert result is not None
    assert "需要" in result.description or "员工" in result.description or "external" in result.description.lower()


def test_revenue_per_employee_with_data():
    """Revenue per employee should calculate correctly with employee data"""
    indicator = RevenuePerEmployeeIndicator()

    data = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'TOTAL_OPERATE_INCOME': [1000000.0],  # 100万收入
    })

    # 通过 kwargs 传入员工数
    result = indicator.calculate(data, employee_count=100)

    # 人均收入 = 100万 / 100人 = 1万/人
    assert result.value == pytest.approx(10000.0, 0.01)
    assert result.unit == "元/人"
