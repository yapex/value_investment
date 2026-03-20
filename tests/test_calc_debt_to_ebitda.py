"""Tests for Debt to EBITDA Calculator"""
import pytest
from value_investment.calculators.calc_debt_to_ebitda import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestDebtToEbitda:
    """Test cases for debt_to_ebitda calculator"""

    def test_required_fields(self):
        expected = ["total_debt", "ebitda"]
        assert required_fields == expected

    def test_basic_calculation(self):
        results = {
            "total_debt": {2023: 1000000000, 2022: 800000000},
            "ebitda": {2023: 400000000, 2022: 320000000},
        }
        output = calculate(results)
        assert output[2023] == pytest.approx(2.5, rel=1e-9)
        assert output[2022] == pytest.approx(2.5, rel=1e-9)

    def test_zero_ebitda_returns_none(self):
        results = {
            "total_debt": {2023: 1000000000},
            "ebitda": {2023: 0},
        }
        output = calculate(results)
        assert output[2023] is None

    def test_negative_debt(self):
        results = {
            "total_debt": {2023: -100000000},
            "ebitda": {2023: 400000000},
        }
        output = calculate(results)
        assert output[2023] == pytest.approx(-0.25, rel=1e-9)

    def test_missing_ebitda_returns_none(self):
        results = {
            "total_debt": {2023: 1000000000},
            "ebitda": {},
        }
        output = calculate(results)
        assert output[2023] is None

    def test_different_years(self):
        results = {
            "total_debt": {2021: 600000000, 2022: 800000000},
            "ebitda": {2022: 320000000, 2023: 400000000},
        }
        output = calculate(results)
        assert output[2022] == pytest.approx(2.5, rel=1e-9)
        # 2021: 只有 total_debt，没有 ebitda -> ebitda 视为 0，返回 None
        assert output[2021] is None
        # 2023: 只有 ebitda，没有 total_debt -> 不会出现在输出中
        assert 2023 not in output

    def test_output_field_constant(self):
        assert OUTPUT_FIELD == "debt_to_ebitda"
