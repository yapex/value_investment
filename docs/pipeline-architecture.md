# Pipeline 架构速查

> 面向 Agent 的精简指南，快速上手 Pipeline 开发。

---

## 1. 核心架构

```
用户请求字段
    ↓
PipelineAPI.get_data(symbol, fields)
    ↓
MessageBus.process(message)  ← 9 Handler 并行处理
    ↓
Calculator 计算派生字段
    ↓
返回结果
```

**9 Handler 矩阵** (3 市场 × 3 数据类型):

| 市场 | 财务报表 | 财务指标 | 市值数据 |
|-----|---------|---------|---------|
| A股 | AStatement | AIndicator | AMarket |
| 港股 | HKStatement | HKIndicator | HKMarket |
| 美股 | USStatement | USIndicator | USMarket |

---

## 2. 新增字段

### 2.1 原始字段（从数据源获取）

1. **定义字段**: `src/value_investment/pipeline/fields.py`
   ```python
   class IFRSFields:
       NEW_FIELD = "new_field"
   ```

2. **添加映射**: `src/value_investment/data/mapper.py`
   ```python
   CORE_FIELD_MAPPING = {
       "new_field": {
           "A股": "字段名",
           "港股": "字段名",
           "美股": "fieldName",
       }
   }
   ```

3. **Handler 支持**: 在对应 Handler 的字段集合中添加
   ```python
   # AStockStatementHandler
   A_STOCK_STATEMENT_FIELDS = {..., IFRSFields.NEW_FIELD}
   ```

### 2.2 派生字段（通过计算）

**三步完成**:

```python
# 1. 创建 Calculator 文件
# src/value_investment/pipeline/calculators/xxx.py

from value_investment.pipeline.calculators import calculator
from value_investment.pipeline.fields import IFRSFields

@calculator  # ← 必须！
class XXXCalculator:
    name = IFRSFields.XXX
    required_fields = {
        IFRSFields.FIELD_A,
        IFRSFields.FIELD_B,
    }
    
    def calculate(self, results):
        field_a = results.get(IFRSFields.FIELD_A, {})
        field_b = results.get(IFRSFields.FIELD_B, {})
        return {year: field_a.get(year, 0) / field_b.get(year, 1)
                for year in field_a}
```

```bash
# 2. 运行测试自动验证依赖链
uv run python -m pytest tests/pipeline/test_validator.py -v

# 3. 完成！无需手动注册
```

---

## 3. 关键文件速查

| 文件 | 用途 |
|-----|------|
| `pipeline/fields.py` | 定义标准字段 `IFRSFields` |
| `data/mapper.py` | 字段映射 `CORE_FIELD_MAPPING` |
| `pipeline/calculators/*.py` | 派生字段计算器 |
| `pipeline/handlers/*_handler.py` | 9 个 Handler 实现 |
| `pipeline/container.py` | 依赖注入容器，注册 Handler |
| `tests/pipeline/test_validator.py` | 自动验证依赖链 |

---

## 4. 常见操作

### 添加新 Calculator
```bash
# 创建文件 → 加 @calculator → 运行测试
uv run python -m pytest tests/pipeline/test_validator.py
```

### 验证依赖链
```bash
# 检查所有 Calculator 的依赖字段是否有 Handler 支持
uv run python -m pytest tests/pipeline/test_validator.py -v
```

### 运行测试
```bash
# 全部测试
uv run python -m pytest tests/pipeline/ -v

# 单个 Calculator
uv run python -m pytest tests/pipeline/test_xxx_calculator.py -v
```

---

## 5. 注意事项

1. **必须加 `@calculator`** - 否则 Calculator 不会被注册
2. **依赖链自动验证** - 测试失败会提示缺少的 Handler
3. **无需手动注册** - `@calculator` 自动完成
4. **字段命名** - 统一使用 `snake_case`

---

## 附录：完整字段列表

```python
# 资产负债表
total_assets, total_liabilities, total_equity
current_assets, current_liabilities
cash_and_equivalents, inventory
accounts_receivable, accounts_payable

# 利润表
total_revenue, net_profit, operating_profit
gross_profit, operating_cost

# 现金流量表
operating_cash_flow, investing_cash_flow
financing_cash_flow, capital_expenditure

# 指标
roe, roa, gross_margin, net_profit_margin
current_ratio, quick_ratio, debt_ratio
asset_turnover, inventory_turnover, receivable_turnover

# 市场数据
pe_ratio, pb_ratio, market_cap
basic_eps, diluted_eps, book_value_per_share
```
