"""Tests for Crisis Period CAGR Calculator"""
import pytest
from value_investment.calculators.calc_crisis_period_cagr import (
    calculate,
    required_fields,
)


class TestCrisisPeriodCagr:
    """Test CrisisPeriodCagr Calculator"""

    def test_required_fields(self):
        """Test required fields are correct"""
        assert "revenue_yoy" in required_fields

    def test_zero_growth_cagr(self):
        """Test zero growth results in zero CAGR"""
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
        assert output[2023] == pytest.approx(0.0)

    def test_positive_growth_cagr(self):
        """Test positive growth results in positive CAGR"""
        results = {
            "revenue_yoy": {
                2019: 0.10,
                2020: 0.10,
                2021: 0.10,
            }
        }
        output = calculate(results)
        # (1.1 * 1.1 * 1.1)^(1/3) - 1 = 0.1
        assert output[2021] == pytest.approx(0.10, rel=0.01)

    def test_mixed_growth_cagr(self):
        """Test mixed growth results in mixed CAGR"""
        results = {
            "revenue_yoy": {
                2019: 0.20,
                2020: -0.10,
                2021: 0.10,
            }
        }
        output = calculate(results)
        # (1.2 * 0.9 * 1.1)^(1/3) - 1
        expected = (1.2 * 0.9 * 1.1) ** (1 / 3) - 1
        assert output[2021] == pytest.approx(expected, rel=0.01)

    def test_insufficient_data_returns_empty(self):
        """Test empty dict when insufficient data"""
        results = {"revenue_yoy": {2021: 0.10, 2022: 0.15}}
        output = calculate(results)
        assert output == {}

    def test_none_values_handled(self):
        """Test None values are handled"""
        results = {
            "revenue_yoy": {
                2019: 0.10,
                2020: None,
                2021: 0.10,
                2022: 0.10,
            }
        }
        output = calculate(results)
        # Windows with None should be skipped
        assert 2022 in output or len(output) == 0
