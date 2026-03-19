"""Tests for Pipeline dependency validation

These tests ensure all Calculator dependencies can be satisfied by Handlers.
Run automatically with: pytest tests/pipeline/
"""
import pytest
from value_investment.pipeline.validator import (
    validate_calculators,
    get_validation_summary,
    assert_all_calculators_valid,
)


class TestPipelineValidator:
    """Pipeline dependency validation tests"""

    def test_all_calculators_have_valid_dependencies(self):
        """所有 Calculator 的依赖字段都必须有 Handler 支持

        这是核心集成测试，确保依赖链完整性。
        如果失败，说明有 Calculator 依赖了无法获取的字段。
        """
        # 这个测试会抛出 AssertionError 如果有缺失
        assert_all_calculators_valid()

    def test_validation_returns_results(self):
        """验证函数返回所有 Calculator 的结果"""
        results = validate_calculators()

        # 应该有多个 Calculator
        assert len(results) > 0

        # 每个结果都应该有必要的字段
        for r in results:
            assert r.calculator
            assert r.status in ("OK", "MISSING_DEPS")
            assert isinstance(r.details, list)

    def test_validation_summary_format(self):
        """验证报告格式正确"""
        results = validate_calculators()
        summary = get_validation_summary(results)

        # 报告应该包含关键信息
        assert "Pipeline Calculator Dependency Validation" in summary
        assert "Total:" in summary
        assert "=" in summary

    def test_known_calculators_are_valid(self):
        """验证已知的 Calculator 都应该通过"""
        results = validate_calculators()

        # 这些是我们已经实现的 Calculator
        known_calculators = {
            "gross_profit",
            "inventory_turnover",
            "implied_growth",
        }

        # 找到已知的 Calculator
        found = {r.calculator for r in results if r.calculator in known_calculators}

        # 应该都找到了
        assert found == known_calculators, f"Missing: {known_calculators - found}"

        # 都应该通过验证
        for r in results:
            if r.calculator in known_calculators:
                assert r.status == "OK", f"{r.calculator} should be OK but got {r.status}"
