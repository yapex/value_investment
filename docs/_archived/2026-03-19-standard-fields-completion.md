# Standard Fields Completion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现标准财务字段 100% 覆盖，完成 P0 直接映射和 P1 Calculator 计算。

**Architecture:** 通过 TushareFieldMapper 直接映射字段，通过 Calculator 计算派生字段，保持架构简洁。

**Tech Stack:** Python, Tushare API, pandas, pytest

---

## Context

当前状态：
- IFRS 标准字段总数: 40 (33 财务报表 + 7 市场数据)
- 已覆盖: 33 财务报表
- 缺失: 7 字段

待处理字段：
| 类别 | 字段 | 解决方案 |
|------|------|----------|
| P0 | basic_eps, diluted_eps, book_value_per_share | 直接映射 |
| P0 | total_shares | 直接映射到 balance_sheet |
| P1 | gross_profit | Calculator 计算 |
| P1 | inventory_turnover | Calculator 计算 |
| P2 | market_cap, pe_ratio, pb_ratio | 独立 API (可选) |

---

## Task 1: P0 - 添加指标字段映射

**Files:**
- Modify: `src/value_investment/pipeline/data/tushare_mapper.py:160-180`

**Step 1: 添加单元测试**

```python
def test_indicator_eps_bps_fields():
    """Test basic_eps, diluted_eps, book_value_per_share mapping"""
    mapper = TushareFieldMapper()
    
    assert IFRSFields.BASIC_EPS in mapper.reverse.indicators
    assert mapper.reverse.indicators[IFRSFields.BASIC_EPS] == "eps"
    
    assert IFRSFields.DILUTED_EPS in mapper.reverse.indicators
    assert IFRSFields.BOOK_VALUE_PER_SHARE in mapper.reverse.indicators
    assert mapper.reverse.indicators[IFRSFields.BOOK_VALUE_PER_SHARE] == "bps"
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/pipeline/test_tushare_mapper.py::test_indicator_eps_bps_fields -v`
Expected: FAIL with assertion error

**Step 3: 添加映射**

在 `tushare_mapper.py` 的 `indicator_fields` 字典中添加:

```python
indicator_fields = {
    ...
    IFRSFields.BASIC_EPS: "eps",
    IFRSFields.DILUTED_EPS: "dt_eps",
    IFRSFields.BOOK_VALUE_PER_SHARE: "bps",
}
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/pipeline/test_tushare_mapper.py::test_indicator_eps_bps_fields -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/value_investment/pipeline/data/tushare_mapper.py tests/pipeline/test_tushare_mapper.py
git commit -m "feat: add eps, dt_eps, bps indicator mappings"
```

---

## Task 2: P0 - 添加总股本字段映射

**Files:**
- Modify: `src/value_investment/pipeline/data/tushare_mapper.py:120-140`

**Step 1: 添加单元测试**

```python
def test_total_shares_mapping():
    """Test total_shares from balance_sheet"""
    mapper = TushareFieldMapper()
    
    assert "total_shares" in mapper.reverse.balance_sheet
    assert mapper.reverse.balance_sheet["total_shares"] == "total_share"
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/pipeline/test_tushare_mapper.py::test_total_shares_mapping -v`
Expected: FAIL

**Step 3: 添加映射**

在 `direct_balance_fields` 字典中添加:

```python
direct_balance_fields = {
    ...
    "total_shares": "total_share",
}
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/pipeline/test_tushare_mapper.py::test_total_shares_mapping -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/value_investment/pipeline/data/tushare_mapper.py tests/pipeline/test_tushare_mapper.py
git commit -m "feat: add total_shares mapping from balance_sheet"
```

---

## Task 3: P1 - 创建 GrossProfitCalculator

**Files:**
- Create: `src/value_investment/pipeline/calculators/gross_profit.py`
- Modify: `src/value_investment/pipeline/api.py`
- Test: `tests/pipeline/test_gross_profit_calculator.py`

**Step 1: 编写测试**

```python
# tests/pipeline/test_gross_profit_calculator.py
def test_gross_profit_calculation():
    from value_investment.pipeline.calculators.gross_profit import GrossProfitCalculator
    from value_investment.pipeline.fields import IFRSFields
    
    calc = GrossProfitCalculator()
    results = {
        IFRSFields.TOTAL_REVENUE: {2024: 1000, 2023: 900},
        IFRSFields.OPERATING_COST: {2024: 600, 2023: 540},
    }
    gp = calc.calculate(results)
    
    assert gp[2024] == 400
    assert gp[2023] == 360
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/pipeline/test_gross_profit_calculator.py -v`
Expected: FAIL with "No module named"

**Step 3: 实现 Calculator**

```python
# src/value_investment/pipeline/calculators/gross_profit.py
from typing import Any
from value_investment.pipeline.fields import IFRSFields

class GrossProfitCalculator:
    name = IFRSFields.GROSS_PROFIT
    required_fields = {
        IFRSFields.TOTAL_REVENUE,
        IFRSFields.OPERATING_COST,
    }

    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        revenue = results.get(IFRSFields.TOTAL_REVENUE, {})
        cost = results.get(IFRSFields.OPERATING_COST, {})
        
        return {
            year: revenue.get(year, 0) - cost.get(year, 0)
            for year in revenue
        }
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/pipeline/test_gross_profit_calculator.py -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/value_investment/pipeline/calculators/gross_profit.py tests/pipeline/test_gross_profit_calculator.py
git commit -m "feat: add GrossProfitCalculator"
```

---

## Task 4: P1 - 创建 InventoryTurnoverCalculator

**Files:**
- Create: `src/value_investment/pipeline/calculators/inventory_turnover.py`
- Test: `tests/pipeline/test_inventory_turnover_calculator.py`

**Step 1: 编写测试**

```python
# tests/pipeline/test_inventory_turnover_calculator.py
def test_inventory_turnover_calculation():
    from value_investment.pipeline.calculators.inventory_turnover import InventoryTurnoverCalculator
    from value_investment.pipeline.fields import IFRSFields
    
    calc = InventoryTurnoverCalculator()
    results = {
        IFRSFields.OPERATING_COST: {2024: 1000, 2023: 900, 2022: 800},
        IFRSFields.INVENTORY: {2024: 200, 2023: 180, 2022: 160},
    }
    it = calc.calculate(results)
    
    # 2024: 1000 / ((200+180)/2) = 1000/190 = 5.26
    assert abs(it[2024] - 5.263) < 0.001
```

**Step 2: 运行测试验证失败**

Run: `pytest tests/pipeline/test_inventory_turnover_calculator.py -v`
Expected: FAIL

**Step 3: 实现 Calculator**

```python
# src/value_investment/pipeline/calculators/inventory_turnover.py
from typing import Any
from value_investment.pipeline.fields import IFRSFields

class InventoryTurnoverCalculator:
    name = IFRSFields.INVENTORY_TURNOVER
    required_fields = {
        IFRSFields.OPERATING_COST,
        IFRSFields.INVENTORY,
    }

    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        cost = results.get(IFRSFields.OPERATING_COST, {})
        inventory = results.get(IFRSFields.INVENTORY, {})
        
        turnover = {}
        years = cost.keys()
        for year in years:
            curr_inv = inventory.get(year, 0)
            prev_inv = inventory.get(year - 1, 0)
            avg_inv = (curr_inv + prev_inv) / 2
            if avg_inv != 0:
                turnover[year] = cost.get(year, 0) / avg_inv
        return turnover
```

**Step 4: 运行测试验证通过**

Run: `pytest tests/pipeline/test_inventory_turnover_calculator.py -v`
Expected: PASS

**Step 5: 提交**

```bash
git add src/value_investment/pipeline/calculators/inventory_turnover.py tests/pipeline/test_inventory_turnover_calculator.py
git commit -m "feat: add InventoryTurnoverCalculator"
```

---

## Task 5: 集成 Calculator 到 PipelineAPI

**Files:**
- Modify: `src/value_investment/pipeline/api.py`

**Step 1: 更新 get_data 方法集成 Calculator**

在 `get_data` 方法中添加:

```python
async def get_data(self, symbol, fields, end, years, market):
    # ... 现有代码 ...
    
    # 计算派生字段
    calculators = {
        IFRSFields.GROSS_PROFIT: GrossProfitCalculator(),
        IFRSFields.INVENTORY_TURNOVER: InventoryTurnoverCalculator(),
    }
    
    for field in fields:
        if field in calculators:
            calc = calculators[field]
            # 获取所需字段
            calc_results = {}
            for req_field in calc.required_fields:
                if req_field in message.results:
                    calc_results[req_field] = message.results[req_field]
            # 计算并添加结果
            calculated = calc.calculate(calc_results)
            message.results[field] = calculated
            message.require.discard(field)
```

**Step 2: 添加 import**

```python
from value_investment.pipeline.calculators.gross_profit import GrossProfitCalculator
from value_investment.pipeline.calculators.inventory_turnover import InventoryTurnoverCalculator
```

**Step 3: 运行 E2E 测试**

Run: `TUSHARE_TOKEN=$TUSHARE_TOKEN pytest tests/pipeline/test_e2e_roic.py -v`
Expected: PASS

**Step 4: 提交**

```bash
git add src/value_investment/pipeline/api.py
git commit -m "feat: integrate calculators into PipelineAPI"
```

---

## Task 6: E2E 验证

**Step 1: 运行完整测试**

```bash
uv run python -c "
import asyncio
from value_investment.pipeline.api import PipelineAPI
from value_investment.pipeline.fields import IFRSFields

async def main():
    api = PipelineAPI()
    result = await api.get_data(
        '600519',
        fields=[
            IFRSFields.GROSS_PROFIT,
            IFRSFields.INVENTORY_TURNOVER,
            IFRSFields.BASIC_EPS,
            IFRSFields.TOTAL_SHARES,
        ],
        end='2024',
        years=3
    )
    print('Results:', list(result.keys()))

asyncio.run(main())
"
```

Expected: 输出包含所有查询字段

**Step 2: 提交**

```bash
git add -A
git commit -m "feat: complete standard fields mapping"
```

---

## 验收标准

```python
# 应能查询所有财务报表字段
result = await api.get_data(
    "600519",
    fields=[
        # 利润表
        "gross_profit",  # Calculator
        # 财务指标
        "inventory_turnover",  # Calculator
        # 每股指标
        "basic_eps", "diluted_eps", "book_value_per_share",
        # 股本
        "total_shares",
    ],
    end="2024",
    years=10
)
```

---

## Plan complete and saved to `docs/plans/2026-03-19-standard-fields-completion.md`.

**Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
