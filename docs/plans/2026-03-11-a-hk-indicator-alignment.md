# A股与港股财务指标对齐实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 分三个阶段对齐A股(104字段)和港股(17字段)的财务指标，通过TDD驱动开发，确保字段映射完整性和数据准确性。

**Architecture:** 
- 第一阶段：核心指标对齐（利润表、资产负债表、现金流量表、关键比率）- 8个字段
- 第二阶段：扩展指标对齐（每股指标、营运能力、估值指标）- 10个字段  
- 第三阶段：特色指标对齐（A股特有、港股特有）- 6个字段

**Tech Stack:** Python, pytest, pandas, akshare, yfinance

**当前状态:**
- A股: 104个财务指标字段可用
- 港股: 17个财务指标字段可用
- 目标: 至少对齐24个核心字段，实现跨市场可比性

---

## 第一阶段：核心指标对齐（最重要）

### Task 1: 对齐利润表核心字段

**Files:**
- Modify: `src/value_investment/data/mapper.py:10-50` (CORE_FIELD_MAPPING)
- Test: `tests/test_field_mapping.py`

**Step 1: 写测试验证利润表字段映射**

```python
# tests/test_field_mapping.py 新增
def test_hk_total_revenue_mapping():
    """港股 total_revenue 字段应映射正确"""
    from value_investment.data.mapper import DataMapper
    result = DataMapper.get_market_field("total_revenue", "港股")
    assert result == "total_revenue"  # 港股返回标准化字段名

def test_hk_net_profit_mapping():
    """港股 net_profit 字段应映射正确"""
    from value_investment.data.mapper import DataMapper
    result = DataMapper.get_market_field("net_profit", "港股")
    assert result == "net_profit"
```

**Step 2: 运行测试确认失败**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_total_revenue_mapping -v`
Expected: FAIL - "AssertionError: assert '收益' == 'total_revenue'"

**Step 3: 写最小实现**

修改 mapper.py 中的 CORE_FIELD_MAPPING，确保港股字段正确映射：
```python
"total_revenue": {
    "A股": "营业总收入",
    "港股": "total_revenue",  # 改为标准化字段名
    "美股": "totalRevenue",
},
```

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_total_revenue_mapping -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/test_field_mapping.py src/value_investment/data/mapper.py
git commit -m "test: 添加港股利润表字段映射测试"
```

---

### Task 2: 对齐资产负债表核心字段

**Files:**
- Modify: `src/value_investment/data/mapper.py:50-100`

**Step 1: 写测试**

```python
def test_hk_balance_sheet_fields():
    """港股资产负债表核心字段映射"""
    from value_investment.data.mapper import DataMapper
    
    fields = ["total_assets", "total_equity", "total_liabilities"]
    for field in fields:
        result = DataMapper.get_market_field(field, "港股")
        assert result == field  # 应返回标准化字段名
```

**Step 2: 运行测试确认失败**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_balance_sheet_fields -v`
Expected: FAIL

**Step 3: 写最小实现**

在 CORE_FIELD_MAPPING 中添加港股字段映射：
```python
"total_assets": {
    "A股": "资产总计",
    "港股": "total_assets",  # 使用标准化字段名
    "美股": "totalAssets",
},
```

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_balance_sheet_fields -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/data/mapper.py
git commit -m "feat: 添加港股资产负债表核心字段映射"
```

---

### Task 3: 对齐现金流量表核心字段

**Files:**
- Modify: `src/value_investment/data/mapper.py:100-120`

**Step 1: 写测试**

```python
def test_hk_cashflow_fields():
    """港股现金流量表核心字段映射"""
    from value_investment.data.mapper import DataMapper
    
    fields = ["operating_cash_flow", "investing_cash_flow", "financing_cash_flow"]
    for field in fields:
        result = DataMapper.get_market_field(field, "港股")
        assert result == field
```

**Step 2: 运行测试**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_cashflow_fields -v`

**Step 3: 实现映射**

在 CORE_FIELD_MAPPING 中添加港股字段映射

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_cashflow_fields -v`

**Step 5: Commit**

```bash
git commit -m "feat: 添加港股现金流量表核心字段映射"
```

---

### Task 4: 对齐关键比率（ROE/ROA/净利率）

**Files:**
- Modify: `src/value_investment/data/mapper.py:120-180`

**Step 1: 写测试**

```python
def test_hk_ratio_fields():
    """港股关键比率字段映射"""
    from value_investment.data.mapper import DataMapper
    
    fields = ["roe", "roa", "net_profit_margin"]
    for field in fields:
        result = DataMapper.get_market_field(field, "港股")
        assert result == field
```

**Step 2: 运行测试**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_ratio_fields -v`

**Step 3: 实现映射**

添加 ROE, ROA, net_profit_margin 到 CORE_FIELD_MAPPING

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_ratio_fields -v`

**Step 5: Commit**

```bash
git commit -m "feat: 添加港股关键比率字段映射"
```

---

## 第二阶段：扩展指标对齐（中等重要）

### Task 5: 对齐每股指标

**Files:**
- Modify: `src/value_investment/data/mapper.py:180-220`

**Step 1: 写测试**

```python
def test_hk_per_share_fields():
    """港股每股指标字段映射"""
    from value_investment.data.mapper import DataMapper
    
    fields = ["basic_eps", "book_value_per_share", "operating_cash_flow_per_share"]
    for field in fields:
        result = DataMapper.get_market_field(field, "港股")
        assert result == field
```

**Step 2: 运行测试**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_per_share_fields -v`

**Step 3: 实现映射**

添加 basic_eps, book_value_per_share 等到 CORE_FIELD_MAPPING

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_per_share_fields -v`

**Step 5: Commit**

```bash
git commit -m "feat: 添加港股每股指标字段映射"
```

---

### Task 6: 对齐营运能力指标

**Files:**
- Modify: `src/value_investment/data/mapper.py:220-260`

**Step 1: 写测试**

```python
def test_hk_operating_fields():
    """港股营运能力指标字段映射"""
    from value_investment.data.mapper import DataMapper
    
    fields = ["current_ratio", "quick_ratio", "cash_ratio", "debt_ratio"]
    for field in fields:
        result = DataMapper.get_market_field(field, "港股")
        assert result == field
```

**Step 2: 运行测试**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_operating_fields -v`

**Step 3: 实现映射**

添加 current_ratio, quick_ratio, cash_ratio, debt_ratio 到映射

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_operating_fields -v`

**Step 5: Commit**

```bash
git commit -m "feat: 添加港股营运能力指标字段映射"
```

---

### Task 7: 对齐估值指标（PE/PB）

**Files:**
- Modify: `src/value_investment/data/mapper.py:260-300`

**Step 1: 写测试**

```python
def test_hk_valuation_fields():
    """港股估值指标字段映射"""
    from value_investment.data.mapper import DataMapper
    
    fields = ["pe_ratio", "pb_ratio"]
    for field in fields:
        result = DataMapper.get_market_field(field, "港股")
        assert result == field
```

**Step 2: 运行测试**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_valuation_fields -v`

**Step 3: 实现映射**

添加 pe_ratio, pb_ratio 到 CORE_FIELD_MAPPING

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_valuation_fields -v`

**Step 5: Commit**

```bash
git commit -m "feat: 添加港股估值指标字段映射"
```

---

## 第三阶段：特色指标对齐（完善）

### Task 8: 对齐港股特有指标

**Files:**
- Modify: `src/value_investment/data/mapper.py:300-350`
- Test: `tests/test_field_mapping.py`

**Step 1: 写测试**

```python
def test_hk_specific_fields():
    """港股特有指标字段映射"""
    from value_investment.data.mapper import DataMapper
    
    fields = [
        "hk_dividend_yield_ttm",
        "hk_dividend_payout_ratio", 
        "hk_dividend_per_share",
        "hk_market_cap",
        "hk_legal_shares",
        "hk_total_revenue_growth_qoq",
        "hk_net_profit_growth_qoq",
    ]
    for field in fields:
        result = DataMapper.get_market_field(field, "港股")
        assert result == field
```

**Step 2: 运行测试**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_specific_fields -v`

**Step 3: 实现映射**

添加港股特有指标到 CORE_FIELD_MAPPING

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_field_mapping.py::test_hk_specific_fields -v`

**Step 5: Commit**

```bash
git commit -m "feat: 添加港股特有指标字段映射"
```

---

### Task 9: 对齐A股特有指标（可选）

**Files:**
- Modify: `src/value_investment/data/mapper.py:350-400`

**Step 1: 写测试**

```python
def test_a_share_specific_fields():
    """A股特有指标字段映射"""
    from value_investment.data.mapper import DataMapper
    
    # 港股没有的A股指标应该能正确返回
    fields = ["deducted_net_profit", "ebit", "ebitda"]
    for field in fields:
        result = DataMapper.get_market_field(field, "港股")
        assert result is None or result == field  # 港股没有返回None或原值
```

**Step 2: 运行测试**

Run: `uv run pytest tests/test_field_mapping.py::test_a_share_specific_fields -v`

**Step 3: 实现处理**

在 DataMapper 中添加对不存在字段的处理逻辑

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_field_mapping.py::test_a_share_specific_fields -v`

**Step 5: Commit**

```bash
git commit -m "feat: 处理A股特有指标的跨市场映射"
```

---

## 集成测试与验证

### Task 10: 端到端集成测试

**Files:**
- Test: `tests/test_datamapper_activated.py`

**Step 1: 写集成测试**

```python
def test_cross_market_financial_indicator():
    """跨市场财务指标一致性测试"""
    from value_investment.api import ValueInvestment
    
    # A股茅台
    vi_a = ValueInvestment(market="A")
    data_a = vi_a.get_financial_indicator("600519")
    
    # 港股腾讯  
    vi_hk = ValueInvestment(market="HK")
    data_hk = vi_hk.get_financial_indicator("00700")
    
    # 验证标准化字段存在
    standard_fields = ["roe", "net_profit_margin", "basic_eps"]
    for field in standard_fields:
        assert field in data_a.columns, f"A股缺少字段: {field}"
        assert field in data_hk.columns, f"港股缺少字段: {field}"
```

**Step 2: 运行测试**

Run: `uv run pytest tests/test_datamapper_activated.py::test_cross_market_financial_indicator -v`

**Step 3: 调试与修复**

如果失败，修复字段映射

**Step 4: 运行测试确认通过**

Run: `uv run pytest tests/test_datamapper_activated.py::test_cross_market_financial_indicator -v`

**Step 5: Commit**

```bash
git add tests/test_datamapper_activated.py
git commit -m "test: 添加跨市场财务指标集成测试"
git push origin main
```

---

## 总结

| 阶段 | 任务数 | 核心字段 | 状态 |
|------|--------|----------|------|
| 第一阶段 | 4 | 利润表+资产负债表+现金流量表+关键比率 | 待开始 |
| 第二阶段 | 3 | 每股指标+营运能力+估值指标 | 待开始 |
| 第三阶段 | 2 | 港股特有+A股特有 | 待开始 |
| 集成测试 | 1 | 端到端验证 | 待开始 |

**预期结果:**
- A股: 104个字段保持不变
- 港股: 从17个字段扩展到至少24个核心字段
- 跨市场分析: 可以使用标准化字段名进行对比
