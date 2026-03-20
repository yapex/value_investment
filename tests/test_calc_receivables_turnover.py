"""Tests for Receivables Turnover Calculator"""
import pytest
from value_investment.calculators.calc_receivables_turnover import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestReceivablesTurnover:
    """Test cases for receivables_turnover calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        assert set(required_fields) == {"total_revenue", "accounts_receivable"}

    def test_basic_calculation(self):
        """Test basic receivables turnover calculation"""
        results = {
            "total_revenue": {2023: 500000000, 2022: 400000000},
            "accounts_receivable": {2023: 50000000, 2022: 40000000},
        }
        output = calculate(results)

        # 2023: 500M / ((50M + 40M) / 2) = 500M / 45M = 11.11...
        assert output[2023] == pytest.approx(11.11, rel=1e-2)
        # 2022: 无上一年数据，无法计算平均，返回 None
        assert output[2022] is None

    def test_multi_year_calculation(self):
        """Test turnover with multiple years of data"""
        results = {
            "total_revenue": {2023: 600000000, 2022: 500000000, 2021: 400000000},
            "accounts_receivable": {2023: 60000000, 2022: 50000000, 2021: 40000000},
        }
        output = calculate(results)

        # 2023: 600M / ((60M + 50M) / 2) = 600M / 55M = 10.91...
        assert output[2023] == pytest.approx(10.91, rel=1e-2)
        # 2022: 500M / ((50M + 40M) / 2) = 500M / 45M = 11.11...
        assert output[2022] == pytest.approx(11.11, rel=1e-2)
        # 2021: 无上一年数据，无法计算平均，返回 None
        assert output[2021] is None

    def test_zero_receivable_returns_none(self):
        """Test that zero receivables returns None"""
        results = {
            "total_revenue": {2023: 500000000},
            "accounts_receivable": {2023: 0},
        }
        output = calculate(results)

        assert output[2023] is None

    def test_missing_receivable_returns_none(self):
        """Test that missing receivables returns None"""
        results = {
            "total_revenue": {2023: 500000000},
            "accounts_receivable": {},
        }
        output = calculate(results)

        assert output[2023] is None

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "receivables_turnover"
