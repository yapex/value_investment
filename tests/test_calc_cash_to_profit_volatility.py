"""Tests for Cash to Profit Volatility Calculator"""
import pytest
from value_investment.calculators.calc_cash_to_profit_volatility import (
    calculate,
    required_fields,
)


class TestCashToProfitVolatility:
    """Test CashToProfitVolatility Calculator"""

    def test_required_fields(self):
        """Test required fields are correct"""
        assert "operating_cash_flow" in required_fields
        assert "net_profit" in required_fields

    def test_stable_cash_profit_low_volatility(self):
        """Test stable cash/profit results in low volatility"""
        results = {
            "operating_cash_flow": {
                2019: 1100,
                2020: 1200,
                2021: 1150,
                2022: 1180,
                2023: 1220,
            },
            "net_profit": {
                2019: 1000,
                2020: 1000,
                2021: 1000,
                2022: 1000,
                2023: 1000,
            },
        }
        output = calculate(results)
        # Ratio ~1.1-1.2, stable -> low CV
        assert output[2023] < 0.15

    def test_volatile_cash_profit_high_volatility(self):
        """Test volatile cash/profit results in high volatility"""
        results = {
            "operating_cash_flow": {
                2019: 2000,
                2020: 500,
                2021: 1800,
                2022: 400,
                2023: 1600,
            },
            "net_profit": {
                2019: 1000,
                2020: 1000,
                2021: 1000,
                2022: 1000,
                2023: 1000,
            },
        }
        output = calculate(results)
        # Ratios: 2.0, 0.5, 1.8, 0.4, 1.6 -> high variation
        assert output[2023] > 0.5

    def test_insufficient_data_returns_empty(self):
        """Test empty dict when insufficient data"""
        results = {
            "operating_cash_flow": {2021: 1100, 2022: 1200, 2023: 1150},
            "net_profit": {2021: 1000, 2022: 1000, 2023: 1000},
        }
        output = calculate(results)
        assert output == {}

    def test_zero_net_profit_skipped_in_ratio(self):
        """Test zero net_profit is skipped in ratio calculation"""
        results = {
            "operating_cash_flow": {
                2018: 1100,
                2019: 1100,
                2020: 1200,
                2021: 1150,
                2022: 1180,
                2023: 1220,
            },
            "net_profit": {
                2018: 1000,
                2019: 1000,
                2020: 0,
                2021: 1000,
                2022: 1000,
                2023: 1000,
            },
        }
        output = calculate(results)
        # 2020 ratio not calculated due to zero net_profit, but 2023 should be in output
        assert 2023 in output

    def test_missing_net_profit_skipped_in_ratio(self):
        """Test missing net_profit is skipped"""
        results = {
            "operating_cash_flow": {
                2018: 1100,
                2019: 1100,
                2020: 1200,
                2021: 1150,
                2022: 1180,
                2023: 1220,
            },
            "net_profit": {
                2018: 1000,
                2019: 1000,
                2021: 1000,
                2022: 1000,
                2023: 1000,
            },
        }
        output = calculate(results)
        # 2020 ratio not calculated due to missing net_profit, but 2023 should be in output
        assert 2023 in output
