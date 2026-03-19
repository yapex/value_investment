---
name: add-calculator
description: Create new financial calculators for value_investment project. Use when implementing new financial indicators like ROE, gross margin, turnover ratios, or any calculated metrics.
---

# Add Calculator

## Golden Rule

> **先定义字段，再写 Calculator**  
> 字段必须存在于 `CustomFields` 或 `IFRSFields`，否则需要先添加字段。

## Workflow

### Phase 1: 确定依赖字段

- [ ] 确认输出指标名称（如 `gross_profit`, `roic`）
- [ ] 确认依赖字段（如 `total_revenue`, `operating_cost`）
- [ ] 确认字段已存在于 `ALL_FIELDS`

```bash
# 验证字段存在
uv run python -c "
from value_investment.domain.fields import ALL_FIELDS, IFRSFields, CustomFields

fields = ['total_revenue', 'operating_cost']
for f in fields:
    print(f'{f}: {f in ALL_FIELDS}')
"
```

### Phase 2: 创建 Calculator 文件

```bash
# 创建文件 (calculators/ 目录下)
# 文件名格式: calc_<name>.py

cat > calculators/calc_<name>.py << 'EOF'
"""<Description>

<Formula explanation>
"""
from typing import Any

# 依赖字段（必须使用 ALL_FIELDS 中存在的字段）
required_fields = ["field_a", "field_b"]

# 可选配置参数（如果需要）
optional_config = {
    "param1": 0.1,
}

def calculate(results: dict[str, dict[int, Any]], config: dict = None) -> dict[int, float]:
    """Calculate <metric> from source fields

    Args:
        results: {field: {year: value}}
        config: 可选配置参数

    Returns:
        {year: <metric>_value}
    """
    cfg = {**optional_config, **(config or {})}
    
    field_a = results.get("field_a", {})
    field_b = results.get("field_b", {})
    
    return {
        year: field_a.get(year, 0) * field_b.get(year, 0)
        for year in field_a
    }
EOF
```

### Phase 3: 验证

```bash
# 运行测试
uv run python -m pytest tests/ -v -k "calculator"

# 验证加载
uv run python -c "
from value_investment.calculator_plugin import registry
from value_investment.calculator_plugin import load_calculator

calc = load_calculator('calculators/calc_<name>.py')
print(f'Loaded: {calc[\"name\"]}')
print(f'Required: {calc[\"required_fields\"]}')

# 注册到 registry
registry.register_from_dict(calc)
print(f'Registered: {registry.get_by_name(\"<name>\")}')
"
```

## Calculator 规范

### 必需元素

| 元素 | 说明 | 示例 |
|------|------|------|
| `required_fields` | 依赖字段列表 | `["total_revenue", "operating_cost"]` |
| `calculate()` | 计算函数 | `def calculate(results, config=None)` |

### 可选元素

| 元素 | 说明 | 示例 |
|------|------|------|
| `name` | 计算器名称（默认从文件名推断） | `"gross_profit"` |
| `optional_config` | 默认配置参数 | `{"wacc": 0.10}` |

### calculate() 函数签名

```python
def calculate(results: dict[str, dict[int, Any]], config: dict = None) -> dict[int, float]:
    """
    Args:
        results: {field: {year: value}}
        config: 可选配置字典
        
    Returns:
        {year: calculated_value}
    """
```

## 常见模式

### 简单比率

```python
required_fields = ["net_profit", "total_equity"]

def calculate(results):
    net_profit = results.get("net_profit", {})
    equity = results.get("total_equity", {})
    return {
        year: net_profit.get(year, 0) / equity.get(year, 1)
        for year in net_profit
    }
```

### 平均值计算（如周转率）

```python
required_fields = ["operating_cost", "inventory"]

def calculate(results):
    cost = results.get("operating_cost", {})
    inventory = results.get("inventory", {})
    
    turnover = {}
    for year in cost:
        curr = inventory.get(year, 0)
        prev = inventory.get(year - 1, 0)  # 前一年
        avg = (curr + prev) / 2
        if avg != 0:
            turnover[year] = cost.get(year, 0) / avg
    return turnover
```

### 带配置的 Calculator

```python
required_fields = ["operating_cash_flow", "market_cap"]

optional_config = {
    "wacc": 0.10,
    "g_terminal": 0.03,
}

def calculate(results, config=None):
    cfg = {**optional_config, **(config or {})}
    # 使用 cfg["wacc"], cfg["g_terminal"]
```

## 文件位置

| 类型 | 位置 |
|------|------|
| 用户 calculators | `{cwd}/calculators/calc_*.py` |
| 项目 calculators | `{project_root}/calculators/calc_*.py` |
| 包内 calculators | `value_investment/calculators/calc_*.py` |

## Validation Checklist

- [ ] `required_fields` 中的字段都在 `ALL_FIELDS` 中
- [ ] `calculate()` 返回 `{year: value}` 格式
- [ ] 文件名格式为 `calc_<name>.py`
- [ ] `uv run python -m pytest tests/ -v` 全部通过
