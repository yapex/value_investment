"""Tests for Free Cash Flow to Debt Calculator"""
import pytest
from value_investment.calculators.calc_free_cash_flow_to_debt import (
    required_fields,
    calculate,
    OUTPUT_FIELD,
)


class TestFreeCashFlowToDebt:
    """Test cases for free_cash_flow_to_debt calculator"""

    def test_required_fields(self):
        """Test that required_fields contains expected fields"""
        expected = ["free_cash_flow_to_firm", "total_debt"]
        assert required_fields == expected

    def test_basic_calculation(self):
        """Test basic FCF to debt ratio calculation"""
        results = {
            "free_cash_flow_to_firm": {2023: 500000000, 2022: 400000000},
            "total_debt": {2023: 1000000000, 2022: 800000000},
        }
        output = calculate(results)
        
        assert output[2023] == pytest.approx(0.5, rel=1e-9)  # 500M/1000M = 0.5
        assert output[2022] == pytest.approx(0.5, rel=1e-9)  # 400M/800M = 0.5

    def test_zero_debt_returns_none(self):
        """Test that zero debt returns None (avoids division by zero)"""
        results = {
            "free_cash_flow_to_firm": {2023: 500000000},
            "total_debt": {2023: 0},
        }
        output = calculate(results)
        
        assert output[2023] is None

    def test_negative_fcf(self):
        """Test when free cash flow is negative"""
        results = {
            "free_cash_flow_to_firm": {2023: -100000000},  # Negative FCF
            "total_debt": {2023: 1000000000},
        }
        output = calculate(results)
        
        assert output[2023] == pytest.approx(-0.1, rel=1e-9)

    def test_missing_debt_returns_none(self):
        """Test that missing total_debt returns None"""
        results = {
            "free_cash_flow_to_firm": {2023: 500000000},
            "total_debt": {},  # Empty
        }
        output = calculate(results)
        
        # total_debt 缺失时视为 0，导致除以零返回 None
        assert output[2023] is None

    def test_fcf_different_from_debt_years(self):
        """Test when FCF and debt have different years"""
        results = {
            "free_cash_flow_to_firm": {2021: 300000000, 2022: 400000000},
            "total_debt": {2022: 800000000, 2023: 1000000000},
        }
        output = calculate(results)
        
        # 2022: 400M/800M = 0.5
        assert output[2022] == pytest.approx(0.5, rel=1e-9)
        # 2021: 只有 FCF，没有 debt -> debt 视为 0，返回 None
        assert output[2021] is None
        # 2023: 只有 debt，没有 FCF -> 不会出现在输出中（因为不在 fcf.keys() 中）
        assert 2023 not in output

    def test_output_field_constant(self):
        """Test OUTPUT_FIELD is defined"""
        assert OUTPUT_FIELD == "free_cash_flow_to_debt"

    def test_varying_ratio_over_years(self):
        """Test with varying values across years"""
        results = {
            "free_cash_flow_to_firm": {2023: 600000000, 2022: 300000000},
            "total_debt": {2023: 1200000000, 2022: 600000000},
        }
        output = calculate(results)
        
        # 2023: 600M/1200M = 0.5
        assert output[2023] == pytest.approx(0.5, rel=1e-9)
        # 2022: 300M/600M = 0.5
        assert output[2022] == pytest.approx(0.5, rel=1e-9)
