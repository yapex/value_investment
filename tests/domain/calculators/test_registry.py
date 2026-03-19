"""Tests for Calculator Registry"""
import pytest

from value_investment.domain.calculators.registry import (
    CalculatorRegistry,
    DynamicCalculatorAdapter,
)


class TestDynamicCalculatorAdapter:
    """测试 DynamicCalculatorAdapter"""

    def test_adapter_implements_calculator_interface(self):
        """测试适配器实现 Calculator 接口"""
        # Given
        def mock_calculate(results):
            return {"2023": 100}

        adapter = DynamicCalculatorAdapter(
            name="test",
            required_fields={"revenue"},
            calculate=mock_calculate,
        )

        # Then
        assert adapter.name == "test"
        assert adapter.required_fields == {"revenue"}
        assert callable(adapter.calculate)

    def test_adapter_calculate_delegates_to_function(self):
        """测试 calculate 委托给原始函数"""
        # Given
        def mock_calculate(results):
            return {"2023": float(results["revenue"]["2023"]) * 0.1}

        adapter = DynamicCalculatorAdapter(
            name="test",
            required_fields={"revenue"},
            calculate=mock_calculate,
        )

        results: dict[str, dict[str, float]] = {"revenue": {"2023": 1000.0}}

        # When
        output = adapter.calculate(results)

        # Then
        assert output == {"2023": 100.0}


class TestCalculatorRegistry:
    """测试 CalculatorRegistry"""

    def test_register_dynamic_calculator(self):
        """测试注册动态 calculator"""
        # Given
        def custom_calculate(results):
            return {"2023": 42}

        registry = CalculatorRegistry()

        # When
        registry.register_dynamic(
            name="custom",
            required_fields={"revenue"},
            calculate=custom_calculate,
        )

        # Then
        calculators = registry.get_all()
        custom = next(c for c in calculators if c.name == "custom")
        assert custom.calculate({}) == {"2023": 42}

    def test_dynamic_overrides_builtin(self):
        """测试动态 calculator 覆盖内置同名"""
        # Given
        def custom_calculate(results):
            return {"2023": 999}  # 自定义返回值

        registry = CalculatorRegistry()

        # 注册动态 calculator（与内置同名）
        registry.register_dynamic(
            name="gross_profit",
            required_fields={"revenue"},
            calculate=custom_calculate,
        )

        # When
        calculators = registry.get_all()

        # Then
        gross_profit = next(c for c in calculators if c.name == "gross_profit")
        assert gross_profit.calculate({}) == {"2023": 999}

    def test_get_by_name(self):
        """测试按名称获取 calculator"""
        # Given
        registry = CalculatorRegistry()
        registry.register_dynamic(
            name="test_calc",
            required_fields=set(),
            calculate=lambda r: {},
        )

        # When
        calc = registry.get_by_name("test_calc")

        # Then
        assert calc is not None
        assert calc.name == "test_calc"

    def test_get_by_name_not_found(self):
        """测试按名称获取不存在的 calculator"""
        # Given
        registry = CalculatorRegistry()

        # When
        calc = registry.get_by_name("nonexistent")

        # Then
        assert calc is None

    def test_register_dynamic_from_dict(self):
        """测试从字典注册动态 calculator"""
        # Given
        registry = CalculatorRegistry()
        calc_dict = {
            "name": "from_dict",
            "required_fields": {"revenue"},
            "calculate": lambda r: {"2023": 100},
            "_source": "/path/to/script.py",
        }

        # When
        registry.register_dynamic_from_dict(calc_dict)

        # Then
        calc = registry.get_by_name("from_dict")
        assert calc is not None
        assert calc._source == "/path/to/script.py"
