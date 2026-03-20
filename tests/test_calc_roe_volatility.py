"""Test for ROE Volatility Calculator

Formula: Volatility = StdDev / Mean (coefficient of variation)
Uses rolling window of 5 years for calculation.
"""
import pytest
from value_investment.calculators.calc_roe_volatility import calculate, required_fields, OUTPUT_FIELD


class TestROEVolatility:
    """Test ROE volatility calculation"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert "roe" in required_fields

    def test_basic_calculation(self):
        """Test basic volatility calculation with stable ROE"""
        # Stable ROE: all values around 15%
        results = {
            "roe": {
                2023: 0.15,
                2022: 0.15,
                2021: 0.15,
                2020: 0.15,
                2019: 0.15,
            },
        }

        volatility = calculate(results)
        # Stable data should have low volatility
        assert 2023 in volatility
        assert volatility[2023] == pytest.approx(0.0, rel=1e-6)

    def test_volatile_roe(self):
        """Test volatility calculation with varying ROE"""
        # Varying ROE: 10%, 15%, 20%, 15%, 10%
        # Mean = 14%, StdDev ≈ 4.47%
        # Volatility ≈ 0.319
        results = {
            "roe": {
                2023: 0.10,
                2022: 0.15,
                2021: 0.20,
                2020: 0.15,
                2019: 0.10,
            },
        }

        volatility = calculate(results)
        assert 2023 in volatility
        # Should be greater than 0 for varying data
        assert volatility[2023] > 0

    def test_insufficient_data(self):
        """Test handling of insufficient data (less than window)"""
        results = {
            "roe": {
                2023: 0.15,
                2022: 0.15,
                2021: 0.15,
            },
        }

        volatility = calculate(results)
        assert len(volatility) == 0

    def test_zero_mean(self):
        """Test handling of zero mean (all zeros or negative)"""
        results = {
            "roe": {
                2023: 0.0,
                2022: 0.0,
                2021: 0.0,
                2020: 0.0,
                2019: 0.0,
            },
        }

        volatility = calculate(results)
        # Should handle zero mean appropriately
        assert 2023 not in volatility or volatility[2023] is None

    def test_longer_time_series(self):
        """Test with longer time series (more than 5 years)"""
        results = {
            "roe": {
                2023: 0.18,
                2022: 0.15,
                2021: 0.12,
                2020: 0.20,
                2019: 0.16,
                2018: 0.14,
                2017: 0.17,
            },
        }

        volatility = calculate(results)
        # Should calculate using rolling window
        assert 2023 in volatility
        assert 2022 in volatility
        assert 2021 in volatility

    def test_none_values(self):
        """Test handling of None values in data"""
        results = {
            "roe": {
                2023: 0.15,
                2022: None,
                2021: 0.15,
                2020: 0.15,
                2019: 0.15,
            },
        }

        volatility = calculate(results)
        # Should skip calculation when any value is None
        assert 2023 not in volatility or volatility[2023] is None

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD constant is defined"""
        assert OUTPUT_FIELD == "roe_volatility"

    def test_percentage_values(self):
        """Test with percentage format values (e.g., 15 for 15%)"""
        results = {
            "roe": {
                2023: 15.0,  # 15%
                2022: 15.0,
                2021: 15.0,
                2020: 15.0,
                2019: 15.0,
            },
        }

        volatility = calculate(results)
        # Should handle percentage values same as decimal
        assert 2023 in volatility
        assert volatility[2023] == pytest.approx(0.0, rel=1e-6)
