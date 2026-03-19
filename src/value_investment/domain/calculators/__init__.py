"""Calculators for derived fields

统一使用函数式格式:
    required_fields = ["field_a", "field_b"]
    def calculate(results, config=None): ...
"""
from value_investment.domain.calculators.registry import (
    CalculatorRegistry,
    DynamicCalculatorAdapter,
    get_registry,
    register_dynamic_calculator,
    get_calculators,
    clear_registry,
    load_builtin_calculators_from_dir,
)


def _validate_fields(calc) -> None:
    """Validate calculator's required_fields are valid"""
    from value_investment.domain.fields import ALL_FIELDS

    invalid = set(calc.required_fields) - ALL_FIELDS
    if invalid:
        raise ValueError(f"Calculator '{calc.name}' has invalid fields: {invalid}")


# 加载内置 calculators
load_builtin_calculators_from_dir()

# 获取所有 calculators
ALL_CALCULATORS = get_calculators()

# 验证字段
for calc in ALL_CALCULATORS:
    _validate_fields(calc)

# 构建 name -> calculator map
CALCULATOR_MAP = {calc.name: calc for calc in ALL_CALCULATORS}

__all__ = [
    "ALL_CALCULATORS",
    "CALCULATOR_MAP",
    "CalculatorRegistry",
    "DynamicCalculatorAdapter",
    "get_registry",
    "register_dynamic_calculator",
    "get_calculators",
    "clear_registry",
    "load_builtin_calculators_from_dir",
]
