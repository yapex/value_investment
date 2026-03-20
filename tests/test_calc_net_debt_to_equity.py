"""Tests for Net Debt to Equity Calculator"""
import pytest
from value_investment.calculators.calc_net_debt_to_equity import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestNetDebtToEquity:
    """Test cases for net_debt_to_equity calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        expected = ["net_debt", "total_equity"]
        assert required_fields == expected

    def test_basic_calculation(self):
        """Test basic net debt to equity calculation"""
        results = {
            "net_debt": {2023: 1000000, 2022: 800000, 2021: 600000},
            "total_equity": {2023: 2000000, 2022: 1800000, 2021: 1500000},
        }
        output = calculate(results)
        
        assert output[2023] == pytest.approx(0.5, rel=1e-9)  # 1000000/2000000 = 0.5
        assert output[2022] == pytest.approx(0.4444, rel=1e-3)  # 800000/1800000 ≈ 0.4444
        assert output[2021] == pytest.approx(0.4, rel=1e-9)  # 600000/1500000 = 0.4

    def test_zero_equity_returns_none(self):
        """Test that zero equity returns None (avoids division by zero)"""
        results = {
            "net_debt": {2023: 1000000},
            "total_equity": {2023: 0},
        }
        output = calculate(results)
        
        assert output[2023] is None

    def test_negative_equity(self):
        """Test negative equity (levered company)"""
        results = {
            "net_debt": {2023: 1000000},
            "total_equity": {2023: -500000},  # Negative equity
        }
        output = calculate(results)
        
        assert output[2023] == pytest.approx(-2.0, rel=1e-9)

    def test_missing_field_returns_zero(self):
        """Test that missing net_debt returns 0 for that year"""
        results = {
            "net_debt": {},  # Empty
            "total_equity": {2023: 2000000},
        }
        output = calculate(results)
        
        assert output == {}  # No output since net_debt has no years

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "net_debt_to_equity"

    def test_calculation_with_negative_net_debt(self):
        """Test when net debt is negative (more cash than debt)"""
        results = {
            "net_debt": {2023: -500000},  # Net cash position
            "total_equity": {2023: 2000000},
        }
        output = calculate(results)
        
        assert output[2023] == pytest.approx(-0.25, rel=1e-9)
