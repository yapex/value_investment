"""Tests for Fair Value Change Ratio Calculator"""
import pytest
from value_investment.calculators.calc_fair_value_change_ratio import (
    calculate,
    required_fields,
)


class TestFairValueChangeRatio:
    """Test FairValueChangeRatio Calculator"""

    def test_required_fields(self):
        """Test required fields are correct"""
        assert "fair_value_change" in required_fields
        assert "net_profit" in required_fields

    def test_basic_calculation(self):
        """Test basic ratio calculation"""
        results = {
            "fair_value_change": {2021: 1000, 2022: 2000, 2023: 1500},
            "net_profit": {2021: 10000, 2022: 20000, 2023: 15000},
        }
        output = calculate(results)
        assert output[2021] == pytest.approx(0.1)
        assert output[2022] == pytest.approx(0.1)
        assert output[2023] == pytest.approx(0.1)

    def test_negative_net_profit_calculation(self):
        """Test calculation when net_profit is negative"""
        results = {
            "fair_value_change": {2021: 1000, 2022: 2000},
            "net_profit": {2021: 10000, 2022: -5000},
        }
        output = calculate(results)
        assert output[2021] == pytest.approx(0.1)
        assert output[2022] == pytest.approx(-0.4)

    def test_zero_net_profit_returns_none(self):
        """Test None when net_profit is zero"""
        results = {
            "fair_value_change": {2021: 1000},
            "net_profit": {2021: 0},
        }
        output = calculate(results)
        assert output[2021] is None

    def test_missing_fair_value_not_in_output(self):
        """Test year without fair_value_change is not in output"""
        results = {
            "fair_value_change": {2021: 1000},
            "net_profit": {2021: 10000, 2022: 20000},
        }
        output = calculate(results)
        assert 2021 in output
        assert 2022 not in output

    def test_missing_net_profit_returns_none(self):
        """Test None when net_profit is missing"""
        results = {
            "fair_value_change": {2021: 1000, 2022: 2000},
            "net_profit": {2021: 10000},
        }
        output = calculate(results)
        assert 2021 in output
        assert 2022 in output
        assert output[2022] is None
