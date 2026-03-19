"""Calculator registry

统一使用函数式格式:
    required_fields = ["field_a", "field_b"]
    def calculate(results, config=None): ...
"""
from pathlib import Path
from typing import Any, Callable

# Global registry for builtin calculators
_builtin_calculators: list = []


def register_functional(
    name: str,
    required_fields: set,
    calculate: Callable[..., Any],
    _source: str | None = None,
) -> None:
    """注册函数式 calculator

    Args:
        name: 指标名称
        required_fields: 依赖字段集合
        calculate: 计算函数
        _source: 来源路径
    """
    adapter = DynamicCalculatorAdapter(
        name=name,
        required_fields=required_fields,
        calculate=calculate,
        _source=_source,
    )
    _builtin_calculators.append(adapter)


class DynamicCalculatorAdapter:
    """Calculator 适配器"""

    def __init__(
        self,
        name: str,
        required_fields: set,
        calculate: Callable[..., Any],
        _source: str | None = None,
    ):
        self.name = name
        self.required_fields = required_fields
        self._calculate = calculate
        self._source = _source

    def calculate(self, results) -> dict:
        return self._calculate(results)


class CalculatorRegistry:
    """Calculator 注册表"""

    def __init__(self):
        self._dynamic_cache: list = []

    def register_dynamic(
        self,
        name: str,
        required_fields: set,
        calculate: Callable[..., Any],
        _source: str | None = None,
    ) -> None:
        """注册动态 calculator"""
        self._dynamic_cache = [c for c in self._dynamic_cache if c.name != name]

        adapter = DynamicCalculatorAdapter(
            name=name,
            required_fields=required_fields,
            calculate=calculate,
            _source=_source,
        )
        self._dynamic_cache.append(adapter)

    def register_dynamic_from_dict(self, calc_dict: dict) -> None:
        """从字典注册动态 calculator"""
        self.register_dynamic(
            name=calc_dict["name"],
            required_fields=calc_dict["required_fields"],
            calculate=calc_dict["calculate"],
            _source=calc_dict.get("_source"),
        )

    def get_all(self) -> list:
        """获取所有 calculator（动态优先于内置）"""
        calculators = {}

        # 1. 内置
        for calc in _builtin_calculators:
            calculators[calc.name] = calc

        # 2. 动态覆盖
        for calc in self._dynamic_cache:
            calculators[calc.name] = calc

        return list(calculators.values())

    def get_by_name(self, name: str):
        """按名称获取 calculator"""
        for calc in self.get_all():
            if calc.name == name:
                return calc
        return None


# 全局 registry
_global_registry = CalculatorRegistry()


def get_registry() -> CalculatorRegistry:
    return _global_registry


def register_dynamic_calculator(
    name: str,
    required_fields: set,
    calculate: Callable[..., Any],
    _source: str | None = None,
) -> None:
    """注册动态 calculator 到全局 registry"""
    _global_registry.register_dynamic(
        name=name,
        required_fields=required_fields,
        calculate=calculate,
        _source=_source,
    )


def get_calculators() -> list:
    """获取所有 calculator"""
    return _global_registry.get_all()


def clear_registry() -> None:
    """清空 registry（用于测试）"""
    _builtin_calculators.clear()
    _global_registry._dynamic_cache.clear()


def load_builtin_calculators_from_dir(dir_path: str | None = None) -> None:
    """从目录加载内置 calculators

    支持两种模式:
    1. 打包状态 (wheel/zipapp): 使用 importlib.resources
    2. 开发/源码状态: 使用文件系统路径

    Args:
        dir_path: 目录路径，默认使用当前模块目录
    """
    from value_investment.domain.calculators.dynamic_loader import (
        CalculatorValidationError,
        load_calculator,
    )

    if dir_path is not None:
        # 外部指定路径，直接使用文件系统
        calculators_dir = Path(dir_path)
        _load_calcs_from_fs(calculators_dir, load_calculator, register_functional)
    else:
        # 尝试用 importlib.resources（支持打包状态）
        if not _load_calcs_from_package(load_calculator, register_functional):
            # 回退到文件系统（开发模式）
            calculators_dir = Path(__file__).parent
            _load_calcs_from_fs(calculators_dir, load_calculator, register_functional)


def _load_calcs_from_package(
    load_calculator_fn,
    register_fn,
) -> bool:
    """从包资源加载 calculators（打包状态）

    Returns:
        True if loaded successfully, False if not available
    """
    import sys

    from value_investment.domain.calculators.dynamic_loader import CalculatorValidationError

    # Python 3.9+ 使用 importlib.resources
    if sys.version_info >= (3, 9):
        from importlib.resources import files

        try:
            # 获取当前包的 resources
            from value_investment.domain import calculators as pkg

            for py_file in files(pkg).iterdir():
                # 只处理 calc_*.py 文件
                if not py_file.name.endswith(".py") or not py_file.name.startswith("calc_"):
                    continue

                try:
                    # 读取文件内容
                    content = py_file.read_text(encoding="utf-8")

                    # 写入临时文件后加载（因为 load_calculator 需要文件路径）
                    import tempfile

                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".py", delete=False, prefix="calc_"
                    ) as tmp:
                        tmp.write(content)
                        tmp_path = tmp.name

                    try:
                        calc_dict = load_calculator_fn(tmp_path, validate=False)
                        # 显式设置 name 和 source（临时文件无法推断正确的 name）
                        calc_dict["name"] = py_file.stem[5:] if py_file.stem.startswith("calc_") else py_file.stem
                        calc_dict["_source"] = f"package://{py_file.name}"
                        register_fn(
                            name=calc_dict["name"],
                            required_fields=calc_dict["required_fields"],
                            calculate=calc_dict["calculate"],
                            _source=calc_dict["_source"],
                        )
                    finally:
                        Path(tmp_path).unlink()
                except CalculatorValidationError as e:
                    print(f"⚠️  Failed to load {py_file.name}: {e}")

            return True
        except Exception:
            return False
    else:
        return False


def _load_calcs_from_fs(
    calculators_dir: Path,
    load_calculator_fn,
    register_fn,
) -> None:
    """从文件系统加载 calculators"""
    from value_investment.domain.calculators.dynamic_loader import CalculatorValidationError

    for py_file in calculators_dir.glob("calc_*.py"):
        try:
            calc_dict = load_calculator_fn(str(py_file))
            register_fn(
                name=calc_dict["name"],
                required_fields=calc_dict["required_fields"],
                calculate=calc_dict["calculate"],
                _source=calc_dict.get("_source"),
            )
        except CalculatorValidationError as e:
            print(f"⚠️  Failed to load {py_file}: {e}")


def load_user_calculators_from_cwd() -> None:
    """从当前执行目录的 calculators/ 子目录加载用户 calculators

    如果存在 {cwd}/calculators/ 目录，自动加载其中的 calc_*.py 文件。
    这些 calculators 会覆盖内置 calculators（同 name）。
    """
    import os

    from value_investment.domain.calculators.dynamic_loader import (
        CalculatorValidationError,
        load_calculator,
    )

    cwd_calculators_dir = Path.cwd() / "calculators"

    if cwd_calculators_dir.is_dir():
        for py_file in cwd_calculators_dir.glob("calc_*.py"):
            try:
                calc_dict = load_calculator(str(py_file))
                # 用户 calculators 注册到 _global_registry，覆盖内置
                _global_registry.register_dynamic(
                    name=calc_dict["name"],
                    required_fields=calc_dict["required_fields"],
                    calculate=calc_dict["calculate"],
                    _source=calc_dict.get("_source"),
                )
                print(f"✓ Loaded user calculator: {calc_dict['name']} from {py_file}")
            except CalculatorValidationError as e:
                print(f"⚠️  Failed to load {py_file}: {e}")
