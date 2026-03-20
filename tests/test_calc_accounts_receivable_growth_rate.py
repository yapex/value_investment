"""Tests for Accounts Receivable Growth Rate Calculator"""
import pytest
from value_investment.calculators.calc_accounts_receivable_growth_rate import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestAccountsReceivableGrowthRate:
    """Test cases for accounts_receivable_growth_rate calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert required_fields == ["accounts_receivable"]

    def test_basic_calculation(self):
        """Test basic AR growth rate calculation"""
        results = {
            "accounts_receivable": {2023: 120, 2022: 100, 2021: 80},
        }
        output = calculate(results)
        
        # (120 - 100) / 100 = 0.2
        assert output[2023] == pytest.approx(0.2, rel=1e-9)
        # (100 - 80) / 80 = 0.25
        assert output[2022] == pytest.approx(0.25, rel=1e-9)

    def test_first_year_no_prev_returns_none(self):
        """Test that first year with no previous data returns None"""
        results = {
            "accounts_receivable": {2023: 120},
        }
        output = calculate(results)
        
        assert 2023 not in output

    def test_zero_prev_ar_not_in_output(self):
        """Test that zero previous AR is skipped (avoids division by zero)"""
        results = {
            "accounts_receivable": {2023: 120, 2022: 0},
        }
        output = calculate(results)
        
        assert 2023 not in output

    def test_negative_growth_rate(self):
        """Test when AR decreases (negative growth)"""
        results = {
            "accounts_receivable": {2023: 80, 2022: 100},
        }
        output = calculate(results)
        
        # (80 - 100) / 100 = -0.2
        assert output[2023] == pytest.approx(-0.2, rel=1e-9)

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "accounts_receivable_growth_rate"
