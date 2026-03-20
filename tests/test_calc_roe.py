"""Tests for ROE Calculator"""
import pytest
from value_investment.calculators.calc_roe import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestROE:
    """Test cases for roe calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert set(required_fields) == {"net_profit", "total_equity"}

    def test_basic_calculation(self):
        """Test basic ROE calculation with average equity"""
        results = {
            "net_profit": {2023: 100000000, 2022: 80000000},
            "total_equity": {2023: 500000000, 2022: 400000000},
        }
        output = calculate(results)

        # 2023: 100000000 / ((500000000 + 400000000) / 2) = 100000000 / 450000000 = 0.2222...
        assert output[2023] == pytest.approx(0.2222, rel=1e-2)
        # 2022: 无上一年数据，无法计算平均，返回 None
        assert output[2022] is None

    def test_multi_year_calculation(self):
        """Test ROE with multiple years of data"""
        results = {
            "net_profit": {2023: 120000000, 2022: 100000000, 2021: 80000000},
            "total_equity": {2023: 600000000, 2022: 500000000, 2021: 400000000},
        }
        output = calculate(results)

        # 2023: 120M / ((600M + 500M) / 2) = 120M / 550M = 0.21818...
        assert output[2023] == pytest.approx(0.21818, rel=1e-2)
        # 2022: 100M / ((500M + 400M) / 2) = 100M / 450M = 0.2222...
        assert output[2022] == pytest.approx(0.2222, rel=1e-2)
        # 2021: 无上一年数据，无法计算平均，返回 None
        assert output[2021] is None

    def test_zero_equity_returns_none(self):
        """Test that zero equity returns None"""
        results = {
            "net_profit": {2023: 100000000},
            "total_equity": {2023: 0},
        }
        output = calculate(results)

        assert output[2023] is None

    def test_missing_equity_returns_none(self):
        """Test that missing equity returns None"""
        results = {
            "net_profit": {2023: 100000000},
            "total_equity": {},
        }
        output = calculate(results)

        assert output[2023] is None

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "roe"
