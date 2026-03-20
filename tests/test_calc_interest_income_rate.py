"""Tests for Interest Income Rate Calculator"""
import pytest
from value_investment.calculators.calc_interest_income_rate import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestInterestIncomeRate:
    """Test cases for interest_income_rate calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert required_fields == ["interest_income", "cash_and_equivalents"]

    def test_basic_calculation(self):
        """Test basic interest income rate calculation"""
        results = {
            "interest_income": {2023: 100, 2022: 80},
            "cash_and_equivalents": {2023: 1000, 2022: 800},
        }
        output = calculate(results)
        
        # 100 / 1000 = 0.1
        assert output[2023] == pytest.approx(0.1, rel=1e-9)
        # 80 / 800 = 0.1
        assert output[2022] == pytest.approx(0.1, rel=1e-9)

    def test_missing_cash_returns_none(self):
        """Test that missing cash returns None"""
        results = {
            "interest_income": {2023: 100},
            "cash_and_equivalents": {},
        }
        output = calculate(results)
        
        assert 2023 not in output

    def test_zero_cash_returns_none(self):
        """Test that zero cash returns None (avoids division by zero)"""
        results = {
            "interest_income": {2023: 100},
            "cash_and_equivalents": {2023: 0},
        }
        output = calculate(results)
        
        assert 2023 not in output

    def test_negative_interest_income(self):
        """Test when interest income is negative (possible for some companies)"""
        results = {
            "interest_income": {2023: -50},
            "cash_and_equivalents": {2023: 1000},
        }
        output = calculate(results)
        
        # -50 / 1000 = -0.05
        assert output[2023] == pytest.approx(-0.05, rel=1e-9)

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "interest_income_rate"
