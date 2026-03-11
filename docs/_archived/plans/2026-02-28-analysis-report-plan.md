# 财报分析报告生成器实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 扩展 analyze 方法，新增 9 个指标 + 异常检测 + Markdown 报告生成

**Architecture:** 新增 growth.py, safety.py, detector.py, reporter.py；修改 efficiency.py, api.py

**Tech Stack:** Python, 继承 BaseIndicator, sessions_spawn 调用 LLM

---

## Task 1: 创建 growth.py - 成长性指标

**Files:**
- Create: `src/value_investment/indicators/growth.py`
- Create: `tests/test_growth_indicators.py`

### Step 1: 写失败的测试

```python
"""Test Growth Indicators"""
import pytest
import pandas as pd
from value_investment.indicators.growth import (
    RevenueGrowthIndicator,
    ProfitGrowthIndicator,
    AssetGrowthIndicator,
    EquityGrowthIndicator,
)


def test_revenue_growth_indicator():
    """Revenue growth should be calculated correctly"""
    indicator = RevenueGrowthIndicator()
    
    income = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31', '2021-12-31'],
        'OPERATE_INCOME': [1200.0, 1000.0, 800.0],
    })
    
    result = indicator.calculate(pd.DataFrame(), income=income)
    
    assert result.value == 20.0  # (1200-1000)/1000 * 100
    assert '%' in result.unit


def test_profit_growth_indicator():
    """Profit growth should be calculated correctly"""
    indicator = ProfitGrowthIndicator()
    
    income = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31', '2021-12-31'],
        'NETPROFIT': [240.0, 200.0, 160.0],
    })
    
    result = indicator.calculate(pd.DataFrame(), income=income)
    
    assert result.value == 20.0  # (240-200)/200 * 100


def test_asset_growth_indicator():
    """Asset growth should be calculated correctly"""
    indicator = AssetGrowthIndicator()
    
    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31', '2021-12-31'],
        'TOTAL_ASSETS': [1200.0, 1000.0, 800.0],
    })
    
    result = indicator.calculate(pd.DataFrame(), balance=balance)
    
    assert result.value == 20.0


def test_equity_growth_indicator():
    """Equity growth should be calculated correctly"""
    indicator = EquityGrowthIndicator()
    
    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31', '2022-12-31', '2021-12-31'],
        'TOTAL_EQUITY': [800.0, 700.0, 600.0],
    })
    
    result = indicator.calculate(pd.DataFrame(), balance=balance)
    
    assert result.value == pytest.approx(14.29, 0.1)
```

### Step 2: 运行测试确认失败

```bash
cd /root/workspace/skills/value_investment && uv run --directory . pytest tests/test_growth_indicators.py -v
```

### Step 3: 创建最小实现

```python
"""Growth Indicators - 成长性指标"""
from typing import List
import pandas as pd

from value_investment.indicators.base import BaseIndicator, IndicatorResult, IndicatorType


class RevenueGrowthIndicator(BaseIndicator):
    """营业收入增长率"""
    name = "revenue_growth"
    needs = ['income']
    description = "营业收入同比增长率"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        income = kwargs.get('income')
        if income is None or income.empty:
            return IndicatorResult(value=0.0, unit="%", description="无数据")
        
        if 'OPERATE_INCOME' not in income.columns:
            return IndicatorResult(value=0.0, unit="%", description="无营业收入数据")
        
        values = income['OPERATE_INCOME'].sort_index(ascending=False)
        if len(values) < 2:
            return IndicatorResult(value=0.0, unit="%", description="数据不足")
        
        latest = float(values.iloc[0])
        previous = float(values.iloc[1])
        
        if previous == 0:
            return IndicatorResult(value=0.0, unit="%", description="基数为0")
        
        growth = (latest - previous) / previous * 100
        return IndicatorResult(value=round(growth, 2), unit="%", description=f"最新同比增长 {growth:.1f}%")

    def get_required_fields(self) -> List[str]:
        return ['OPERATE_INCOME']


class ProfitGrowthIndicator(BaseIndicator):
    """净利润增长率"""
    name = "profit_growth"
    needs = ['income']
    description = "净利润同比增长率"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        income = kwargs.get('income')
        if income is None or income.empty:
            return IndicatorResult(value=0.0, unit="%", description="无数据")
        
        if 'NETPROFIT' not in income.columns:
            return IndicatorResult(value=0.0, unit="%", description="无净利润数据")
        
        values = income['NETPROFIT'].sort_index(ascending=False)
        if len(values) < 2:
            return IndicatorResult(value=0.0, unit="%", description="数据不足")
        
        latest = float(values.iloc[0])
        previous = float(values.iloc[1])
        
        if previous == 0:
            return IndicatorResult(value=0.0, unit="%", description="基数为0")
        
        growth = (latest - previous) / previous * 100
        return IndicatorResult(value=round(growth, 2), unit="%", description=f"最新同比增长 {growth:.1f}%")

    def get_required_fields(self) -> List[str]:
        return ['NETPROFIT']


class AssetGrowthIndicator(BaseIndicator):
    """总资产增长率"""
    name = "asset_growth"
    needs = ['balance']
    description = "总资产同比增长率"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        balance = kwargs.get('balance')
        if balance is None or balance.empty:
            return IndicatorResult(value=0.0, unit="%", description="无数据")
        
        if 'TOTAL_ASSETS' not in balance.columns:
            return IndicatorResult(value=0.0, unit="%", description="无资产数据")
        
        values = balance['TOTAL_ASSETS'].sort_index(ascending=False)
        if len(values) < 2:
            return IndicatorResult(value=0.0, unit="%", description="数据不足")
        
        latest = float(values.iloc[0])
        previous = float(values.iloc[1])
        
        if previous == 0:
            return IndicatorResult(value=0.0, unit="%", description="基数为0")
        
        growth = (latest - previous) / previous * 100
        return IndicatorResult(value=round(growth, 2), unit="%", description=f"最新同比增长 {growth:.1f}%")

    def get_required_fields(self) -> List[str]:
        return ['TOTAL_ASSETS']


class EquityGrowthIndicator(BaseIndicator):
    """净资产增长率"""
    name = "equity_growth"
    needs = ['balance']
    description = "净资产同比增长率"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        balance = kwargs.get('balance')
        if balance is None or balance.empty:
            return IndicatorResult(value=0.0, unit="%", description="无数据")
        
        if 'TOTAL_EQUITY' not in balance.columns:
            return IndicatorResult(value=0.0, unit="%", description="无净资产数据")
        
        values = balance['TOTAL_EQUITY'].sort_index(ascending=False)
        if len(values) < 2:
            return IndicatorResult(value=0.0, unit="%", description="数据不足")
        
        latest = float(values.iloc[0])
        previous = float(values.iloc[1])
        
        if previous == 0:
            return IndicatorResult(value=0.0, unit="%", description="基数为0")
        
        growth = (latest - previous) / previous * 100
        return IndicatorResult(value=round(growth, 2), unit="%", description=f"最新同比增长 {growth:.1f}%")

    def get_required_fields(self) -> List[str]:
        return ['TOTAL_EQUITY']
```

### Step 4: 运行测试确认通过

```bash
cd /root/workspace/skills/value_investment && uv run --directory . pytest tests/test_growth_indicators.py -v
```

### Step 5: 提交

```bash
git add src/value_investment/indicators/growth.py tests/test_growth_indicators.py
git commit -m "feat: 添加成长性指标 (revenue_growth, profit_growth, asset_growth, equity_growth)"
```

---

## Task 2: 创建 safety.py - 安全性指标

**Files:**
- Create: `src/value_investment/indicators/safety.py`
- Modify: `tests/test_safety_indicators.py`

### 测试用例

```python
def test_cash_to_debt_indicator():
    """Cash to debt ratio"""
    indicator = CashToDebtIndicator()
    
    balance = pd.DataFrame({
        'MONETARYFUNDS': [1000.0],
        'SHORT_LOAN': [200.0],
        'LONG_LOAN': [300.0],
    })
    
    result = indicator.calculate(pd.DataFrame(), balance=balance)
    
    assert result.value == 2.0  # 1000 / (200 + 300)


def test_debt_ratio_total_indicator():
    """Total debt to assets ratio"""
    indicator = DebtRatioTotalIndicator()
    
    balance = pd.DataFrame({
        'TOTAL_ASSETS': [2000.0],
        'SHORT_LOAN': [200.0],
        'LONG_LOAN': [300.0],
    })
    
    result = indicator.calculate(pd.DataFrame(), balance=balance)
    
    assert result.value == 25.0  # (200 + 300) / 2000 * 100
```

### 实现

```python
class CashToDebtIndicator(BaseIndicator):
    """货币资金 / 有息负债"""
    name = "cash_to_debt"
    needs = ['balance']
    description = "货币资金/有息负债"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        balance = kwargs.get('balance')
        if balance is None or balance.empty:
            return IndicatorResult(value=0.0, unit="", description="无数据")
        
        cash = float(balance['MONETARYFUNDS'].iloc[0]) if 'MONETARYFUNDS' in balance.columns else 0
        short_loan = float(balance['SHORT_LOAN'].iloc[0]) if 'SHORT_LOAN' in balance.columns else 0
        long_loan = float(balance['LONG_LOAN'].iloc[0]) if 'LONG_LOAN' in balance.columns else 0
        
        total_debt = short_loan + long_loan
        if total_debt == 0:
            return IndicatorResult(value=float('inf'), unit="", description="无有息负债")
        
        ratio = cash / total_debt
        return IndicatorResult(value=round(ratio, 2), unit="", description=f"货币资金是有息负债的 {ratio:.1f} 倍")


class DebtRatioTotalIndicator(BaseIndicator):
    """有息负债 / 总资产"""
    name = "debt_ratio_total"
    needs = ['balance']
    description = "有息负债占总资产比例"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        balance = kwargs.get('balance')
        if balance is None or balance.empty:
            return IndicatorResult(value=0.0, unit="%", description="无数据")
        
        total_assets = float(balance['TOTAL_ASSETS'].iloc[0]) if 'TOTAL_ASSETS' in balance.columns else 0
        short_loan = float(balance['SHORT_LOAN'].iloc[0]) if 'SHORT_LOAN' in balance.columns else 0
        long_loan = float(balance['LONG_LOAN'].iloc[0]) if 'LONG_LOAN' in balance.columns else 0
        
        if total_assets == 0:
            return IndicatorResult(value=0.0, unit="%", description="无资产数据")
        
        ratio = (short_loan + long_loan) / total_assets * 100
        return IndicatorResult(value=round(ratio, 2), unit="%", description=f"有息负债占比 {ratio:.1f}%")
```

---

## Task 3: 补充 efficiency.py - 费用指标

新增 `ExpenseRatioIndicator`, `FeeRateIndicator`, `FixedAssetTurnoverIndicator`

---

## Task 4: 在 Factory 注册新指标

修改 `factory.py`，导入并注册所有新指标

---

## Task 5: 创建 detector.py - 异常信号检测

```python
# src/value_investment/analysis/detector.py

def detect_warnings(indicators: dict) -> tuple[list, list]:
    """检测异常信号"""
    warnings = []
    notes = []
    
    # ROE 检查
    if 'ROE' in indicators:
        roe = indicators['ROE'].value
        if roe < 10:
            warnings.append(f"⚠️ ROE 偏低: {roe:.1f}%")
        elif roe > 20:
            notes.append(f"✅ ROE 优秀: {roe:.1f}%")
    
    # ... 更多检查
    
    return warnings, notes
```

---

## Task 6: 创建 reporter.py - 报告生成器

```python
# src/value_investment/analysis/reporter.py

REPORT_PROMPT = """
你是专业的财报分析师。根据以下数据生成 Markdown 分析报告...

数据: {data_json}
"""

def generate_report_prompt(data: dict) -> str:
    """生成 LLM 提示词"""
    return REPORT_PROMPT.format(data_json=json.dumps(data, ensure_ascii=False))
```

---

## Task 7: 修改 api.py - 扩展 analyze 方法

1. 添加 `report: bool = False` 参数
2. 调用 detector 检测异常信号
3. 返回 warnings 和 notes
4. 如果 report=True，生成 report 字段

---

## Task 8: 集成测试

```bash
# 测试完整流程
uv run --directory . python -m value_investment.cli analyze 600519 -m A -y 5
```

---

## 验收清单

- [ ] `cli indicator revenue_growth -s 600519 -m A` 返回增长率
- [ ] `cli indicator profit_growth -s 600519 -m A` 返回增长率
- [ ] `cli indicator cash_to_debt -s 600519 -m A` 返回比率
- [ ] `cli analyze 600519 -m A -y 5` 输出包含 warnings 和 notes
- [ ] 所有单元测试通过
