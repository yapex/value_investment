"""Tests for Financing Cost Rate Calculator"""
import pytest
from value_investment.calculators.calc_financing_cost_rate import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestFinancingCostRate:
    """Test cases for financing_cost_rate calculator"""

    def test_required_fields(self):
        expected = ["finance_expense_ratio", "interest_bearing_debt"]
        assert required_fields == expected

    def test_basic_calculation(self):
        results = {
            "finance_expense_ratio": {2023: 0.05, 2022: 0.04},
            "interest_bearing_debt": {2023: 1000000000, 2022: 800000000},
        }
        output = calculate(results)
        assert output[2023] == pytest.approx(5e-11, rel=1e-9)
        assert output[2022] == pytest.approx(5e-11, rel=1e-9)

    def test_zero_debt_returns_none(self):
        results = {
            "finance_expense_ratio": {2023: 0.05},
            "interest_bearing_debt": {2023: 0},
        }
        output = calculate(results)
        assert output[2023] is None

    def test_missing_debt_returns_none(self):
        results = {
            "finance_expense_ratio": {2023: 0.05},
            "interest_bearing_debt": {},
        }
        output = calculate(results)
        assert output[2023] is None

    def test_different_years(self):
        results = {
            "finance_expense_ratio": {2021: 0.03, 2022: 0.04},
            "interest_bearing_debt": {2022: 800000000, 2023: 1000000000},
        }
        output = calculate(results)
        assert output[2022] == pytest.approx(5e-11, rel=1e-9)
        # 2021: 只有 fe_ratio，没有 debt -> debt 视为 0，返回 None
        assert output[2021] is None
        # 2023: 只有 debt，没有 fe_ratio -> 不会出现在输出中
        assert 2023 not in output

    def test_output_field_constant(self):
        assert OUTPUT_FIELD == "financing_cost_rate"
