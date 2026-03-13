---
name: develop-indicator
description: 开发新的财务指标，用于价值投资分析。使用场景：需要添加新的财务指标（如ROE、ROIC、毛利率等）到项目中。
---

# 开发新财务指标

本指南介绍如何在 value_investment 项目中开发一个新的财务指标。

## 指标类型

项目中有两种指标类型：

| 类型 | 说明 | 例子 |
|------|------|------|
| RAW | 从数据源直接获取 | `roe` (A 股从 Tushare 获取) |
| CALCULATED | 需要自行计算 | 港股 ROE、A 股 ROIC |

---

## 开发流程

### 1. 确定指标需求

明确以下问题：
- 指标名称（如 ROE、ROIC、毛利率）
- 指标公式
- 适用市场（A 股/港股/美股）
- 需要哪些字段作为输入

### 2. A 股指标：使用现有框架

A 股指标使用 `BaseIndicator` 类，参考：

```
src/value_investment/indicators/growth.py     # ROIC、CAGR 等
src/value_investment/indicators/profitability.py  # 利润率指标
```

示例结构：
```python
class ROEIndicator(BaseIndicator):
    name = "ROE"
    description = "Return on Equity (净资产收益率)"
    type = IndicatorType.CALCULATED

    def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
        # 使用 _find_column 查找字段
        net_profit_col = self._find_column(data, ['net_profit', 'parent_net_profit'])
        equity_col = self._find_column(data, ['total_equity'])

        # 计算
        roe = data[net_profit_col] / data[equity_col] * 100
        ...

        return IndicatorResult(value=..., unit='%', ...)
```

### 3. 港股指标：从三表计算

港股数据源不支持多年历史财务指标，需要**从三表自行计算**。

#### 3.1 添加计算函数

在 `src/value_investment/indicators/hk.py` 中添加函数：

```python
def calculate_hk_指标名(income: pd.DataFrame, balance: pd.DataFrame) -> pd.DataFrame:
    """计算港股指标

    Args:
        income: 利润表 DataFrame
        balance: 资产负债表 DataFrame

    Returns:
        包含 year 和 指标名 列的 DataFrame
    """
    # 1. 合并数据
    merged = income[['year', '净利润字段']].merge(
        balance[['year', '权益字段']],
        on='year', how='inner'
    )

    # 2. 计算指标（使用向量化操作）
    result = np.where(
        (merged['权益字段'] != 0) & (merged['权益字段'].notna()),
        merged['净利润字段'] / merged['权益字段'] * 100,
        np.nan
    )

    return pd.DataFrame({'year': merged['year'], '指标名': result})
```

#### 3.2 字段映射参考

港股字段名与 A 股不同：

| A 股字段 | 港股字段 |
|---------|---------|
| `net_profit` | `股东应占溢利` |
| `total_equity` | `股东权益` |
| `total_revenue` | `营业额` |
| `gross_profit` | `gross_profit` |
| `interest_expense` | `融资成本` |
| `short_term_debt` | `短期贷款` |
| `long_term_debt` | `长期贷款` |

#### 3.3 修改 Scanner

在 `src/value_investment/scanner/scanner.py` 的 `_get_hk_financial_data` 方法中：

1. 导入计算函数
2. 在循环中调用计算函数
3. 将计算结果添加到返回数据中

```python
from value_investment.indicators.hk import calculate_hk_指标名

# 在 _get_hk_financial_data 中
if '指标名' in [f.lower() for f in fields]:
    indicator_df = calculate_hk_指标名(income, balance)
    indicator_value = indicator_df[indicator_df['year'] == year]['指标名'].values
    if len(indicator_value) > 0:
        row_data['指标名'] = indicator_value[0]
```

---

## 实战案例：港股 ROE 指标开发

### 步骤 1：编写测试

创建 `tests/test_hk_indicators.py`：

```python
import pytest
import pandas as pd
from value_investment.indicators.hk import calculate_hk_roe

def test_calculate_hk_roe_basic():
    income = pd.DataFrame({
        'year': [2024, 2023],
        '股东应占溢利': [1000, 900],
    })
    balance = pd.DataFrame({
        'year': [2024, 2023],
        '股东权益': [10000, 9000],
    })

    result = calculate_hk_roe(income, balance)
    assert 'roe' in result.columns
    assert result['roe'].tolist() == [10.0, 10.0]
```

### 步骤 2：实现计算函数

在 `indicators/hk.py` 中添加函数（参考现有函数）。

### 步骤 3：集成到 Scanner

修改 `scanner.py` 的 `_get_hk_financial_data` 方法。

### 步骤 4：测试

```bash
uv run python -c "
from value_investment.scanner import Scanner
scanner = Scanner(market='HK')
data = scanner.get_financial_data(['00700'], ['roe'], years=5)
print(data)
"
```

---

## 注意事项

1. **使用向量化操作**：避免使用 `apply`，使用 `np.where` 或 `pandas` 向量化操作
2. **处理除零**：使用 `np.where` 或 `data.replace(0, 1)` 避免除零错误
3. **缓存**：Scanner 已内置缓存，不需要手动处理
4. **字段兼容**：A 股和港股字段名不同，需要分别处理
