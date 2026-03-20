"""Test for Net Profit CAGR 5-Year Calculator

Formula: CAGR = (end_value / start_value) ^ (1 / 5) - 1
"""
import pytest
from value_investment.calculators.calc_net_profit_cagr_5y import calculate, required_fields, OUTPUT_FIELD


class TestNetProfitCAGR5Y:
    """Test net profit CAGR 5-year calculation"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert "net_profit" in required_fields

    def test_basic_calculation(self):
        """Test basic CAGR calculation with 5 years of data"""
        # Net profit: 100 -> 150 over 5 years
        # CAGR = (150/100)^(1/5) - 1 = 1.5^0.2 - 1 ≈ 0.0845
        results = {
            "net_profit": {
                2023: 150.0,
                2022: 140.0,
                2021: 130.0,
                2020: 120.0,
                2019: 100.0,
            },
        }

        cagr = calculate(results)

        # Should calculate CAGR for 2023 (using 2019-2023)
        assert 2023 in cagr
        assert cagr[2023] == pytest.approx(0.0845, rel=1e-2)

    def test_negative_cagr(self):
        """Test CAGR with declining profit"""
        # Net profit: 200 -> 100 over 5 years (declining)
        results = {
            "net_profit": {
                2023: 100.0,
                2022: 120.0,
                2021: 140.0,
                2020: 160.0,
                2019: 200.0,
            },
        }

        cagr = calculate(results)
        # Should be negative
        assert 2023 in cagr
        assert cagr[2023] < 0

    def test_insufficient_data(self):
        """Test handling of insufficient data (less than 5 years)"""
        results = {
            "net_profit": {
                2023: 150.0,
                2022: 140.0,
                2021: 130.0,
            },
        }

        cagr = calculate(results)
        assert len(cagr) == 0

    def test_loss_to_profit(self):
        """Test with loss turning to profit"""
        # Net profit: -50 -> 100 over 5 years
        # This is problematic for CAGR
        results = {
            "net_profit": {
                2023: 100.0,
                2022: 50.0,
                2021: 0.0,
                2020: -25.0,
                2019: -50.0,
            },
        }

        cagr = calculate(results)
        # Should handle negative values appropriately
        # Result depends on implementation (may skip or calculate)
        # Just verify it doesn't crash
        assert isinstance(cagr, dict)

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD constant is defined"""
        assert OUTPUT_FIELD == "net_profit_cagr_5y"

    def test_zero_start_value(self):
        """Test handling of zero start value"""
        results = {
            "net_profit": {
                2023: 150.0,
                2022: 140.0,
                2021: 130.0,
                2020: 120.0,
                2019: 0.0,
            },
        }

        cagr = calculate(results)
        assert 2023 not in cagr or cagr[2023] is None

    def test_none_values(self):
        """Test handling of None values in data"""
        results = {
            "net_profit": {
                2023: 150.0,
                2022: None,
                2021: 130.0,
                2020: 120.0,
                2019: 100.0,
            },
        }

        cagr = calculate(results)
        assert 2023 not in cagr or cagr[2023] is None
