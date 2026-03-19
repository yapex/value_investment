# 动态 Calculator 加载实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现动态 calculator 加载机制，支持 skill 生成 Python 脚本并通过 CLI 动态注册为 calculator。

**Architecture:** 使用 `importlib` + 隔离命名空间动态加载 Python 脚本，提取函数式 calculator（name, required_fields, calculate）并注册到 registry，动态 calculator 优先级高于内置。

**Tech Stack:** Python importlib, pytest

---

## Task 1: 创建 DynamicCalculatorLoader

**Files:**
- Create: `src/value_investment/domain/calculators/dynamic_loader.py`
- Test: `tests/domain/calculators/test_dynamic_loader.py`

### Step 1: 写测试文件

```bash
mkdir -p tests/domain/calculators
```

创建 `tests/domain/calculators/test_dynamic_loader.py`:

```python
"""Tests for DynamicCalculatorLoader"""
import tempfile
from pathlib import Path
from value_investment.domain.calculators.dynamic_loader import (
    load_calculator,
    load_calculators_from_dir,
    CalculatorValidationError,
)


class TestLoadCalculator:
    """测试 load_calculator 函数"""

    def test_load_valid_calculator(self):
        """测试加载有效的 calculator 脚本"""
        # Given
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("""
name = "roic"
required_fields = ["net_income", "total_equity"]

def calculate(results):
    income = results["net_income"]
    equity = results["total_equity"]
    return {y: income[y] / equity[y] for y in income}
""")
            path = f.name

        try:
            # When
            result = load_calculator(path)

            # Then
            assert result["name"] == "roic"
            assert result["required_fields"] == {"net_income", "total_equity"}
            assert callable(result["calculate"])
            assert result["_source"] == path
        finally:
            Path(path).unlink()

    def test_infer_name_from_filename(self):
        """测试 name 从文件名推断"""
        # Given
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, prefix="calc_"
        ) as f:
            f.write("""
required_fields = ["net_income"]

def calculate(results):
    return {}
""")
            path = f.name

        try:
            # When
            result = load_calculator(path)

            # Then
            assert result["name"] == Path(path).stem[5:]  # 去掉 calc_ 前缀
        finally:
            Path(path).unlink()

    def test_explicit_name_override_filename(self):
        """测试显式 name 覆盖文件名推断"""
        # Given
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, prefix="calc_my_roic"
        ) as f:
            f.write("""
name = "roic"  # 覆盖默认的 my_roic
required_fields = ["net_income"]

def calculate(results):
    return {}
""")
            path = f.name

        try:
            # When
            result = load_calculator(path)

            # Then
            assert result["name"] == "roic"
        finally:
            Path(path).unlink()

    def test_missing_required_fields_raises(self):
        """测试缺少 required_fields 报错"""
        # Given
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("""
def calculate(results):
    return {}
""")
            path = f.name

        try:
            # When/Then
            with pytest.raises(CalculatorValidationError) as exc_info:
                load_calculator(path)
            assert "required_fields" in str(exc_info.value)
        finally:
            Path(path).unlink()

    def test_missing_calculate_raises(self):
        """测试缺少 calculate 函数报错"""
        # Given
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("""
required_fields = ["net_income"]
""")
            path = f.name

        try:
            # When/Then
            with pytest.raises(CalculatorValidationError) as exc_info:
                load_calculator(path)
            assert "calculate" in str(exc_info.value)
        finally:
            Path(path).unlink()


class TestLoadCalculatorsFromDir:
    """测试 load_calculators_from_dir 函数"""

    def test_load_only_calc_prefix_files(self):
        """测试只加载 calc_*.py 文件"""
        # Given
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建 calc_roic.py
            (Path(tmpdir) / "calc_roic.py").write_text("""
name = "roic"
required_fields = []
def calculate(results): return {}
""")
            # 创建 calc_pe.py
            (Path(tmpdir) / "calc_pe.py").write_text("""
name = "pe"
required_fields = []
def calculate(results): return {}
""")
            # 创建 other.py（不应被加载）
            (Path(tmpdir) / "other.py").write_text("""
name = "other"
required_fields = []
def calculate(results): return {}
""")

            # When
            calculators = load_calculators_from_dir(tmpdir)

            # Then
            assert len(calculators) == 2
            names = {c["name"] for c in calculators}
            assert names == {"roic", "pe"}

    def test_invalid_file_prints_warning(self):
        """测试无效文件打印警告但不中断"""
        # Given
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "calc_valid.py").write_text("""
name = "valid"
required_fields = []
def calculate(results): return {}
""")
            (Path(tmpdir) / "calc_invalid.py").write_text("""
# 缺少 required_fields 和 calculate
""")

            # When
            calculators = load_calculators_from_dir(tmpdir)

            # Then
            assert len(calculators) == 1
            assert calculators[0]["name"] == "valid"
```

### Step 2: 运行测试确认失败

Run: `pytest tests/domain/calculators/test_dynamic_loader.py -v`
Expected: FAIL - module not found

### Step 3: 实现 minimal loader

创建 `src/value_investment/domain/calculators/dynamic_loader.py`:

```python
"""Dynamic Calculator Loader

使用 importlib + 隔离命名空间动态加载 calculator 脚本。
"""
import importlib.util
import hashlib
from pathlib import Path
from typing import Any


class CalculatorValidationError(ValueError):
    """Calculator 脚本验证失败"""
    pass


def load_calculator(path: str) -> dict[str, Any]:
    """加载单个 calculator 脚本

    Args:
        path: calculator 脚本路径

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
    # 生成隔离的模块名
    module_name = f"dynamic_calc_{hashlib.md5(path.encode()).hexdigest()}"

    # 加载模块到隔离命名空间
    spec = importlib.util.spec_from_file_location(module_name, path)
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

    return {
        "name": name,
        "required_fields": required_fields,
        "calculate": module.calculate,
        "_source": path,
    }


def load_calculators_from_dir(dir_path: str) -> list[dict[str, Any]]:
    """扫描目录加载所有 calc_*.py 文件

    Args:
        dir_path: 目录路径

    Returns:
        list[dict]: calculator 列表
    """
    calculators = []
    for py_file in Path(dir_path).glob("calc_*.py"):
        try:
            calc = load_calculator(str(py_file))
            calculators.append(calc)
        except CalculatorValidationError as e:
            print(f"⚠️  Failed to load {py_file}: {e}")
    return calculators
```

### Step 4: 运行测试确认通过

Run: `pytest tests/domain/calculators/test_dynamic_loader.py -v`
Expected: PASS

### Step 5: 提交

```bash
git add src/value_investment/domain/calculators/dynamic_loader.py tests/domain/calculators/test_dynamic_loader.py
git commit -m "feat: add DynamicCalculatorLoader for dynamic calculator loading"
```

---

## Task 2: 改造 Registry 支持动态 Calculator

**Files:**
- Modify: `src/value_investment/domain/calculators/registry.py`
- Test: `tests/domain/calculators/test_registry.py`

### Step 1: 写测试

创建 `tests/domain/calculators/test_registry.py`:

```python
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
            return {"2023": results["revenue"]["2023"] * 0.1}

        adapter = DynamicCalculatorAdapter(
            name="test",
            required_fields={"revenue"},
            calculate=mock_calculate,
        )

        results = {"revenue": {"2023": 1000}}

        # When
        output = adapter.calculate(results)

        # Then
        assert output == {"2023": 100}


class TestCalculatorRegistry:
    """测试 CalculatorRegistry"""

    def test_dynamic_overrides_builtin(self):
        """测试动态 calculator 覆盖内置同名"""
        # Given
        def custom_calculate(results):
            return {"2023": 999}  # 自定义返回值

        registry = CalculatorRegistry()

        # 注册动态 calculator
        registry.register_dynamic(
            name="gross_profit",  # 与内置同名
            required_fields={"revenue"},
            calculate=custom_calculate,
        )

        # When
        calculators = registry.get_all()

        # Then
        gross_profit = next(c for c in calculators if c.name == "gross_profit")
        assert gross_profit.calculate({}) == {"2023": 999}
```

### Step 2: 运行测试确认失败

Run: `pytest tests/domain/calculators/test_registry.py -v`
Expected: FAIL

### Step 3: 改造 registry

修改 `src/value_investment/domain/calculators/registry.py`:

```python
"""Calculator registry and decorator

All calculators must be decorated with @calculator to be discovered.
This makes registration explicit and avoids implicit conventions.

Usage:
    from value_investment.domain.calculators import calculator

    @calculator
    class ROICCalculator:
        name = "roic"
        required_fields = {...}
        
        def calculate(self, results):
            return {...}
"""
from typing import Any


# Global registry for builtin calculators
_builtin_calculators: list = []

# Global registry for dynamic calculators
_dynamic_calculators: list = []


def calculator(cls):
    """Decorator to register a Calculator
    
    Must be used on all Calculator classes. Without this decorator,
    the class will NOT be discovered.
    
    Args:
        cls: Calculator class to register
        
    Returns:
        Same class (unchanged)
        
    Raises:
        ValueError: If class doesn't have required attributes
    """
    # Validate required attributes
    required_attrs = ["name", "required_fields", "calculate"]
    for attr in required_attrs:
        if not hasattr(cls, attr):
            raise ValueError(
                f"Calculator class '{cls.__name__}' is missing required attribute '{attr}'. "
                f"Calculator must have: {', '.join(required_attrs)}"
            )
    
    # Validate 'calculate' is callable
    if not callable(getattr(cls, "calculate", None)):
        raise ValueError(
            f"Calculator class '{cls.__name__}' has 'calculate' attribute but it's not callable"
        )
    
    # Register the class (not instance - instantiation happens later)
    _builtin_calculators.append(cls)
    
    return cls


class DynamicCalculatorAdapter:
    """动态 Calculator 适配器
    
    将函数式 calculator 转换为 Calculator 接口，
    便于与内置 calculator 统一处理。
    """
    
    def __init__(
        self,
        name: str,
        required_fields: set,
        calculate: callable,
        _source: str = None,
    ):
        self.name = name
        self.required_fields = required_fields
        self._calculate = calculate
        self._source = _source
    
    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, Any]:
        return self._calculate(results)


class CalculatorRegistry:
    """Calculator 注册表
    
    管理内置和动态 calculator，提供统一的访问接口。
    """
    
    def __init__(self):
        self._dynamic_cache: list = []
    
    def register_dynamic(
        self,
        name: str,
        required_fields: set,
        calculate: callable,
        _source: str = None,
    ) -> None:
        """注册动态 calculator
        
        Args:
            name: 指标名称
            required_fields: 依赖字段集合
            calculate: 计算函数
            _source: 来源路径（可选）
        """
        # 移除已存在的同名动态 calculator
        self._dynamic_cache = [
            c for c in self._dynamic_cache if c.name != name
        ]
        
        adapter = DynamicCalculatorAdapter(
            name=name,
            required_fields=required_fields,
            calculate=calculate,
            _source=_source,
        )
        self._dynamic_cache.append(adapter)
    
    def register_dynamic_from_dict(self, calc_dict: dict) -> None:
        """从字典注册动态 calculator
        
        Args:
            calc_dict: load_calculator 返回的字典
        """
        self.register_dynamic(
            name=calc_dict["name"],
            required_fields=calc_dict["required_fields"],
            calculate=calc_dict["calculate"],
            _source=calc_dict.get("_source"),
        )
    
    def get_all(self) -> list:
        """获取所有 calculator（动态优先于内置）
        
        Returns:
            list: 所有 calculator 实例
        """
        calculators = {}
        
        # 1. 先加载内置
        for cls in _builtin_calculators:
            try:
                calculators[cls.name] = cls()
            except Exception as e:
                print(f"⚠️  Failed to instantiate {cls.__name__}: {e}")
        
        # 2. 动态 calculator 覆盖内置
        for calc in self._dynamic_cache:
            calculators[calc.name] = calc
        
        return list(calculators.values())
    
    def get_by_name(self, name: str):
        """按名称获取 calculator
        
        Args:
            name: 指标名称
            
        Returns:
            Calculator or None
        """
        for calc in self.get_all():
            if calc.name == name:
                return calc
        return None


# 模块级全局 registry 实例
_global_registry = CalculatorRegistry()


def get_registry() -> CalculatorRegistry:
    """获取全局 registry 实例"""
    return _global_registry


def register_dynamic_calculator(
    name: str,
    required_fields: set,
    calculate: callable,
    _source: str = None,
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


def get_registered_builtin_calculators() -> list:
    """获取所有已注册的 builtin Calculator 类"""
    return list(_builtin_calculators)


def clear_registry() -> None:
    """清空 registry（用于测试）"""
    _builtin_calculators.clear()
    _dynamic_calculators.clear()
    _global_registry._dynamic_cache.clear()


def instantiate_calculators() -> list:
    """实例化所有注册的 builtin calculators"""
    instances = []
    for cls in _builtin_calculators:
        try:
            instances.append(cls())
        except Exception as e:
            print(f"⚠️  Failed to instantiate {cls.__name__}: {e}")
    return instances
```

### Step 4: 运行测试确认通过

Run: `pytest tests/domain/calculators/test_registry.py -v`
Expected: PASS

### Step 5: 提交

```bash
git add src/value_investment/domain/calculators/registry.py tests/domain/calculators/test_registry.py
git commit -m "refactor: enhance registry with dynamic calculator support"
```

---

## Task 3: CLI 添加动态 Calculator 参数

**Files:**
- Modify: `src/value_investment/cli.py`
- Test: `tests/test_cli.py`

### Step 1: 写测试

在 `tests/test_cli.py` 中添加：

```python
def test_cli_loads_dynamic_calculator(tmp_path):
    """测试 CLI 加载动态 calculator"""
    # Given: 创建临时 calculator 文件
    calc_file = tmp_path / "calc_custom.py"
    calc_file.write_text("""
required_fields = []

def calculate(results):
    return {"2023": 42}
""")

    # When: 运行 CLI（需要 mock 数据获取）
    result = subprocess.run(
        [
            "python", "-m", "value_investment.cli",
            "calc", "600519",
            "--calculator", str(calc_file),
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # Then: 检查输出包含自定义计算结果或正常执行
    # 注：这里需要 mock 数据源，简化测试只检查不报错
    assert "Traceback" not in result.stderr or result.returncode == 0
```

### Step 2: 修改 CLI

修改 `src/value_investment/cli.py`，添加 `--calculator` 和 `--calculator-dir` 参数：

```python
# 在适当位置添加导入
from value_investment.domain.calculators.dynamic_loader import (
    load_calculator,
    load_calculators_from_dir,
)
from value_investment.domain.calculators.registry import register_dynamic_calculator


# 在 calc 子命令中添加参数
@click.command()
@click.argument("symbol")
@click.option("--calculator", "-c", multiple=True, help="动态 calculator 脚本路径")
@click.option("--calculator-dir", "-d", multiple=True, help="动态 calculator 目录路径")
def calc(symbol, calculator, calculator_dir):
    """计算股票的财务指标"""
    
    # 注册动态 calculators
    for path in calculator:
        try:
            calc_dict = load_calculator(path)
            register_dynamic_calculator(**calc_dict)
        except Exception as e:
            click.echo(f"⚠️  加载 calculator 失败: {path}")
            click.echo(f"   {e}")
    
    for dir_path in calculator_dir:
        try:
            calculators = load_calculators_from_dir(dir_path)
            for calc_dict in calculators:
                register_dynamic_calculator(**calc_dict)
        except Exception as e:
            click.echo(f"⚠️  加载 calculator 目录失败: {dir_path}")
            click.echo(f"   {e}")
    
    # 后续逻辑保持不变...
```

### Step 3: 运行测试

Run: `pytest tests/test_cli.py -v`
Expected: PASS

### Step 4: 提交

```bash
git add src/value_investment/cli.py tests/test_cli.py
git commit -m "feat: add --calculator and --calculator-dir CLI options"
```

---

## Task 4: 端到端测试

**Files:**
- Create: `tests/e2e/test_dynamic_calculator_e2e.py`

### Step 1: 写端到端测试

```python
"""端到端测试：动态 Calculator 完整流程"""
import tempfile
from pathlib import Path
from value_investment.domain.calculators.dynamic_loader import load_calculator
from value_investment.domain.calculators.registry import get_registry, register_dynamic_calculator


class TestDynamicCalculatorE2E:
    """动态 Calculator 端到端测试"""

    def test_full_workflow(self):
        """完整工作流：生成脚本 -> 加载 -> 注册 -> 使用"""
        # Step 1: 模拟 skill 生成 calculator 脚本
        with tempfile.TemporaryDirectory() as tmpdir:
            calc_path = Path(tmpdir) / "calc_roic.py"
            calc_path.write_text("""
name = "roic"
required_fields = ["net_income", "total_equity"]

def calculate(results):
    income = results.get("net_income", {})
    equity = results.get("total_equity", {})
    return {y: income.get(y, 0) / equity.get(y, 1) for y in income}
""")

            # Step 2: 加载
            calc_dict = load_calculator(str(calc_path))
            assert calc_dict["name"] == "roic"
            assert calc_dict["required_fields"] == {"net_income", "total_equity"}

            # Step 3: 注册
            registry = get_registry()
            registry.register_dynamic_from_dict(calc_dict)

            # Step 4: 使用
            calculators = registry.get_all()
            roic = next((c for c in calculators if c.name == "roic"), None)
            assert roic is not None

            # 验证计算结果
            test_data = {
                "net_income": {"2023": 100},
                "total_equity": {"2023": 500},
            }
            result = roic.calculate(test_data)
            assert result["2023"] == pytest.approx(0.2)

    def test_override_builtin_with_dynamic(self):
        """测试动态 calculator 覆盖内置"""
        # Given: 创建覆盖 gross_profit 的动态 calculator
        with tempfile.TemporaryDirectory() as tmpdir:
            calc_path = Path(tmpdir) / "calc_gross_profit.py"
            calc_path.write_text("""
# 自定义的 gross_profit 计算（可能加了调整项）
required_fields = ["total_revenue", "operating_cost"]

def calculate(results):
    revenue = results["total_revenue"]
    cost = results["operating_cost"]
    # 这里加了一些调整逻辑
    return {y: revenue.get(y, 0) - cost.get(y, 0) * 0.99 for y in revenue}
""")

            # When: 加载并注册
            calc_dict = load_calculator(str(calc_path))
            registry = get_registry()
            registry.register_dynamic_from_dict(calc_dict)

            # Then: 获取 calculators 时动态的覆盖内置的
            calculators = registry.get_all()
            gross_profit = next(c for c in calculators if c.name == "gross_profit")
            
            # 验证使用的是动态的（不是内置的）
            assert gross_profit._source == str(calc_path)
```

### Step 2: 运行测试

Run: `pytest tests/e2e/test_dynamic_calculator_e2e.py -v`

### Step 3: 提交

```bash
git add tests/e2e/test_dynamic_calculator_e2e.py
git commit -m "test: add E2E tests for dynamic calculator loading"
```

---

## Task 5: 迁移现有 Calculator（可选，后续执行）

> 注：此任务可选，建议在核心功能稳定后再执行。

**Files:**
- Create: `src/value_investment/domain/calculators/calc_gross_profit.py`
- Delete: `src/value_investment/domain/calculators/gross_profit.py`
- (其他 calculator 同理)

### 迁移步骤（每个 calculator 重复）：

1. 创建新的函数式格式文件 `calc_xxx.py`
2. 运行现有测试确保行为一致
3. 删除旧的类格式文件
4. 更新 `__init__.py` 导入
5. 提交

---

## 总结

完成所有任务后，系统将支持：

```bash
# 动态加载单个 calculator
uv run python -m value_investment.cli calc 600519 --calculator ./custom/calc_roic.py

# 动态加载整个目录
uv run python -m value_investment.cli calc 600519 --calculator-dir ./custom/

# 动态 calculator 覆盖内置
uv run python -m value_investment.cli calc 600519 --calculator ./override_builtin.py
```
