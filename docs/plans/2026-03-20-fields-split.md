# Fields 拆分实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 `CustomFields` 拆分为 `SourceFields`（原始数据字段）和 `IndicatorFields`（衍生指标），使 `fields` 命令只列原始字段，`indicators` 命令列衍生指标。

**Architecture:** 保持向后兼容，通过 `__getattr__` 让 `CustomFields` 作为 `SourceFields` 的别名，避免大规模 import 修改。

**Tech Stack:** Python, pytest

---

## 影响范围分析

| 文件 | 修改方式 |
|------|---------|
| `domain/fields.py` | 重构核心数据结构 |
| `domain/__init__.py` | 更新导出 |
| `cli.py` | `fields` 命令只列 SourceFields |
| 41 个 Calculator | `name` 输出即为 Indicator |

---

## Task 1: 重构 fields.py - 定义新数据结构

**Files:**
- Modify: `src/value_investment/domain/fields.py`
- Test: `tests/domain/test_fields_split.py` (新建)

**Step 1: 编写测试**

```python
# tests/domain/test_fields_split.py
import pytest
from value_investment.domain.fields import (
    SourceFields,
    IndicatorFields,
    ALL_FIELDS,
    get_source_fields,
    get_indicator_fields,
)


def test_source_fields_contains_original_data():
    """SourceFields 应包含原始数据字段"""
    source = get_source_fields()
    assert "net_profit" in source
    assert "total_revenue" in source
    assert "inventory" in source
    assert "short_term_borrowings" in source


def test_indicator_fields_contains_calculated_metrics():
    """IndicatorFields 应包含衍生指标"""
    indicators = get_indicator_fields()
    assert "roe" in indicators
    assert "net_margin" in indicators
    assert "revenue_cagr_5y" in indicators


def test_indicator_fields_comes_from_calculators():
    """IndicatorFields 数量应等于 Calculator 数量"""
    from value_investment.calculator_plugin import registry
    indicators = get_indicator_fields()
    assert len(indicators) == len(registry.get_all())


def test_indicator_not_in_source():
    """衍生指标不应出现在 SourceFields"""
    source = get_source_fields()
    indicators = get_indicator_fields()
    overlap = source & indicators
    assert len(overlap) == 0, f"Overlap found: {overlap}"


def test_all_fields_union():
    """ALL_FIELDS = SourceFields | IndicatorFields"""
    source = get_source_fields()
    indicators = get_indicator_fields()
    assert ALL_FIELDS == source | indicators
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/domain/test_fields_split.py -v
```

**Step 3: 实现拆分逻辑**

将 `CustomFields` 重构为两个类：

```python
# src/value_investment/domain/fields.py 关键结构

class SourceFields:
    """原始数据字段 - 从数据源获取的字段"""
    
    # 从原 CustomFields 中筛选出的原始字段
    # (被 Calculator 依赖但不作为 Calculator 输出的字段)
    
    # ========== 资产负债表科目类 ==========
    GOODWILL = "goodwill"
    INTANGIBLE_ASSETS = "intangible_assets"
    LONG_TERM_INVESTMENT = "long_term_investment"
    CONSTRUCTION_IN_PROGRESS = "construction_in_progress"
    LONG_TERM_DEBT = "long_term_debt"
    SHORT_TERM_BORROWINGS = "short_term_borrowings"
    SHORT_TERM_DEBT = "short_term_debt"
    OTHER_RECEIVABLES = "other_receivables"
    NON_CURRENT_LIABILITIES_DUE_1Y = "non_current_liabilities_due_1y"
    BOND_PAYABLE = "bond_payable"
    PREPAYMENT = "prepayment"
    # ... 其他原始字段

    # ========== 利润表补充字段 ==========
    MAIN_BUSINESS_INCOME = "main_business_income"
    NON_OPERATING_INCOME = "non_operating_income"
    FAIR_VALUE_CHANGE = "fair_value_change"
    INVESTMENT_INCOME = "investment_income"
    INTEREST_EXPENSE = "interest_expense"
    INTEREST_INCOME = "interest_income"

    # ========== 衍生指标（来自 Tushare fina_indicator）==========
    # 这些字段虽然从 fina_indicator 获取，但作为原始数据使用
    NET_DEBT = "net_debt"
    EBIT = "ebit"
    EBITDA = "ebitda"
    INTEREST_BEARING_DEBT = "interest_bearing_debt"
    TOTAL_DEBT = "total_debt"
    FREE_CASH_FLOW_TO_FIRM = "free_cash_flow_to_firm"
    FINANCE_EXPENSE_RATIO = "finance_expense_ratio"
    REVENUE_YOY = "revenue_yoy"
    GROSS_MARGIN = "gross_margin"

    @classmethod
    def all(cls) -> frozenset:
        return frozenset(
            v for k, v in vars(cls).items() 
            if k.isupper() and not callable(v)
        )


class IndicatorFields:
    """衍生指标 - 由 Calculator 计算得出的字段"""
    
    # Calculator 输出的指标定义（可从 Calculator registry 动态获取）
    # 也可以定义为常量（从 Calculator 的 name 字段提取）
    
    @classmethod
    def all(cls) -> frozenset:
        """从 Calculator registry 获取所有指标"""
        from value_investment.calculator_plugin import registry
        return frozenset(c.name for c in registry.get_all())


def get_source_fields() -> frozenset:
    """获取所有原始数据字段"""
    return SourceFields.all()


def get_indicator_fields() -> frozenset:
    """获取所有衍生指标"""
    return IndicatorFields.all()


# 向后兼容别名
CustomFields = SourceFields

# 更新 ALL_FIELDS
ALL_FIELDS = SourceFields.all() | IndicatorFields.all()
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/domain/test_fields_split.py -v
```

**Step 5: 提交**

```bash
git add src/value_investment/domain/fields.py tests/domain/test_fields_split.py
git commit -m "feat(domain): split fields into SourceFields and IndicatorFields"
```

---

## Task 2: 更新 domain/__init__.py

**Files:**
- Modify: `src/value_investment/domain/__init__.py`

**Step 1: 更新导出**

```python
"""Domain layer - core business logic"""
from value_investment.domain.fields import (
    IFRSFields,
    SourceFields,
    IndicatorFields,  # 新增
    ALL_FIELDS,
    validate_fields,
    get_source_fields,  # 新增
    get_indicator_fields,  # 新增
)

# 向后兼容
CustomFields = SourceFields

__all__ = [
    "IFRSFields",
    "SourceFields",
    "IndicatorFields",
    "ALL_FIELDS",
    "validate_fields",
    "get_source_fields",
    "get_indicator_fields",
]
```

**Step 2: 运行现有测试确保向后兼容**

```bash
pytest tests/pipeline/test_validator.py -v
```

**Step 3: 提交**

```bash
git add src/value_investment/domain/__init__.py
git commit -m "feat(domain): export new field types"
```

---

## Task 3: 更新 CLI - 分离 fields 和 indicators 命令

**Files:**
- Modify: `src/value_investment/cli.py`

**Step 1: 修改 `fields` 命令**

```python
@app.command()
def fields(
    prefix: str | None = typer.Option(None, "--prefix", "-p", help="Filter by prefix"),
):
    """List all available source fields (raw data from data providers)"""
    from value_investment.domain.fields import get_source_fields
    
    all_fields = sorted(get_source_fields())
    if prefix:
        all_fields = [f for f in all_fields if f.startswith(prefix)]
    for field in all_fields:
        print(field)
```

**Step 2: 验证 `indicators` 命令已正确工作**

```bash
uv run python -m value_investment.cli indicators | wc -l
# 应输出 41 行（指标列表）
```

**Step 3: 提交**

```bash
git add src/value_investment/cli.py
git commit -m "fix(cli): fields command shows only source fields"
```

---

## Task 4: 更新文档

**Files:**
- Modify: `docs/财报分析字段清单.md`

**Step 1: 添加说明**

在文档开头添加：

```markdown
## 字段分类说明

| 类型 | 说明 | CLI 命令 |
|------|------|---------|
| SourceFields (原始字段) | 从数据源直接获取的字段 | `fields` |
| IndicatorFields (衍生指标) | 由 Calculator 计算得出的字段 | `indicators` |
```

**Step 2: 提交**

```bash
git add docs/财报分析字段清单.md
git commit -m "docs: explain field types in documentation"
```

---

## Task 5: 验证端到端

**Step 1: 运行完整测试**

```bash
uv run python -m pytest tests/ -v
```

**Step 2: 验证 CLI 命令**

```bash
# 查看原始字段
uv run python -m value_investment.cli fields | head -20

# 查看衍生指标  
uv run python -m value_investment.cli indicators | head -20

# 验证无重叠
uv run python -c "
from value_investment.domain.fields import get_source_fields, get_indicator_fields
source = get_source_fields()
indicators = get_indicator_fields()
overlap = source & indicators
print(f'Source: {len(source)}, Indicators: {len(indicators)}, Overlap: {len(overlap)}')
assert len(overlap) == 0, f'Overlap: {overlap}'
print('✓ No overlap!')
"
```

**Step 3: 提交**

```bash
git commit -m "chore: verify fields split works end-to-end"
```

---

## 总结

| Task | 文件修改 | 关键变更 |
|------|---------|---------|
| 1 | `fields.py` | 新增 `SourceFields` + `IndicatorFields` |
| 2 | `__init__.py` | 更新导出 |
| 3 | `cli.py` | `fields` 命令只列原始字段 |
| 4 | `docs/` | 更新文档 |
| 5 | - | 端到端验证 |
