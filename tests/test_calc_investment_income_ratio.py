"""Tests for Investment Income Ratio Calculator"""
import pytest
from value_investment.calculators.calc_investment_income_ratio import (
    calculate,
    required_fields,
)


class TestInvestmentIncomeRatio:
    """Test InvestmentIncomeRatio Calculator"""

    def test_required_fields(self):
        """Test required fields are correct"""
        assert "investment_income" in required_fields
        assert "net_profit" in required_fields

    def test_basic_calculation(self):
        """Test basic ratio calculation"""
        results = {
            "investment_income": {2021: 500, 2022: 1000, 2023: 800},
            "net_profit": {2021: 10000, 2022: 20000, 2023: 16000},
        }
        output = calculate(results)
        assert output[2021] == pytest.approx(0.05)
        assert output[2022] == pytest.approx(0.05)
        assert output[2023] == pytest.approx(0.05)

    def test_negative_investment_income(self):
        """Test negative investment income (loss)"""
        results = {
            "investment_income": {2021: -500, 2022: 1000},
            "net_profit": {2021: 10000, 2022: 20000},
        }
        output = calculate(results)
        assert output[2021] == pytest.approx(-0.05)
        assert output[2022] == pytest.approx(0.05)

    def test_zero_net_profit_returns_none(self):
        """Test None when net_profit is zero"""
        results = {
            "investment_income": {2021: 500},
            "net_profit": {2021: 0},
        }
        output = calculate(results)
        assert output[2021] is None

    def test_missing_fields_not_in_output(self):
        """Test missing fields are not in output"""
        results = {
            "investment_income": {2021: 500},
            "net_profit": {2021: 10000, 2022: 20000},
        }
        output = calculate(results)
        assert 2022 not in output
