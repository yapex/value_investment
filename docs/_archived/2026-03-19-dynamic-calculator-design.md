# 动态 Calculator 加载机制设计

## 背景

现有 `value_investment` 工具的 calculator 使用 `@calculator` 装饰器静态注册。当业务需要自定义财务指标时，需要修改源代码并重新部署。

本设计支持 skill 生成 Python 脚本，通过 CLI 动态加载为 calculator，实现灵活扩展。

## 目标

1. Skill 可以生成 Python 脚本文件，描述自定义财务指标的计算方式
2. CLI 支持通过路径参数加载动态 calculator
3. 动态 calculator 与内置 calculator 统一处理，优先级更高
4. TDD 驱动开发

---

## Calculator 脚本格式

### 函数式格式

```python
# ./custom/calc_roic.py

required_fields = ["net_income", "total_equity", "debt"]

def calculate(results):
    """计算 ROIC = Net Income / (Equity + Debt)"""
    income = results["net_income"]
    equity = results["total_equity"]
    debt = results.get("debt", {})
    return {y: income[y] / (equity.get(y, 0) + debt.get(y, 0)) for y in income}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | `str` | 否 | 指标名称。默认从文件名推断（`calc_roic.py` → `roic`） |
| `required_fields` | `list[str]` | **是** | 依赖的财务字段列表 |
| `calculate` | `function` | **是** | 计算函数，接收 `results` 返回计算结果 |

### 命名约定

- 文件名必须符合 `calc_*.py` 格式（如 `calc_roic.py`）
- `name` 默认从文件名推断：去掉 `calc_` 前缀
- 如需自定义 name，可在脚本中显式指定：

```python
# ./custom/calc_my_roic.py
name = "roic"  # 显式指定，覆盖默认的 "my_roic"
required_fields = ["net_income", "total_equity"]
def calculate(results): ...
```

---

## 技术方案

### 动态加载机制

使用 `importlib` + 隔离命名空间实现动态加载：

```python
# src/value_investment/domain/calculators/dynamic_loader.py

import importlib.util
import hashlib
from pathlib import Path
from typing import Any

def load_calculator(path: str) -> dict[str, Any]:
    """加载单个 calculator 脚本
    
    使用 importlib + 隔离命名空间，不污染 sys.modules
    """
    module_name = f"dynamic_calc_{hashlib.md5(path.encode()).hexdigest()}"
    
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
            raise ValueError(
                f"Cannot infer name from '{path}'. "
                f"Please name file as 'calc_xxx.py' or specify 'name' in script."
            )
    
    return {
        "name": name,
        "required_fields": set(module.required_fields),
        "calculate": module.calculate,
        "_source": path,
    }


def load_calculators_from_dir(dir_path: str) -> list[dict[str, Any]]:
    """扫描目录加载所有 calc_*.py 文件"""
    calculators = []
    
    for py_file in Path(dir_path).glob("calc_*.py"):
        try:
            calc = load_calculator(str(py_file))
            calculators.append(calc)
        except Exception as e:
            print(f"⚠️  Failed to load {py_file}: {e}")
    
    return calculators
```

### Registry 集成策略

动态 calculator 优先级高于内置，同名时覆盖：

```python
# src/value_investment/domain/calculators/registry.py

def get_calculators() -> list:
    """获取所有 calculator（含内置 + 动态）"""
    calculators = {}
    
    # 1. 先加载内置
    for cls in _get_builtin_calculators():
        calculators[cls.name] = cls()
    
    # 2. 动态 calculator 覆盖内置
    for dynamic in _dynamic_calculators:
        calculators[dynamic["name"]] = DynamicCalculatorAdapter(**dynamic)
    
    return list(calculators.values())


class DynamicCalculatorAdapter:
    """动态 calculator 适配器，将函数式转换为 Calculator 接口"""
    
    def __init__(self, name, required_fields, calculate, _source=None):
        self.name = name
        self.required_fields = required_fields
        self._calculate = calculate
    
    def calculate(self, results):
        return self._calculate(results)
```

---

## CLI 接口

```bash
# 单个文件
uv run python -m value_investment.cli calc 600519 --calculator ./custom/calc_roic.py

# 整个目录
uv run python -m value_investment.cli calc 600519 --calculator-dir ./custom/

# 组合使用
uv run python -m value_investment.cli calc 600519 \
    --calculator ./special/calc_custom.py \
    --calculator-dir ./custom/
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--calculator <path>` | 指定单个 calculator 脚本路径，可重复 |
| `--calculator-dir <path>` | 指定目录，扫描 `calc_*.py` 加载 |

---

## TDD 开发计划

### 测试用例设计

```python
# tests/domain/calculators/test_dynamic_loader.py

def test_load_calculator_from_file():
    """测试加载单个 calculator 脚本"""
    # Given: 一个有效的 calc_roic.py 文件
    # When: 调用 load_calculator
    # Then: 返回正确的 name, required_fields, calculate
    
def test_load_calculator_infer_name_from_filename():
    """测试 name 从文件名推断"""
    # Given: calc_roic.py 没有显式 name
    # When: 调用 load_calculator
    # Then: name = "roic"
    
def test_load_calculator_explicit_name_override():
    """测试显式 name 覆盖文件名推断"""
    # Given: calc_my_roic.py 有 name = "roic"
    # When: 调用 load_calculator
    # Then: name = "roic"（不是 "my_roic"）

def test_load_calculators_from_dir():
    """测试目录扫描加载"""
    # Given: 目录下有 calc_roic.py, calc_pe.py, other.py
    # When: 调用 load_calculators_from_dir
    # Then: 只加载 calc_roic.py 和 calc_pe.py

def test_dynamic_calculator_override_builtin():
    """测试动态 calculator 覆盖内置"""
    # Given: 内置有 roic，动态也定义了 roic
    # When: 调用 get_calculators
    # Then: 返回动态的 roic

def test_invalid_calculator_missing_required_fields():
    """测试缺失 required_fields 报错"""
    # Given: 缺少 required_fields 的脚本
    # When: 调用 load_calculator
    # Then: 抛出 ValueError

def test_invalid_calculator_missing_calculate():
    """测试缺失 calculate 报错"""
    # Given: 缺少 calculate 函数的脚本
    # When: 调用 load_calculator
    # Then: 抛出 ValueError
```

### 实现顺序

1. **红：写测试** → `test_dynamic_loader.py`
2. **绿：实现 loader** → `dynamic_loader.py`
3. **绿：集成 registry** → 改造 `registry.py`
4. **绿：CLI 参数** → `cli.py` 添加 `--calculator`/`--calculator-dir`
5. **重构：迁移现有 calculator** → `gross_profit.py` 等改为函数式格式
6. **端到端测试** → 用真实 skill 生成脚本测试

---

## 文件改动清单

| 操作 | 文件 |
|------|------|
| 新增 | `src/value_investment/domain/calculators/dynamic_loader.py` |
| 改造 | `src/value_investment/domain/calculators/registry.py` |
| 改造 | `src/value_investment/cli.py` |
| 新增 | `tests/domain/calculators/test_dynamic_loader.py` |
| 迁移 | `src/value_investment/domain/calculators/gross_profit.py` → 函数式 |
| 迁移 | `src/value_investment/domain/calculators/implied_growth.py` → 函数式 |
| 迁移 | `src/value_investment/domain/calculators/inventory_turnover.py` → 函数式 |
| 迁移 | `src/value_investment/domain/calculators/operating_profit_margin.py` → 函数式 |

---

## 附录：现有 Calculator 迁移示例

```python
# 迁移前：src/value_investment/domain/calculators/gross_profit.py

from value_investment.domain.calculators import calculator
from value_investment.domain.fields import CustomFields, IFRSFields

@calculator
class GrossProfit:
    name = CustomFields.GROSS_PROFIT
    required_fields = {IFRSFields.TOTAL_REVENUE, IFRSFields.OPERATING_COST}
    
    def calculate(self, results):
        revenue = results.get(IFRSFields.TOTAL_REVENUE, {})
        cost = results.get(IFRSFields.OPERATING_COST, {})
        return {year: revenue.get(year, 0) - cost.get(year, 0) for year in revenue}
```

```python
# 迁移后：src/value_investment/domain/calculators/calc_gross_profit.py

required_fields = ["total_revenue", "operating_cost"]

def calculate(results):
    revenue = results["total_revenue"]
    cost = results["operating_cost"]
    return {year: revenue.get(year, 0) - cost.get(year, 0) for year in revenue}
```

注意：迁移后字段名使用字符串（如 `"total_revenue"`），由 mapper 层处理与 IFRSFields 的映射。
