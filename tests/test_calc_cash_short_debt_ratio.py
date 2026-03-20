"""Tests for Cash Short-term Debt Ratio Calculator"""
import pytest
from value_investment.calculators.calc_cash_short_debt_ratio import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestCashShortDebtRatio:
    """Test cases for cash_short_debt_ratio calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert set(required_fields) == {"cash_and_equivalents", "short_term_borrowings"}

    def test_basic_calculation(self):
        """Test basic cash to short-term debt ratio calculation"""
        results = {
            "cash_and_equivalents": {2023: 200000000, 2022: 150000000},
            "short_term_borrowings": {2023: 100000000, 2022: 100000000},
        }
        output = calculate(results)

        # 2023: 200M / 100M = 2.0
        assert output[2023] == pytest.approx(2.0, rel=1e-9)
        # 2022: 150M / 100M = 1.5
        assert output[2022] == pytest.approx(1.5, rel=1e-9)

    def test_safe_ratio_above_one(self):
        """Test ratio above 1 (safe level)"""
        results = {
            "cash_and_equivalents": {2023: 150000000},
            "short_term_borrowings": {2023: 100000000},
        }
        output = calculate(results)

        # 150M / 100M = 1.5 (>1 indicates sufficient liquidity)
        assert output[2023] == pytest.approx(1.5, rel=1e-9)

    def test_unsafe_ratio_below_one(self):
        """Test ratio below 1 (potential liquidity risk)"""
        results = {
            "cash_and_equivalents": {2023: 50000000},
            "short_term_borrowings": {2023: 100000000},
        }
        output = calculate(results)

        # 50M / 100M = 0.5 (<1 indicates liquidity risk)
        assert output[2023] == pytest.approx(0.5, rel=1e-9)

    def test_zero_debt_returns_none(self):
        """Test that zero debt returns None"""
        results = {
            "cash_and_equivalents": {2023: 200000000},
            "short_term_borrowings": {2023: 0},
        }
        output = calculate(results)

        assert output[2023] is None

    def test_missing_debt_returns_none(self):
        """Test that missing debt returns None"""
        results = {
            "cash_and_equivalents": {2023: 200000000},
            "short_term_borrowings": {},
        }
        output = calculate(results)

        assert output[2023] is None

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "cash_short_debt_ratio"
