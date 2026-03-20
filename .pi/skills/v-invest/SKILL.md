---
name: v-invest
description: 价值投资 CLI - 查询 A股/港股/美股财务数据、指标、自定义计算器
---

# v-invest CLI

## 命令速查

| 命令 | 说明 |
|------|------|
| `v-invest query <股票> -r <字段>` | 查询数据 |
| `v-invest validate <股票> -r <字段>` | 验证配置 |
| `v-invest fields` | 查看可用字段 |
| `v-invest indicators` | 查看可用指标 |

## 市场识别

| 市场 | 代码格式 | 示例 |
|-----|---------|------|
| A 股 | 6 位 (0/3/6 开头) | 600519 |
| 港股 | 5 位数字 | 00700 |
| 美股 | 字母 | AAPL |

---

## query 用法

```bash
v-invest query <股票> -r <字段1,字段2> [-y 年数] [-m 市场]
```

**示例：**
```bash
v-invest query 600519 -r "roe,gross_margin,debt_ratio" -y 10
v-invest query 00700 -r "roe,revenue_cagr_10y" -m HK
```

## 常用字段

| 字段 | 说明 | 字段 | 说明 |
|------|------|------|------|
| total_revenue | 营收 | net_profit | 净利润 |
| total_assets | 总资产 | total_liabilities | 总负债 |
| total_equity | 股东权益 | cash_and_equivalents | 货币资金 |
| roe | 净资产收益率 | gross_margin | 毛利率 |
| debt_ratio | 资产负债率 | current_ratio | 流动比率 |

**全部字段：** `v-invest fields`

## 常用指标

| 指标 | 说明 | 指标 | 说明 |
|------|------|------|------|
| revenue_cagr_10y | 营收 10 年 CAGR | net_profit_cagr_10y | 净利润 10 年 CAGR |
| roe_volatility | ROE 波动率 | gross_margin_volatility | 毛利率波动率 |
| goodwill_to_net_assets_ratio | 商誉/净资产 | interest_coverage_ratio | 利息保障倍数 |

**全部指标：** `v-invest indicators`

## 自定义计算器

**脚本（`calc_xxx.py`）：**
```python
name = "xxx"
required_fields = ["field_a", "field_b"]

def calculate(results):
    out = {}
    for year, data in results.items():
        a, b = data.get("field_a"), data.get("field_b")
        out[year] = a / b if a and b else None
    return out
```

**使用：** `v-invest query 600519 -r "xxx,roe" -c ./calc_xxx.py`

## 常见错误

| 错误 | 解决 |
|------|------|
| `Unknown fields` | 拼写检查：`v-invest fields` |
| `Missing fields` | 该市场暂无此字段 |
