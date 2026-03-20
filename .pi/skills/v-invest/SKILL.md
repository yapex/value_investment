---
name: v-invest
description: 价值投资分析 CLI 工具 - 查询 A股/港股/美股财务数据、指标计算、数据验证。**必须先读此文档！**
---

# v-invest CLI 工具

> **框架入口**：所有财务数据查询必须通过此 skill
>
> **核心命令**：`v-invest query` / `v-invest fields` / `v-invest indicators`

---

## 命令速查

| 需求 | 命令 |
|------|------|
| 查询财务数据 | `v-invest query <股票> -r <字段> -y <年数>` |
| 查询指标 | 同上，用指标名作为字段 |
| 验证配置 | `v-invest validate <股票> -r <字段>` |
| 查看可用字段 | `v-invest fields` |
| 查看可用指标 | `v-invest indicators` |

---

## 市场识别

| 市场 | 代码格式 | 示例 | 自动识别 |
|-----|---------|------|---------|
| A 股 | 6 位数字 (0/3/6 开头) | 600519, 000001 | ✅ |
| 港股 | 5 位数字 | 00700, 09988 | ✅ |
| 美股 | 字母代码 | AAPL, TSLA | ✅ |

---

## 模块一：数据查询 (核心)

### 命令格式

```bash
v-invest query <股票> -r <字段1,字段2,...> -e <结束年> -y <年数> -m <市场>
```

### 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|:----:|------|------|
| `<股票>` | ✅ | 股票代码 | 600519, 00700, AAPL |
| `-r / --requires` | ✅ | 字段列表（逗号分隔） | `roe,net_profit,gross_margin` |
| `-e / --end` | ❌ | 结束年份，默认 2024 | `2024`, `20231231` |
| `-y / --years` | ❌ | 查询年数，默认 10 | `10`, `5`, `1` |
| `-m / --market` | ❌ | 市场，不指定则自动识别 | `A`, `HK`, `US` |
| `-f / --format` | ❌ | 输出格式，默认 markdown | `markdown`, `json`, `plain` |

### 示例

```bash
# A 股：茅台 10 年财务数据
v-invest query 600519 -r "roe,gross_margin,net_profit_margin,debt_ratio,current_ratio" -y 10

# 港股：腾讯 10 年指标（自动识别港股）
v-invest query 00700 -r "roe,gross_margin,revenue_cagr_10y,roe_volatility" -y 10

# 美股：苹果 5 年数据（指定市场）
v-invest query AAPL -r "total_revenue,net_profit,operating_cash_flow" -y 5 -m US

# 查询特定年份（最近 3 年）
v-invest query 600519 -r "roe,net_profit" -e 2024 -y 3
```

### 输出格式

默认 markdown 表格：
```
| field | 2024 | 2023 | 2022 | 2021 | 2020 |
|-------|------|------|------|------|------|
| roe   | 0.32 | 0.30 | 0.29 | 0.27 | 0.26 |
```

---

## 模块二：验证配置

### 命令格式

```bash
v-invest validate <股票> -r <字段>
```

### 用途

- **执行前验证**：查询数据前先用此命令验证字段是否有效
- **Dry Run**：不实际获取数据，只检查配置

### 示例

```bash
# 验证字段是否支持
v-invest validate 600519 -r "roe,unknown_field"
# 输出：
# ✗ Unknown fields: unknown_field
# ✓ All fields valid

# 验证 + 指定市场
v-invest validate 00700 -r "roe,net_profit" -m HK
```

---

## 模块三：可用字段

### 查看所有字段

```bash
v-invest fields
```

### 常用字段（IFRS 标准）

| 字段 | 说明 | 字段 | 说明 |
|------|------|------|------|
| total_revenue | 营业总收入 | operating_cost | 营业成本 |
| operating_profit | 营业利润 | net_profit | 净利润 |
| total_assets | 总资产 | total_liabilities | 总负债 |
| total_equity | 股东权益 | cash_and_equivalents | 货币资金 |
| current_assets | 流动资产 | current_liabilities | 流动负债 |
| inventory | 存货 | accounts_receivable | 应收账款 |
| accounts_payable | 应付账款 | capital_expenditure | 资本开支 |
| operating_cash_flow | 经营现金流 | investing_cash_flow | 投资现金流 |
| financing_cash_flow | 筹资现金流 | prepayment | 预付款项 |
| fixed_assets | 固定资产 | intangible_assets | 无形资产 |
| goodwill | 商誉 | short_term_borrowings | 短期借款 |
| long_term_debt | 长期借款 | bond_payable | 应付债券 |
| interest_expense | 利息支出 | interest_income | 利息收入 |
| investment_income | 投资收益 | non_operating_income | 营业外收入 |
| fair_value_change | 公允价值变动 | construction_in_progress | 在建工程 |
| long_term_investment | 长期股权投资 | other_receivables | 其他应收款 |

### 财务指标（IFRS 标准）

| 字段 | 说明 | 字段 | 说明 |
|------|------|------|------|
| roe | 净资产收益率 | roa | 总资产收益率 |
| gross_margin | 毛利率 | net_profit_margin | 净利率 |
| operating_profit_margin | 经营利润率 | debt_ratio | 资产负债率 |
| current_ratio | 流动比率 | quick_ratio | 速动比率 |
| asset_turnover | 总资产周转率 | receivable_turnover | 应收账款周转率 |
| pe_ratio | 市盈率 | pb_ratio | 市净率 |

---

## 模块四：可用指标（40 个）

### 查看所有指标

```bash
v-invest indicators
```

### 查看指标依赖

```bash
v-invest indicators -d
```

### 按类别查看

```bash
v-invest indicators -g
```

### 常用指标速查

| 类别 | 指标 | 说明 |
|------|------|------|
| **增长** | revenue_cagr_10y | 营收 10 年 CAGR |
| | revenue_cagr_5y | 营收 5 年 CAGR |
| | net_profit_cagr_10y | 净利润 10 年 CAGR |
| | net_profit_cagr_5y | 净利润 5 年 CAGR |
| | growth_consistency | 增长一致性（正增长年数占比） |
| | revenue_yoy | 营收同比增长率 |
| | net_profit_yoy | 净利润同比增长率 |
| **盈利** | roe_volatility | ROE 波动率（越小越稳定） |
| | gross_margin_volatility | 毛利率波动率 |
| | cash_to_profit_volatility | 现金流/净利润波动率 |
| **偿债** | debt_to_ebitda | 债务/EBITDA |
| | free_cash_flow_to_debt | 自由现金流/债务 |
| | ocf_to_debt | 经营现金流/债务 |
| | currentdebt_to_debt | 短期债务占比 |
| **风险** | goodwill_to_net_assets_ratio | 商誉/净资产 |
| | prepayment_ratio | 预付款/总资产 |
| | other_receivables_ratio | 其他应收款/总资产 |
| | interest_coverage_ratio | 利息保障倍数 |
| **其他** | capex_to_revenue_ratio | 资本开支/营收 |
| | capex_stability | 资本开支稳定性 |
| | crisis_period_cagr | 危机期间 CAGR |
| | post_crisis_recovery | 危机后恢复速度 |

---

## 典型使用场景

### 场景 1：快速基本面概览（1 年）

```bash
v-invest query 600519 -r "roe,gross_margin,net_profit_margin,debt_ratio,current_ratio,total_revenue,net_profit" -y 1
```

### 场景 2：10 年财务分析

```bash
v-invest query 600519 -r "roe,gross_margin,net_profit_margin,revenue_cagr_10y,roe_volatility,capex_to_revenue_ratio,interest_coverage_ratio" -y 10
```

### 场景 3：偿债能力分析

```bash
v-invest query 600519 -r "debt_ratio,current_ratio,quick_ratio,cash_ratio,net_debt,ebitda,ocf_to_debt,debt_to_ebitda" -y 5
```

### 场景 4：风险排查

```bash
v-invest query 600519 -r "goodwill_to_net_assets_ratio,prepayment_ratio,other_receivables_ratio,interest_coverage_ratio,cash_to_net_profit_ratio" -y 5
```

### 场景 5：验证新字段

```bash
# 先验证
v-invest validate 600519 -r "new_field,roe"
# 再查询
v-invest query 600519 -r "new_field,roe" -y 1
```

---

## 校验清单

执行数据查询前确认：

- [ ] 字段名拼写正确（大小写敏感）
- [ ] 年数合理（1-10 年，A 股建议 10 年）
- [ ] 股票代码正确
- [ ] 需要验证时先用 `v-invest validate`

---

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `Unknown fields: xxx` | 字段名拼写错误 | `v-invest fields` 查看正确名称 |
| `Missing fields: xxx` | 字段暂不支持该市场 | 换用其他字段或 `-y 1` 测试 |
| 市场识别错误 | 代码同时满足多市场规则 | 显式指定 `-m A/HK/US` |
