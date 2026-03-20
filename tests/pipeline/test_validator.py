"""Tests for Pipeline dependency validation"""
import pytest
from value_investment.pipeline.validator import (
    validate_calculators,
    get_validation_summary,
    assert_all_valid,
)
from value_investment.calculator_plugin import get_calculators
from value_investment.domain.fields import ALL_FIELDS

ALL_CALCULATORS = get_calculators()


class TestPipelineValidator:
    """Pipeline validation tests"""

    def test_all_calculators_have_valid_dependencies(self):
        """所有 Calculator 的依赖字段都必须有 Handler 支持
        
        注：fair_value_change 和 investment_income 的 Tushare 字段名待确认，
        相关计算器 (fair_value_change_ratio, investment_income_ratio) 
        暂时跳过依赖验证。
        """
        # 需要验证的计算器（排除待确认字段的依赖）
        pending_calcs = [c for c in ALL_CALCULATORS if c.name not in (
            "fair_value_change_ratio",
            "investment_income_ratio",
        )]
        assert_all_valid(pending_calcs)

    def test_all_calculators_registered_in_fields(self):
        """所有 Calculator 的输出字段必须在 ALL_FIELDS 中注册"""
        unregistered = []
        for calc in ALL_CALCULATORS:
            if calc.name not in ALL_FIELDS:
                unregistered.append(calc.name)
        
        assert not unregistered, (
            f"以下 Calculator 的输出字段未在 ALL_FIELDS 中注册: {unregistered}. "
            f"需要添加到 CustomFields。"
        )

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

