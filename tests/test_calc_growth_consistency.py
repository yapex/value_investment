"""Tests for Growth Consistency Calculator"""
import pytest
from value_investment.calculators.calc_growth_consistency import (
    calculate,
    required_fields,
)


class TestGrowthConsistency:
    """Test GrowthConsistency Calculator"""

    def test_required_fields(self):
        """Test required fields are correct"""
        assert "revenue_yoy" in required_fields

    def test_basic_calculation(self):
        """Test basic consistency calculation"""
        results = {
            "revenue_yoy": {
                2019: 0.10,
                2020: 0.15,
                2021: 0.20,
                2022: 0.12,
                2023: 0.18,
            }
        }
        output = calculate(results)
        # 5 positive years / 5 total years = 1.0
        assert output[2023] == pytest.approx(1.0)

    def test_partial_consistency(self):
        """Test partial consistency (some negative years)"""
        results = {
            "revenue_yoy": {
                2019: 0.10,
                2020: -0.05,
                2021: 0.20,
                2022: 0.12,
                2023: 0.18,
            }
        }
        output = calculate(results)
        # 4 positive years / 5 total years = 0.8
        assert output[2023] == pytest.approx(0.8)

    def test_no_consistency(self):
        """Test no consistency (all negative years)"""
        results = {
            "revenue_yoy": {
                2019: -0.10,
                2020: -0.05,
                2021: -0.02,
                2022: -0.08,
                2023: -0.03,
            }
        }
        output = calculate(results)
        # 0 positive years / 5 total years = 0.0
        assert output[2023] == pytest.approx(0.0)

    def test_insufficient_data_returns_empty(self):
        """Test empty dict when insufficient data"""
        results = {"revenue_yoy": {2021: 0.10, 2022: 0.15, 2023: 0.20}}
        output = calculate(results)
        assert output == {}

    def test_threshold_exactly_zero(self):
        """Test threshold exactly zero is treated as not positive"""
        results = {
            "revenue_yoy": {
                2019: 0.0,
                2020: 0.0,
                2021: 0.0,
                2022: 0.0,
                2023: 0.0,
            }
        }
        output = calculate(results)
        # 0 growth years = 0, threshold > 0 so not counted
        assert output[2023] == pytest.approx(0.0)
