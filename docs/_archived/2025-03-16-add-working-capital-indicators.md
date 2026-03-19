# 添加运营资金指标 (Working Capital Indicators)

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 添加 3 个七看八问框架所需的财务指标：working_capital, wc_to_revenue, revenue_per_employee

**Architecture:** 
- 在 CORE_FIELD_MAPPING 中添加缺失的字段映射（contract_assets, contract_liab, prepayment, adv_receipts）
- 在 BalanceSheet 模型中添加对应字段
- 在 efficiency.py 中实现 3 个新指标类
- 在 registry 中注册新指标

**Tech Stack:** Python, pandas, pytest

---

## 前置检查

运行以下命令确认当前系统状态：

```bash
# 检查现有指标
v-invest indicators A | grep -E "working|wc_to|revenue_per"
# 预期：无输出（指标不存在）

# 检查测试能否运行
uv run python -m pytest tests/test_safety_indicators.py -v
# 预期：测试通过
```

---

## Task 1: 添加字段映射 (CORE_FIELD_MAPPING)

**Files:**
- Modify: `src/value_investment/data/mapper.py`

**Step 1: 在 CORE_FIELD_MAPPING 中添加新字段**

在 "资产负债表 (Balance Sheet)" 部分添加以下字段（放在 accounts_receivable 附近）：

```python
"accounts_receivable": {
    "A股": "应收账款",
    "港股": "应收帐款",
    "美股": "accountsReceivable",
},
"contract_assets": {  # 新增
    "A股": "合同资产",
    "港股": "合同资产",
    "美股": "contractAssets",
},
"prepayment": {  # 新增（注意：已有 prepaid_expenses，这是流动资产中的预付款项）
    "A股": "预付款项",
    "港股": "预付款项",
    "美股": "prepayments",
},
"accounts_payable": {
    "A股": "应付账款",
    "港股": "应付帐款",
    "美股": "accountsPayable",
},
"adv_receipts": {  # 新增（预收款项）
    "A股": "预收款项",
    "港股": "预收款项",
    "美股": "advanceReceipts",
},
"contract_liab": {  # 新增（合同负债）
    "A股": "合同负债",
    "港股": "合同负债",
    "美股": "contractLiabilities",
},
```

**注意：** 需要检查 `prepaid_expenses` 和 `prepayment` 的区别：
- `prepaid_expenses` 是长期待摊费用（非流动资产）
- `prepayment` 是预付款项（流动资产）

**Step 2: 验证映射**

运行：
```bash
uv run python -c "from value_investment.data.mapper import CORE_FIELD_MAPPING; print('contract_assets' in CORE_FIELD_MAPPING)"
# 预期：True
```

**Step 3: Commit**

```bash
git add src/value_investment/data/mapper.py
git commit -m "feat: add contract_assets, contract_liab, prepayment, adv_receipts to CORE_FIELD_MAPPING"
```

---

## Task 2: 更新 BalanceSheet 模型

**Files:**
- Modify: `src/value_investment/data/models.py`

**Step 1: 在 BalanceSheet 类中添加新字段**

在现有字段后添加：

```python
# 运营资金相关字段（新增）
contract_assets: float | None = None  # 合同资产
contract_liab: float | None = None  # 合同负债
prepayment: float | None = None  # 预付款项（流动资产）
adv_receipts: float | None = None  # 预收款项
```

**Step 2: 更新 StandardFinancialData**

在 StandardFinancialData 类中也添加这些字段（如果它包含单独的资产负债表字段）。

**Step 3: Commit**

```bash
git add src/value_investment/data/models.py
git commit -m "feat: add working capital fields to BalanceSheet model"
```

---

## Task 3: 实现 WorkingCapitalIndicator

**Files:**
- Create: `tests/test_working_capital_indicators.py`
- Modify: `src/value_investment/indicators/efficiency.py`

**Step 1: 编写测试**

```python
"""Test Working Capital Indicators"""
import pytest
import pandas as pd
from value_investment.indicators.efficiency import (
    WorkingCapitalIndicator,
    WCToRevenueIndicator,
)


def test_working_capital_indicator():
    """Working capital should be calculated correctly
    WC = 应收 + 预付 + 存货 + 合同资产 - (应付 + 预收 + 合同负债)
    """
    indicator = WorkingCapitalIndicator()

    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'ACCOUNTS_RECE': [1000.0],  # 应收账款
        'PREPAYMENT': [200.0],  # 预付款项
        'INVENTORY': [500.0],  # 存货
        'CONTRACT_ASSETS': [100.0],  # 合同资产
        'ACCOUNTS_PAYABLE': [800.0],  # 应付账款
        'ADV_RECEIPTS': [150.0],  # 预收款项
        'CONTRACT_LIAB': [50.0],  # 合同负债
    })

    result = indicator.calculate(balance)

    # WC = 1000 + 200 + 500 + 100 - (800 + 150 + 50) = 1800 - 1000 = 800
    assert result.value == pytest.approx(800.0, 0.01)
    assert result.unit == "元"
    assert "Working Capital" in result.description or "流动资金" in result.description


def test_working_capital_with_missing_fields():
    """Working capital should handle missing fields gracefully"""
    indicator = WorkingCapitalIndicator()

    balance = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'ACCOUNTS_RECE': [1000.0],
        'INVENTORY': [500.0],
        'ACCOUNTS_PAYABLE': [800.0],
        # 其他字段缺失
    })

    result = indicator.calculate(balance)

    # WC = 1000 + 0 + 500 + 0 - (800 + 0 + 0) = 700
    assert result.value == pytest.approx(700.0, 0.01)


def test_working_capital_required_fields():
    """WorkingCapitalIndicator should report required fields"""
    indicator = WorkingCapitalIndicator()
    fields = indicator.get_required_fields()

    assert 'ACCOUNTS_RECE' in fields
    assert 'INVENTORY' in fields
    assert 'ACCOUNTS_PAYABLE' in fields


def test_wc_to_revenue_indicator():
    """WC to revenue ratio should be calculated correctly"""
    indicator = WCToRevenueIndicator()

    data = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'ACCOUNTS_RECE': [1000.0],
        'PREPAYMENT': [200.0],
        'INVENTORY': [500.0],
        'CONTRACT_ASSETS': [100.0],
        'ACCOUNTS_PAYABLE': [800.0],
        'ADV_RECEIPTS': [150.0],
        'CONTRACT_LIAB': [50.0],
        'TOTAL_OPERATE_INCOME': [5000.0],  # 营业收入
    })

    result = indicator.calculate(data)

    # WC = 800, Revenue = 5000
    # WC/Revenue = 800 / 5000 = 0.16
    assert result.value == pytest.approx(0.16, 0.01)
    assert result.unit == "ratio"


def test_wc_to_revenue_zero_revenue():
    """WC to revenue should handle zero revenue gracefully"""
    indicator = WCToRevenueIndicator()

    data = pd.DataFrame({
        'REPORT_DATE': ['2023-12-31'],
        'ACCOUNTS_RECE': [1000.0],
        'INVENTORY': [500.0],
        'ACCOUNTS_PAYABLE': [800.0],
        'TOTAL_OPERATE_INCOME': [0.0],
    })

    result = indicator.calculate(data)

    # Should not crash, return 0 or handle gracefully
    assert result.value >= 0
```

**Step 2: 运行测试确认失败**

```bash
uv run python -m pytest tests/test_working_capital_indicators.py -v
# 预期：ImportError 或 AttributeError（类不存在）
```

**Step 3: 实现 WorkingCapitalIndicator**

在 `src/value_investment/indicators/efficiency.py` 中添加：

```python
class WorkingCapitalIndicator(BaseIndicator):
    """Working Capital = 应收账款 + 预付款项 + 存货 + 合同资产 - (应付账款 + 预收款项 + 合同负债)
    
    反映企业运营资金占用情况，越低说明对上下游议价能力越强
    """

    name = "working_capital"
    description = "Working Capital (流动资金 = 应收+预付+存货+合同资产 - 应付-预收-合同负债)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 流动资产部分
        ar_col = self._find_column(data, ['accounts_receivable', 'ACCOUNTS_RECE'])
        prepay_col = self._find_column(data, ['prepayment', 'PREPAYMENT'])
        inv_col = self._find_column(data, ['inventory', 'INVENTORY'])
        ca_col = self._find_column(data, ['contract_assets', 'CONTRACT_ASSETS'])

        # 流动负债部分
        ap_col = self._find_column(data, ['accounts_payable', 'ACCOUNTS_PAYABLE'])
        adv_col = self._find_column(data, ['adv_receipts', 'ADV_RECEIPTS'])
        cl_col = self._find_column(data, ['contract_liab', 'CONTRACT_LIAB'])

        # 计算各项（缺失则为0）
        ar = data[ar_col] if ar_col else pd.Series(0, index=data.index)
        prepay = data[prepay_col] if prepay_col else pd.Series(0, index=data.index)
        inv = data[inv_col] if inv_col else pd.Series(0, index=data.index)
        ca = data[ca_col] if ca_col else pd.Series(0, index=data.index)

        ap = data[ap_col] if ap_col else pd.Series(0, index=data.index)
        adv = data[adv_col] if adv_col else pd.Series(0, index=data.index)
        cl = data[cl_col] if cl_col else pd.Series(0, index=data.index)

        # 计算流动资金
        wc = (ar + prepay + inv + ca) - (ap + adv + cl)

        return IndicatorResult(
            value=float(wc.mean()) if len(wc) > 0 else 0.0,
            unit="元",
            description="Working Capital (流动资金)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=wc.tolist() if len(wc) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['accounts_receivable', 'prepayment', 'inventory', 'contract_assets',
                'accounts_payable', 'adv_receipts', 'contract_liab']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None


class WCToRevenueIndicator(BaseIndicator):
    """WC to Revenue Ratio = Working Capital / Operating Revenue
    
    反映1元收入占用的流动资金，越低说明运营效率越高
    """

    name = "wc_to_revenue"
    description = "WC to Revenue Ratio (1元收入占用流动资金)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 先计算 WC
        ar_col = self._find_column(data, ['accounts_receivable', 'ACCOUNTS_RECE'])
        prepay_col = self._find_column(data, ['prepayment', 'PREPAYMENT'])
        inv_col = self._find_column(data, ['inventory', 'INVENTORY'])
        ca_col = self._find_column(data, ['contract_assets', 'CONTRACT_ASSETS'])
        ap_col = self._find_column(data, ['accounts_payable', 'ACCOUNTS_PAYABLE'])
        adv_col = self._find_column(data, ['adv_receipts', 'ADV_RECEIPTS'])
        cl_col = self._find_column(data, ['contract_liab', 'CONTRACT_LIAB'])
        revenue_col = self._find_column(data, ['operating_revenue', 'OPERATE_INCOME', 'TOTAL_OPERATE_INCOME'])

        # 计算 WC
        ar = data[ar_col] if ar_col else pd.Series(0, index=data.index)
        prepay = data[prepay_col] if prepay_col else pd.Series(0, index=data.index)
        inv = data[inv_col] if inv_col else pd.Series(0, index=data.index)
        ca = data[ca_col] if ca_col else pd.Series(0, index=data.index)
        ap = data[ap_col] if ap_col else pd.Series(0, index=data.index)
        adv = data[adv_col] if adv_col else pd.Series(0, index=data.index)
        cl = data[cl_col] if cl_col else pd.Series(0, index=data.index)
        
        wc = (ar + prepay + inv + ca) - (ap + adv + cl)
        
        # 获取营业收入
        revenue = data[revenue_col] if revenue_col else pd.Series([1], index=data.index)
        
        # 计算比率
        ratio = wc / revenue.replace(0, 1)

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="ratio",
            description="WC to Revenue Ratio (1元收入占用流动资金)",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['accounts_receivable', 'prepayment', 'inventory', 'contract_assets',
                'accounts_payable', 'adv_receipts', 'contract_liab', 'operating_revenue']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
```

**Step 4: 运行测试确认通过**

```bash
uv run python -m pytest tests/test_working_capital_indicators.py::test_working_capital_indicator -v
uv run python -m pytest tests/test_working_capital_indicators.py::test_wc_to_revenue_indicator -v
# 预期：测试通过
```

**Step 5: Commit**

```bash
git add tests/test_working_capital_indicators.py src/value_investment/indicators/efficiency.py
git commit -m "feat: add working_capital and wc_to_revenue indicators"
```

---

## Task 4: 实现 RevenuePerEmployeeIndicator (标记为需要外部数据)

**Files:**
- Modify: `src/value_investment/indicators/efficiency.py`

**说明：** revenue_per_employee 需要员工人数数据，该数据不在标准财务报表中，需要从外部获取（如 tushare, web search 等）。

**Step 1: 实现指标（带数据缺失提示）**

```python
class RevenuePerEmployeeIndicator(BaseIndicator):
    """Revenue per Employee = Operating Revenue / Employee Count
    
    反映人均产出效率。注意：员工人数需要从外部数据源获取（如tushare公司基本信息接口）。
    
    数据来源参考：
    - tushare: stock_company接口的employee字段
    - 同花顺/东方财富F10公司概况
    - 年报附注"公司员工情况"
    """

    name = "revenue_per_employee"
    description = "Revenue per Employee (人均收入，需要员工人数外部数据)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        revenue_col = self._find_column(data, ['operating_revenue', 'OPERATE_INCOME', 'TOTAL_OPERATE_INCOME'])
        
        # 尝试从 kwargs 获取员工人数
        employee_count = kwargs.get('employee_count', None)
        
        if employee_count is None:
            # 尝试从数据列中获取
            emp_col = self._find_column(data, ['employee_count', 'EMPLOYEE_COUNT'])
            if emp_col:
                employee_count = data[emp_col].iloc[0]
        
        revenue = data[revenue_col] if revenue_col else pd.Series([0], index=data.index)
        
        if employee_count is None or employee_count == 0:
            # 返回提示信息
            return IndicatorResult(
                value=0.0,
                unit="元/人",
                description="Revenue per Employee (需要员工人数数据 - 可从tushare或web搜索获取)",
                years=data['year'].tolist() if 'year' in data.columns else [],
                values=[0.0] * len(revenue)
            )
        
        # 计算人均收入
        ratio = revenue / employee_count

        return IndicatorResult(
            value=float(ratio.mean()) if len(ratio) > 0 else 0.0,
            unit="元/人",
            description=f"Revenue per Employee (员工数: {employee_count})",
            years=data['year'].tolist() if 'year' in data.columns else [],
            values=ratio.tolist() if len(ratio) > 0 else []
        )

    def get_required_fields(self) -> list[str]:
        return ['operating_revenue']

    def _find_column(self, df: pd.DataFrame, candidates: list[str]) -> str:
        for col in candidates:
            if col in df.columns:
                return col
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
        return None
```

**Step 2: Commit**

```bash
git add src/value_investment/indicators/efficiency.py
git commit -m "feat: add revenue_per_employee indicator (requires external employee data)"
```

---

## Task 5: 注册新指标

**Files:**
- Modify: `src/value_investment/indicators/registry.py` 或 `src/value_investment/indicators/factory.py`

**Step 1: 查找注册位置**

```bash
grep -r "FixedAssetTurnoverIndicator\|PayableTurnoverIndicator" /Users/yapex/workspace/value_investment/src/value_investment/indicators/
```

**Step 2: 添加注册代码**

在注册其他 efficiency 指标的位置添加：

```python
from value_investment.indicators.efficiency import (
    WorkingCapitalIndicator,
    WCToRevenueIndicator,
    RevenuePerEmployeeIndicator,
)

# 在注册代码中添加
registry.register(WorkingCapitalIndicator())
registry.register(WCToRevenueIndicator())
registry.register(RevenuePerEmployeeIndicator())
```

**Step 3: 验证注册**

```bash
v-invest indicators A | grep -E "working_capital|wc_to_revenue|revenue_per_employee"
# 预期：显示3个新指标
```

**Step 4: Commit**

```bash
git add src/value_investment/indicators/
git commit -m "feat: register working capital indicators"
```

---

## Task 6: 更新七看八问框架文档

**Files:**
- Modify: `src/value_investment/.pi/agent/skills/v-invest/REFERENCES/financial_analysis_7n8/7_looks_financial.md`

**Step 1: 更新"看投入产出"部分**

修改第6步"看投入产出"的数据获取命令：

```markdown
### 数据获取

```bash
# 周转效率指标（包含新增指标）
v-invest indicator "asset_turnover,inventory_turnover,receivables_turnover,working_capital,wc_to_revenue" -s {股票代码} -m {市场} -y 5

# 注意：revenue_per_employee 需要员工人数数据，可通过以下方式获取：
# 1. tushare stock_company 接口
# 2. web search "{公司名} 员工人数"
```
```

**Step 2: 添加指标说明**

在分析要点表格后添加：

```markdown
### 指标说明

| 指标 | 计算公式 | 数据来源 | 说明 |
|------|---------|---------|------|
| working_capital | 应收+预付+存货+合同资产-(应付+预收+合同负债) | 资产负债表 | 自动计算 |
| wc_to_revenue | WC / 营业收入 | 资产负债表+利润表 | 自动计算 |
| revenue_per_employee | 营业收入 / 员工数 | 利润表+外部数据 | 需手动提供员工数 |

**注意：** revenue_per_employee 的员工人数不在标准财务报表中，可从以下渠道获取：
- tushare.pro stock_company 接口
- 同花顺/东方财富 F10 公司概况
- 年报附注"公司员工情况"
- web search "{公司名} 员工人数"
```

**Step 3: Commit**

```bash
git add src/value_investment/.pi/agent/skills/v-invest/REFERENCES/
git commit -m "docs: update 7_looks_financial.md with working capital indicators"
```

---

## Task 7: 集成测试

**Files:**
- Create: `tests/test_integration_working_capital.py`

**Step 1: 编写集成测试**

```python
"""Integration test for working capital indicators with real data"""
import pytest
from value_investment import ValueInvestment


def test_working_capital_with_real_data():
    """Test working capital calculation with real stock data"""
    vi = ValueInvestment(market='A')
    
    # 获取贵州茅台数据
    result = vi.indicator('working_capital', stock_code='600519', years=3)
    
    assert result is not None
    assert result.value != 0  # 茅台应该有正数的流动资金
    print(f"茅台 Working Capital: {result.value}")


def test_wc_to_revenue_with_real_data():
    """Test WC to revenue ratio with real stock data"""
    vi = ValueInvestment(market='A')
    
    result = vi.indicator('wc_to_revenue', stock_code='600519', years=3)
    
    assert result is not None
    assert result.value >= 0
    print(f"茅台 WC/Revenue: {result.value}")


def test_revenue_per_employee_needs_external_data():
    """Test that revenue_per_employee indicates need for external data"""
    vi = ValueInvestment(market='A')
    
    result = vi.indicator('revenue_per_employee', stock_code='600519', years=1)
    
    assert result is not None
    # 没有员工数据时应该返回提示
    assert "需要" in result.description or "员工" in result.description
```

**Step 2: 运行集成测试**

```bash
uv run python -m pytest tests/test_integration_working_capital.py -v -s
# 预期：前两个测试通过，第三个测试显示提示信息
```

**Step 3: Commit**

```bash
git add tests/test_integration_working_capital.py
git commit -m "test: add integration tests for working capital indicators"
```

---

## 完成验证

运行以下命令验证所有功能：

```bash
# 1. 单元测试
uv run python -m pytest tests/test_working_capital_indicators.py -v

# 2. 集成测试
uv run python -m pytest tests/test_integration_working_capital.py -v

# 3. 指标列表检查
v-invest indicators A | grep -E "working_capital|wc_to_revenue|revenue_per_employee"

# 4. 实际查询测试
v-invest indicator working_capital -s 600519 -m A -y 3
v-invest indicator wc_to_revenue -s 600519 -m A -y 3
```

---

## 后续优化（可选）

1. **添加员工人数数据源**：
   - 集成 tushare.pro stock_company 接口
   - 或添加 web scraping 获取员工数据

2. **添加更多相关指标**：
   - `cash_conversion_cycle` (现金转换周期)
   - `working_capital_turnover` (流动资金周转率)

3. **行业对比**：
   - 添加同行业公司 working_capital 对比功能

