"""Dynamic Calculator Loader

使用 importlib + 隔离命名空间动态加载 calculator 脚本，
加载后清理 sys.modules 避免污染 Python 内置命名空间。
"""
import hashlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any, Callable


class CalculatorValidationError(ValueError):
    """Calculator 脚本验证失败"""

    pass


def load_calculator(path: str, validate: bool = True) -> dict[str, Any]:
    """加载单个 calculator 脚本

    Args:
        path: calculator 脚本路径
        validate: 是否验证规范（默认 True）

    Returns:
        dict: {
            "name": str,           # 指标名称
            "required_fields": set,  # 依赖字段
            "calculate": callable, # 计算函数
            "_source": str,        # 来源路径
        }

    Raises:
        CalculatorValidationError: 脚本格式错误
    """
    # 生成隔离的模块名（hash-based 避免冲突）
    module_name = f"dynamic_calc_{hashlib.md5(path.encode()).hexdigest()}"

    try:
        # 加载模块到隔离命名空间
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise CalculatorValidationError(f"Cannot load module from '{path}'")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 推断 name
        name = getattr(module, "name", None)
        if name is None:
            filename = Path(path).stem
            if filename.startswith("calc_"):
                name = filename[5:]
            else:
                raise CalculatorValidationError(
                    f"Cannot infer name from '{path}'. "
                    f"Name file as 'calc_xxx.py' or specify 'name' in script."
                )

        # 验证 required_fields
        if not hasattr(module, "required_fields"):
            raise CalculatorValidationError(
                f"Missing 'required_fields' in {path}"
            )
        required_fields = set(module.required_fields)

        # 验证 calculate
        if not callable(getattr(module, "calculate", None)):
            raise CalculatorValidationError(
                f"Missing or non-callable 'calculate' in {path}"
            )

        # 详细校验
        if validate:
            _validate_calculator(name, required_fields, module.calculate, path)

        return {
            "name": name,
            "required_fields": required_fields,
            "calculate": module.calculate,
            "_source": path,
        }
    finally:
        # 清理 sys.modules，避免污染 Python 命名空间
        if module_name in sys.modules:
            del sys.modules[module_name]


def _validate_calculator(
    name: str,
    required_fields: set,
    calculate: Callable[..., Any],
    source: str,
) -> None:
    """详细校验 calculator 规范

    Args:
        name: 指标名称
        required_fields: 依赖字段
        calculate: 计算函数
        source: 来源路径

    Raises:
        CalculatorValidationError: 校验失败
    """
    # 1. name 必须是 str
    if not isinstance(name, str):
        raise CalculatorValidationError(
            f"'{source}': name must be str, got {type(name).__name__}"
        )

    # 2. name 必须是有效的标识符
    if not name.isidentifier():
        raise CalculatorValidationError(
            f"'{source}': name '{name}' must be valid Python identifier "
            f"(字母、数字、下划线，不能以数字开头)"
        )

    # 3. required_fields 必须是 list 或 set
    if not isinstance(required_fields, (list, set)):
        raise CalculatorValidationError(
            f"'{source}': required_fields must be list or set, "
            f"got {type(required_fields).__name__}"
        )

    # 4. required_fields 元素必须是 str
    for field in required_fields:
        if not isinstance(field, str):
            raise CalculatorValidationError(
                f"'{source}': required_fields elements must be str, "
                f"got {type(field).__name__}: '{field}'"
            )

    # 5. calculate 必须是 callable
    if not callable(calculate):
        raise CalculatorValidationError(
            f"'{source}': calculate must be callable"
        )

    # 6. calculate 必须接受至少 1 个参数 (results)
    sig = inspect.signature(calculate)
    params = list(sig.parameters.keys())
    if len(params) < 1:
        raise CalculatorValidationError(
            f"'{source}': calculate must accept 'results' parameter"
        )


def load_calculators_from_dir(dir_path: str, validate: bool = True) -> list[dict[str, Any]]:
    """扫描目录加载所有 calc_*.py 文件

    Args:
        dir_path: 目录路径
        validate: 是否验证规范（默认 True）

    Returns:
        list[dict]: calculator 列表
    """
    calculators = []
    for py_file in Path(dir_path).glob("calc_*.py"):
        try:
            calc = load_calculator(str(py_file), validate=validate)
            calculators.append(calc)
        except CalculatorValidationError as e:
            print(f"⚠️  Failed to load {py_file}: {e}")
    return calculators
