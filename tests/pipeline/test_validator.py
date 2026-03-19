"""Tests for Pipeline dependency validation"""
import pytest
from value_investment.pipeline.validator import (
    validate_calculators,
    get_validation_summary,
    assert_all_valid,
)
from value_investment.pipeline.calculators import ALL_CALCULATORS


class TestPipelineValidator:
    """Pipeline validation tests"""

    def test_all_calculators_have_valid_dependencies(self):
        """所有 Calculator 的依赖字段都必须有 Handler 支持"""
        assert_all_valid(ALL_CALCULATORS)

    def test_validation_returns_results(self):
        """验证函数返回所有 Calculator 的结果"""
        results = validate_calculators(ALL_CALCULATORS)
        assert len(results) > 0
        
        for r in results:
            assert r.calculator
            assert r.status in ("OK", "MISSING_DEPS")
            assert isinstance(r.details, list)

    def test_validation_summary_format(self):
        """验证报告格式正确"""
        results = validate_calculators(ALL_CALCULATORS)
        summary = get_validation_summary(results)
        
        assert "Pipeline Calculator Validation" in summary
        assert "Total:" in summary

    def test_known_calculators_are_valid(self):
        """验证已知的 Calculator 都应该通过"""
        results = validate_calculators(ALL_CALCULATORS)
        
        known = {"gross_profit", "inventory_turnover", "implied_growth"}
        found = {r.calculator for r in results if r.calculator in known}
        
        assert found == known
        
        for r in results:
            if r.calculator in known:
                assert r.status == "OK"

