"""Tests for Prepayment Ratio Calculator"""
import pytest
from value_investment.calculators.calc_prepayment_ratio import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestPrepaymentRatio:
    """Test cases for prepayment_ratio calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert required_fields == ["prepayment", "total_assets"]

    def test_basic_calculation(self):
        """Test basic prepayment ratio calculation"""
        results = {
            "prepayment": {2023: 50, 2022: 40},
            "total_assets": {2023: 1000, 2022: 800},
        }
        output = calculate(results)
        
        # 50 / 1000 = 0.05
        assert output[2023] == pytest.approx(0.05, rel=1e-9)
        # 40 / 800 = 0.05
        assert output[2022] == pytest.approx(0.05, rel=1e-9)

    def test_missing_total_assets_returns_none(self):
        """Test that missing total_assets returns None"""
        results = {
            "prepayment": {2023: 50},
            "total_assets": {},
        }
        output = calculate(results)
        
        assert 2023 not in output

    def test_zero_total_assets_returns_none(self):
        """Test that zero total_assets returns None (avoids division by zero)"""
        results = {
            "prepayment": {2023: 50},
            "total_assets": {2023: 0},
        }
        output = calculate(results)
        
        assert 2023 not in output

    def test_zero_prepayment(self):
        """Test when prepayment is zero"""
        results = {
            "prepayment": {2023: 0},
            "total_assets": {2023: 1000},
        }
        output = calculate(results)
        
        # 0 / 1000 = 0
        assert output[2023] == pytest.approx(0.0, rel=1e-9)

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "prepayment_ratio"
