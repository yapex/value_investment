"""Calculator Plugin - 动态计算器加载插件

使用方式:
    from value_investment.calculator_plugin import (
        registry,
        load_calculator,
        get_calculators,
    )

Calculator 格式:
    required_fields = ["field_a", "field_b"]
    def calculate(results, config=None): ...

加载来源:
    1. {cwd}/calculators/ - 用户 calculators
    2. 项目 calculators/ - 项目内置 calculators
    3. 包内 calculators/ - 包内置 calculators
"""
import hashlib
import importlib.util
import importlib.resources
import inspect
import sys
from pathlib import Path
from typing import Any
from collections.abc import Callable

# ============================================================================
# 核心：动态加载器
# ============================================================================


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
    """详细校验 calculator 规范"""
    # 1. name 必须是 str
    if not isinstance(name, str):
        raise CalculatorValidationError(
            f"'{source}': name must be str, got {type(name).__name__}"
        )

    # 2. name 必须是有效的标识符
    if not name.isidentifier():
        raise CalculatorValidationError(
            f"'{source}': name '{name}' must be valid Python identifier"
        )

    # 3. required_fields 必须是 list 或 set
    if not isinstance(required_fields, (list, set)):
        raise CalculatorValidationError(
            f"'{source}': required_fields must be list or set"
        )

    # 4. required_fields 元素必须是 str
    for field in required_fields:
        if not isinstance(field, str):
            raise CalculatorValidationError(
                f"'{source}': required_fields elements must be str"
            )

    # 5. calculate 必须是 callable
    if not callable(calculate):
        raise CalculatorValidationError(f"'{source}': calculate must be callable")

    # 6. calculate 必须接受至少 1 个参数
    sig = inspect.signature(calculate)
    if len(sig.parameters) < 1:
        raise CalculatorValidationError(
            f"'{source}': calculate must accept 'results' parameter"
        )


def load_calculators_from_dir(dir_path: str, validate: bool = True) -> list[dict[str, Any]]:
    """扫描目录加载所有 calc_*.py 文件"""
    calculators = []
    for py_file in Path(dir_path).glob("calc_*.py"):
        try:
            calc = load_calculator(str(py_file), validate=validate)
            calculators.append(calc)
        except CalculatorValidationError as e:
            print(f"⚠️  Failed to load {py_file}: {e}")
    return calculators


# ============================================================================
# 核心：注册表
# ============================================================================


class CalculatorAdapter:
    """Calculator 适配器

    错误处理策略:
    - 捕获所有 Exception，返回 None（而不是抛异常）
    - 计算器出错不影响其他计算器，保证整体流程不中断
    - Calculator 作者无需处理异常，框架统一兜底
    """

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

    def calculate(self, results) -> dict[int, float | None] | None:
        """执行计算，捕获所有错误，返回 None"""
        try:
            return self._calculate(results)
        except Exception as e:
            # 框架兜底：任何计算错误都返回 None，不中断整个计算流程
            import warnings
            warnings.warn(f"[Calculator '{self.name}'] 计算错误: {e}", RuntimeWarning)
            return None


class CalculatorRegistry:
    """Calculator 注册表"""

    def __init__(self):
        self._calculators: dict[str, CalculatorAdapter] = {}

    def register(
        self,
        name: str,
        required_fields: set,
        calculate: Callable[..., Any],
        _source: str | None = None,
    ) -> None:
        """注册 calculator（覆盖已存在的同名 calculator）"""
        self._calculators[name] = CalculatorAdapter(
            name=name,
            required_fields=required_fields,
            calculate=calculate,
            _source=_source,
        )

    def register_from_dict(self, calc_dict: dict) -> None:
        """从字典注册 calculator"""
        self.register(
            name=calc_dict["name"],
            required_fields=calc_dict["required_fields"],
            calculate=calc_dict["calculate"],
            _source=calc_dict.get("_source"),
        )

    def get_all(self) -> list:
        """获取所有 calculators"""
        return list(self._calculators.values())

    def get_by_name(self, name: str):
        """按名称获取 calculator"""
        return self._calculators.get(name)


# 全局注册表
registry = CalculatorRegistry()


def get_calculators() -> list:
    """获取所有 calculators"""
    return registry.get_all()


def clear_registry() -> None:
    """清空注册表（用于测试）"""
    registry._calculators.clear()


# ============================================================================
# 内置 calculators 加载
# ============================================================================


def _load_calcs_from_fs(
    calculators_dir: Path,
    load_func,
    register_func,
) -> None:
    """从文件系统加载 calculators"""
    for py_file in calculators_dir.glob("calc_*.py"):
        try:
            calc_dict = load_func(str(py_file))
            register_func(
                name=calc_dict["name"],
                required_fields=calc_dict["required_fields"],
                calculate=calc_dict["calculate"],
                _source=calc_dict.get("_source"),
            )
        except CalculatorValidationError as e:
            print(f"⚠️  Failed to load {py_file}: {e}")


def _load_calcs_from_package(
    package_name: str,
    load_func,
    register_func,
) -> bool:
    """从包资源加载 calculators（打包状态）"""
    try:
        for py_file in importlib.resources.files(package_name).iterdir():
            if not py_file.name.endswith(".py") or not py_file.name.startswith("calc_"):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                import tempfile

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False, prefix="calc_"
                ) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name

                try:
                    calc_dict = load_func(tmp_path, validate=False)
                    # 显式设置 name 和 source
                    file_name = py_file.name
                    file_stem = file_name[:-3] if file_name.endswith(".py") else file_name
                    calc_dict["name"] = (
                        file_stem[5:] if file_stem.startswith("calc_") else file_stem
                    )
                    calc_dict["_source"] = f"package://{file_name}"
                    register_func(
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


def _get_project_root() -> Path | None:
    """获取项目根目录"""
    # 从 calculator_plugin.py 向上找
    # src/value_investment/calculator_plugin.py -> src/value_investment/ -> src/ -> 项目根目录
    plugin_path = Path(__file__).resolve()
    # 检查是否是包内安装
    if "site-packages" in str(plugin_path) or ".venv" in str(plugin_path):
        return None
    # 计算项目根目录：src/value_investment -> src -> 项目根目录
    # parent = src/value_investment, parent.parent = src, parent.parent.parent = 项目根目录
    return plugin_path.parent.parent.parent


def load_builtin_calculators() -> None:
    """加载内置 calculators

    加载顺序（后者覆盖前者）:
    1. 包内 calculators/ (package://value_investment.calculators/)
    2. 项目 calculators/ (项目根目录/calculators/) [兼容旧位置]
    3. 用户 calculators/ ({cwd}/calculators/) [兼容旧位置]
    """
    # 1. 包内 calculators
    _load_calcs_from_package("value_investment.calculators", load_calculator, registry.register)

    # 2. 项目 calculators/ (旧位置，兼容)
    project_root = _get_project_root()
    if project_root:
        project_calcs_dir = project_root / "calculators"
        if project_calcs_dir.is_dir():
            _load_calcs_from_fs(project_calcs_dir, load_calculator, registry.register)

    # 3. 用户 calculators/ (旧位置，兼容)
    cwd_calcs_dir = Path.cwd() / "calculators"
    if cwd_calcs_dir.is_dir():
        for py_file in cwd_calcs_dir.glob("calc_*.py"):
            try:
                calc_dict = load_calculator(str(py_file))
                registry.register(
                    name=calc_dict["name"],
                    required_fields=calc_dict["required_fields"],
                    calculate=calc_dict["calculate"],
                    _source=calc_dict.get("_source"),
                )
                print(f"✓ Loaded user calculator: {calc_dict['name']} from {py_file}")
            except CalculatorValidationError as e:
                print(f"⚠️  Failed to load {py_file}: {e}")


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "CalculatorValidationError",
    "CalculatorAdapter",
    "CalculatorRegistry",
    "registry",
    "load_calculator",
    "load_calculators_from_dir",
    "get_calculators",
    "clear_registry",
    "load_builtin_calculators",
]

# ============================================================================
# 自动加载内置 calculators
# ============================================================================

# 加载内置 calculators
load_builtin_calculators()
