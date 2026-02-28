# MarketCap Indicator 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 新增 MarketCapIndicator，让 `market_cap` 命令可用

**Architecture:** 新建 `market_cap.py` 指标类，从财务指标获取市值字段，自动检测市场类型

**Tech Stack:** Python, 继承 BaseIndicator

---

## Task 1: 创建 MarketCapIndicator 类

**Files:**
- Create: `src/value_investment/indicators/market_cap.py`
- Test: `tests/test_market_cap_indicator.py`

### Step 1: 写失败的测试

```python
"""Test MarketCapIndicator"""
import pytest
from value_investment.indicators.market_cap import MarketCapIndicator


def test_indicator_has_name():
    """MarketCapIndicator should have name 'market_cap'"""
    indicator = MarketCapIndicator()
    assert indicator.name == "market_cap"


def test_indicator_has_description():
    """MarketCapIndicator should have description"""
    indicator = MarketCapIndicator()
    assert indicator.description is not None
    assert len(indicator.description) > 0
```

### Step 2: 运行测试确认失败

```bash
cd /root/workspace/skills/value_investment && uv run --directory . pytest tests/test_market_cap_indicator.py -v
```

Expected: `ModuleNotFoundError: No module named 'value_investment.indicators.market_cap'`

### Step 3: 创建最小实现

```python
"""Market Capitalization Indicator - fetch market cap from financial indicators"""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class MarketCapIndicator(BaseIndicator):
    """
    市值指标
    
    从财务指标直接获取市值，自动检测市场类型。
    - 港股: hk_market_cap (港元)
    - A股: a_market_cap (人民币)
    - 美股: us_market_cap (美元)
    """
    
    name = "market_cap"
    needs = ['financial_indicator']
    description = "总市值 (从财务指标获取)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # TODO: 实现计算逻辑
        return IndicatorResult(
            value=0.0,
            unit="",
            description="总市值",
            years=[],
            values=[]
        )

    def get_required_fields(self) -> List[str]:
        return []
```

### Step 4: 运行测试确认通过

```bash
cd /root/workspace/skills/value_investment && uv run --directory . pytest tests/test_market_cap_indicator.py -v
```

Expected: 2 passed

### Step 5: 提交

```bash
git add src/value_investment/indicators/market_cap.py tests/test_market_cap_indicator.py
git commit -m "feat: 添加 MarketCapIndicator 骨架"
```

---

## Task 2: 实现港股市值获取

**Files:**
- Modify: `src/value_investment/indicators/market_cap.py`
- Modify: `tests/test_market_cap_indicator.py`

### Step 1: 写失败的测试

```python
def test_hk_market_cap_from_financial_indicator():
    """Should get market cap from hk_market_cap field for HK stocks"""
    import pandas as pd
    from value_investment.indicators.market_cap import MarketCapIndicator
    
    indicator = MarketCapIndicator()
    
    # 模拟港股财务指标数据
    finind = pd.DataFrame({
        'hk_market_cap': [4151041376020.0],  # 腾讯市值
    })
    
    result = indicator.calculate(
        pd.DataFrame(),
        financial_indicator=finind,
        stock_code='00700'
    )
    
    assert result.value == 4151041376020.0
    assert '港元' in result.description or 'HK' in result.description
```

### Step 2: 运行测试确认失败

```bash
cd /root/workspace/skills/value_investment && uv run --directory . pytest tests/test_market_cap_indicator.py::test_hk_market_cap_from_financial_indicator -v
```

Expected: `AssertionError: assert 0.0 == 4151041376020.0`

### Step 3: 实现港股市值获取

在 `market_cap.py` 的 `calculate` 方法中添加：

```python
def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
    financial_indicator = kwargs.get('financial_indicator')
    stock_code = kwargs.get('stock_code', '')
    
    if financial_indicator is None or financial_indicator.empty:
        return IndicatorResult(
            value=0.0,
            unit="",
            description="总市值 (无财务指标数据)",
            years=[],
            values=[]
        )
    
    finind = financial_indicator
    
    # 检测市场类型
    is_hk = len(stock_code) == 5 and stock_code.isdigit()
    is_us = stock_code.isalpha()
    
    market_cap = None
    market_name = ""
    unit = ""
    
    if is_hk:
        # 港股：优先使用内部标准字段
        for col in ['hk_market_cap', 'market_cap_hkd', '港股市值(港元)', '总市值(港元)']:
            if col in finind.columns:
                market_cap = float(finind[col].iloc[0])
                break
        market_name = "港股"
        unit = "港元"
    elif is_us:
        # TODO: 美股处理（下一个任务）
        pass
    else:
        # TODO: A股处理（下一个任务）
        pass
    
    if market_cap and market_cap > 0:
        return IndicatorResult(
            value=market_cap,
            unit=unit,
            description=f"总市值 ({market_name}, {unit})",
            years=[],
            values=[]
        )
    
    return IndicatorResult(
        value=0.0,
        unit="",
        description="总市值 (无法获取)",
        years=[],
        values=[]
    )
```

### Step 4: 运行测试确认通过

```bash
cd /root/workspace/skills/value_investment && uv run --directory . pytest tests/test_market_cap_indicator.py::test_hk_market_cap_from_financial_indicator -v
```

Expected: passed

### Step 5: 提交

```bash
git add src/value_investment/indicators/market_cap.py tests/test_market_cap_indicator.py
git commit -m "feat: MarketCapIndicator 支持港股市值获取"
```

---

## Task 3: 实现 A股和美股市值获取

**Files:**
- Modify: `src/value_investment/indicators/market_cap.py`
- Modify: `tests/test_market_cap_indicator.py`

### Step 1: 写失败的测试

```python
def test_a_market_cap_from_financial_indicator():
    """Should get market cap for A-shares"""
    import pandas as pd
    from value_investment.indicators.market_cap import MarketCapIndicator
    
    indicator = MarketCapIndicator()
    
    finind = pd.DataFrame({
        'a_market_cap': [2000000000000.0],  # 茅台市值
    })
    
    result = indicator.calculate(
        pd.DataFrame(),
        financial_indicator=finind,
        stock_code='600519'
    )
    
    assert result.value == 2000000000000.0
    assert '人民币' in result.description or 'A' in result.description


def test_us_market_cap_from_financial_indicator():
    """Should get market cap for US stocks"""
    import pandas as pd
    from value_investment.indicators.market_cap import MarketCapIndicator
    
    indicator = MarketCapIndicator()
    
    finind = pd.DataFrame({
        'us_market_cap': [3000000000000.0],  # 苹果市值
    })
    
    result = indicator.calculate(
        pd.DataFrame(),
        financial_indicator=finind,
        stock_code='AAPL'
    )
    
    assert result.value == 3000000000000.0
    assert '美元' in result.description or 'US' in result.description
```

### Step 2: 运行测试确认失败

```bash
cd /root/workspace/skills/value_investment && uv run --directory . pytest tests/test_market_cap_indicator.py -v -k "a_market or us_market"
```

Expected: 2 failed

### Step 3: 实现 A股和美股逻辑

在 `calculate` 方法中补充：

```python
    elif is_us:
        # 美股：优先使用内部标准字段
        for col in ['us_market_cap', 'market_cap_usd', '总市值(美元)']:
            if col in finind.columns:
                market_cap = float(finind[col].iloc[0])
                break
        market_name = "美股"
        unit = "美元"
    else:
        # A股：优先使用内部标准字段
        for col in ['a_market_cap', 'market_cap_cny', '总市值(元)', '总市值(人民币)']:
            if col in finind.columns:
                market_cap = float(finind[col].iloc[0])
                break
        market_name = "A股"
        unit = "人民币"
```

### Step 4: 运行测试确认通过

```bash
cd /root/workspace/skills/value_investment && uv run --directory . pytest tests/test_market_cap_indicator.py -v
```

Expected: all passed

### Step 5: 提交

```bash
git add src/value_investment/indicators/market_cap.py tests/test_market_cap_indicator.py
git commit -m "feat: MarketCapIndicator 支持A股和美股市值获取"
```

---

## Task 4: 在 Factory 注册 MarketCapIndicator

**Files:**
- Modify: `src/value_investment/indicators/factory.py`

### Step 1: 写失败的测试

```python
def test_market_cap_registered_in_factory():
    """market_cap should be available via factory"""
    from value_investment.indicators.factory import IndicatorFactory
    
    factory = IndicatorFactory()
    indicator = factory.get('market_cap')
    
    assert indicator is not None
    assert indicator.name == 'market_cap'
```

### Step 2: 运行测试确认失败

```bash
cd /root/workspace/skills/value_investment && uv run --directory . pytest tests/test_market_cap_indicator.py::test_market_cap_registered_in_factory -v
```

Expected: `ValueError: Unknown indicator: market_cap`

### Step 3: 注册到 Factory

修改 `factory.py`:

```python
# 在文件顶部添加导入
from value_investment.indicators.market_cap import MarketCapIndicator

# 在 _register_default_indicators 的 indicators 列表中添加
MarketCapIndicator(),
```

### Step 4: 运行测试确认通过

```bash
cd /root/workspace/skills/value_investment && uv run --directory . pytest tests/test_market_cap_indicator.py::test_market_cap_registered_in_factory -v
```

Expected: passed

### Step 5: 提交

```bash
git add src/value_investment/indicators/factory.py tests/test_market_cap_indicator.py
git commit -m "feat: 在 Factory 注册 MarketCapIndicator"
```

---

## Task 5: 集成测试 - CLI 验证

**Files:**
- 无新增文件，验证现有功能

### Step 1: 测试港股

```bash
cd /root/workspace/skills/value_investment && uv run --directory . python -m value_investment.cli indicator market_cap -s 00700 -m HK
```

Expected: 返回腾讯市值 (~4.15万亿港元)

### Step 2: 测试A股

```bash
cd /root/workspace/skills/value_investment && uv run --directory . python -m value_investment.cli indicator market_cap -s 600519 -m A
```

Expected: 返回茅台市值

### Step 3: 测试美股

```bash
cd /root/workspace/skills/value_investment && uv run --directory . python -m value_investment.cli indicator market_cap -s AAPL -m US
```

Expected: 返回苹果市值

### Step 4: 确认 list-indicators 包含 market_cap

```bash
cd /root/workspace/skills/value_investment && uv run --directory . python -m value_investment.cli list-indicators | grep market_cap
```

Expected: 显示 `market_cap`

### Step 5: 提交

```bash
git add -A
git commit -m "test: 集成测试验证 market_cap 指标可用"
```

---

## 验收清单

- [ ] `cli indicator market_cap -s 00700 -m HK` 返回腾讯市值
- [ ] `cli indicator market_cap -s 600519 -m A` 返回茅台市值
- [ ] `cli indicator market_cap -s AAPL -m US` 返回苹果市值
- [ ] 所有单元测试通过
- [ ] `list-indicators` 显示 `market_cap`
