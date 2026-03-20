---
name: add-calculator
description: Create new financial calculators for value_investment project. Use when implementing new financial indicators like ROE, gross margin, turnover ratios, or any calculated metrics.
---

# Add Calculator

> **先定义字段，再写 Calculator**  
> 字段必须存在于 `CustomFields` 或 `IFRSFields`

## 命名规范

| 原则 | 说明 |
|------|------|
| snake_case | 全小写，下划线分隔 |
| 简短明确 | 方便阅读，不过度详细 |
| 自主命名 | 以我们为主，不参考 provider |
| **无重复** | 输出字段不能与现有字段同名 |

**示例：** `net_debt_to_equity`, `gross_margin`, `inventory_turnover`

## 流程

### Phase 0: 检查重复（最先做）

添加 Calculator 前，检查输出字段是否已存在：

```bash
uv run python -c "
from value_investment.domain.fields import ALL_FIELDS
# 如：添加净负债率 Calculator，检查 net_debt_to_equity
print('net_debt_to_equity' in ALL_FIELDS)
"
```

### 1. 确认依赖字段

```bash
uv run python -c "
from value_investment.domain.fields import ALL_FIELDS
fields = ['total_revenue', 'operating_cost']
for f in fields:
    print(f'{f}: {f in ALL_FIELDS}')
"
```

### 2. 创建 Calculator

**文件：** `calculators/calc_<name>.py`

```python
"""<Description>"""
from typing import Any

required_fields = ["field_a", "field_b"]  # 依赖字段

def calculate(results: dict[str, dict[int, Any]], config: dict = None) -> dict[int, float]:
    field_a = results.get("field_a", {})
    field_b = results.get("field_b", {})
    
    return {
        year: field_a.get(year, 0) / field_b.get(year, 1)
        for year in field_a
    }
```

### 3. TDD 测试

```bash
# 先写测试，再写实现
uv run python -m pytest tests/ -v -k "<name>"
```

## 常见模式

**简单比率：**
```python
required_fields = ["net_profit", "total_equity"]
```

**平均值（周转率）：**
```python
required_fields = ["operating_cost", "inventory"]
```

**带配置：**
```python
optional_config = {"wacc": 0.10}

def calculate(results, config=None):
    cfg = {**optional_config, **(config or {})}
```

## 验证

### 1. 单元测试

```bash
uv run python -m pytest tests/ -v -k "calc_<name>"
```

### 2. 字段注册验证

```bash
# Calculator 输出字段必须在 CustomFields 中
uv run python -c "
from value_investment.domain.fields import CustomFields
print('calc_output' in CustomFields.all())
"

# 依赖字段必须存在
uv run python -c "
from value_investment.domain.fields import ALL_FIELDS
fields = ['field_a', 'field_b']
print(all(f in ALL_FIELDS for f in fields))
"
```

### 3. Pipeline Dry Run

```bash
uv run python -c "
from value_investment.pipeline.validator import validate_pipeline
report = validate_pipeline(['calc_output'], '600519', 'A股', dry_run=True)
print(f'Blocking errors: {len(report.inconsistencies)}')
for i in report.inconsistencies:
    print('  ', i)
"
```

### 4. Calculator 注册验证

```bash
uv run python -c "
from value_investment.calculator_plugin import get_calculators, load_calculator

calc = load_calculator('calculators/calc_<name>.py')
calcs = get_calculators()
print(f'Loaded: {calc[\"name\"]}')
print(f'In registry: {calc[\"name\"] in [c.name for c in calcs]}')
"
```

### 5. 全量测试

```bash
uv run python -m pytest tests/ -q
```
