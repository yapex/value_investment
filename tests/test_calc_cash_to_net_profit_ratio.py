"""Tests for Cash to Net Profit Ratio Calculator"""
import pytest
from value_investment.calculators.calc_cash_to_net_profit_ratio import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestCashToNetProfitRatio:
    """Test cases for cash_to_net_profit_ratio calculator"""

    def test_required_fields(self):
        expected = ["operating_cash_flow", "net_profit"]
        assert required_fields == expected

    def test_basic_calculation(self):
        results = {
            "operating_cash_flow": {2023: 500000000, 2022: 400000000},
            "net_profit": {2023: 400000000, 2022: 320000000},
        }
        output = calculate(results)
        assert output[2023] == pytest.approx(1.25, rel=1e-9)
        assert output[2022] == pytest.approx(1.25, rel=1e-9)

    def test_zero_net_profit_returns_none(self):
        results = {
            "operating_cash_flow": {2023: 500000000},
            "net_profit": {2023: 0},
        }
        output = calculate(results)
        assert output[2023] is None

    def test_negative_ocf(self):
        results = {
            "operating_cash_flow": {2023: -100000000},
            "net_profit": {2023: 400000000},
        }
        output = calculate(results)
        assert output[2023] == pytest.approx(-0.25, rel=1e-9)

    def test_missing_net_profit_returns_none(self):
        results = {
            "operating_cash_flow": {2023: 500000000},
            "net_profit": {},
        }
        output = calculate(results)
        assert output[2023] is None

    def test_different_years(self):
        results = {
            "operating_cash_flow": {2021: 300000000, 2022: 400000000},
            "net_profit": {2022: 320000000, 2023: 400000000},
        }
        output = calculate(results)
        assert output[2022] == pytest.approx(1.25, rel=1e-9)
        # 2021: 只有 ocf，没有 net_profit -> net_profit 视为 0，返回 None
        assert output[2021] is None
        # 2023: 只有 net_profit，没有 ocf -> 不会出现在输出中
        assert 2023 not in output

    def test_output_field_constant(self):
        assert OUTPUT_FIELD == "cash_to_net_profit_ratio"
