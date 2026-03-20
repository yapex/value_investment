"""Tests for Interest Coverage Ratio Calculator"""
import pytest
from value_investment.calculators.calc_interest_coverage_ratio import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestInterestCoverageRatio:
    """Test cases for interest_coverage_ratio calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        expected = ["operating_profit", "interest_expense"]
        assert required_fields == expected

    def test_basic_calculation(self):
        """Test basic interest coverage ratio calculation"""
        results = {
            "operating_profit": {2023: 100000000, 2022: 80000000, 2021: 60000000},
            "interest_expense": {2023: 10000000, 2022: 10000000, 2021: 10000000},
        }
        output = calculate(results)
        
        assert output[2023] == pytest.approx(10.0, rel=1e-9)  # 100000000/10000000 = 10
        assert output[2022] == pytest.approx(8.0, rel=1e-9)  # 80000000/10000000 = 8
        assert output[2021] == pytest.approx(6.0, rel=1e-9)  # 60000000/10000000 = 6

    def test_zero_interest_returns_none(self):
        """Test that zero interest expense returns None (avoids division by zero)"""
        results = {
            "operating_profit": {2023: 100000000},
            "interest_expense": {2023: 0},
        }
        output = calculate(results)
        
        assert output[2023] is None

    def test_operating_loss(self):
        """Test when operating profit is negative (operating loss)"""
        results = {
            "operating_profit": {2023: -10000000},  # Operating loss
            "interest_expense": {2023: 10000000},
        }
        output = calculate(results)
        
        assert output[2023] == pytest.approx(-1.0, rel=1e-9)

    def test_missing_field_returns_none(self):
        """Test that missing interest_expense returns None (division by zero)"""
        results = {
            "operating_profit": {2023: 100000000},
            "interest_expense": {},  # Empty
        }
        output = calculate(results)
        
        # interest_expense 缺失时视为 0，导致除以零返回 None
        assert output[2023] is None

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "interest_coverage_ratio"

    def test_varying_interest_over_years(self):
        """Test with varying interest expense across years"""
        results = {
            "operating_profit": {2023: 100000000, 2022: 80000000},
            "interest_expense": {2023: 20000000, 2022: 10000000},
        }
        output = calculate(results)
        
        assert output[2023] == pytest.approx(5.0, rel=1e-9)  # 100M/20M = 5
        assert output[2022] == pytest.approx(8.0, rel=1e-9)  # 80M/10M = 8
