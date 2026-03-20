"""Tests for Gross Margin Volatility Calculator"""
import pytest
from value_investment.calculators.calc_gross_margin_volatility import (
    calculate,
    required_fields,
)


class TestGrossMarginVolatility:
    """Test GrossMarginVolatility Calculator"""

    def test_required_fields(self):
        """Test required fields are correct"""
        assert "gross_margin" in required_fields

    def test_stable_margins_low_volatility(self):
        """Test stable margins result in low volatility"""
        results = {
            "gross_margin": {
                2019: 0.30,
                2020: 0.31,
                2021: 0.30,
                2022: 0.30,
                2023: 0.31,
            }
        }
        output = calculate(results)
        # Very stable margins -> low coefficient of variation
        assert output[2023] < 0.1

    def test_volatile_margins_high_volatility(self):
        """Test volatile margins result in high volatility"""
        results = {
            "gross_margin": {
                2019: 0.10,
                2020: 0.40,
                2021: 0.15,
                2022: 0.35,
                2023: 0.20,
            }
        }
        output = calculate(results)
        # Volatile margins -> higher coefficient of variation
        assert output[2023] > 0.3

    def test_insufficient_data_returns_empty(self):
        """Test empty dict when insufficient data"""
        results = {"gross_margin": {2021: 0.30, 2022: 0.31, 2023: 0.30}}
        output = calculate(results)
        assert output == {}

    def test_zero_mean_skipped(self):
        """Test zero mean is not included in output"""
        results = {
            "gross_margin": {
                2019: 0.0,
                2020: 0.0,
                2021: 0.0,
                2022: 0.0,
                2023: 0.0,
            }
        }
        output = calculate(results)
        assert output == {}

    def test_missing_values_skipped(self):
        """Test missing values in window are handled"""
        results = {
            "gross_margin": {
                2019: 0.30,
                2020: 0.31,
                2021: None,
                2022: 0.30,
                2023: 0.31,
            }
        }
        output = calculate(results)
        # Should skip windows with None
        assert 2023 not in output or output[2023] < 0.1
