# 数据获取优化指南 - 按需查询

> 避免返回过多数据，使用 `-f` 参数指定所需字段

---

## 一、指标数据查询（推荐）

### 1. 核心指标（当前+历史）

```bash
# 当前5年数据
v-invest indicator \
  roe,roa,net_profit_margin,gross_margin,total_assets_turnover,equity_multiplier,debt_ratio \
  -s {stock_code} -y 5

# 历史10年趋势数据
v-invest indicator \
  roe,net_profit_margin,total_assets_turnover,equity_multiplier \
  -s {stock_code} -y 10
```

### 2. 成长性指标

```bash
v-invest indicator \
  roe_yoy,net_profit_yoy,total_revenue_yoy \
  -s {stock_code} -y 5
```

### 3. 运营效率指标

```bash
v-invest indicator \
  inventory_turnover,receivable_turnover,current_ratio \
  -s {stock_code} -y 5
```

---

## 二、财务报表查询（按需指定字段）

### 1. 利润表 - 关键字段

```bash
# 基础利润数据
v-invest income {stock_code} -y 10 -f \
  report_date,total_revenue,operating_cost,gross_profit,operating_profit,net_profit

# 费用结构分析
v-invest income {stock_code} -y 10 -f \
  report_date,total_revenue,selling_expenses,admin_expenses,rd_expenses,financial_expense

# 完整利润分析
v-invest income {stock_code} -y 10 -f \
  report_date,total_revenue,operating_cost,gross_profit,operating_profit,net_profit,income_tax
```

**常用利润表字段**:
| 字段名 | 说明 | 用途 |
|-------|------|------|
| report_date | 报告日期 | 时间序列 |
| total_revenue | 营业收入 | 规模分析 |
| operating_cost | 营业成本 | 成本分析 |
| gross_profit | 毛利润 | 毛利率计算 |
| operating_profit | 营业利润 | 经营效率 |
| net_profit | 净利润 | 盈利能力 |
| selling_expenses | 销售费用 | 费用结构 |
| admin_expenses | 管理费用 | 费用结构 |
| rd_expenses | 研发费用 | 创新能力 |
| financial_expense | 财务费用 | 财务成本 |
| income_tax | 所得税 | 税收分析 |

### 2. 资产负债表 - 关键字段

```bash
# 资产负债结构
v-invest balance {stock_code} -y 10 -f \
  report_date,total_assets,total_equity,total_liabilities

# 营运资本分析
v-invest balance {stock_code} -y 10 -f \
  report_date,current_assets,current_liabilities,inventory,accounts_receivable

# 完整资产分析
v-invest balance {stock_code} -y 10 -f \
  report_date,total_assets,total_equity,total_liabilities,current_assets,current_liabilities
```

**常用资产负债表字段**:
| 字段名 | 说明 | 用途 |
|-------|------|------|
| report_date | 报告日期 | 时间序列 |
| total_assets | 总资产 | 规模分析 |
| total_equity | 股东权益 | 净资产 |
| total_liabilities | 总负债 | 负债水平 |
| current_assets | 流动资产 | 流动性 |
| current_liabilities | 流动负债 | 流动性 |
| inventory | 存货 | 周转分析 |
| accounts_receivable | 应收账款 | 周转分析 |
| fixed_assets | 固定资产 | 资产结构 |

### 3. 现金流量表 - 关键字段

```bash
# 现金流质量分析
v-invest cashflow {stock_code} -y 10 -f \
  report_date,operating_cash_flow,net_profit

# 完整现金流分析
v-invest cashflow {stock_code} -y 10 -f \
  report_date,operating_cash_flow,investing_cash_flow,financing_cash_flow
```

**常用现金流量表字段**:
| 字段名 | 说明 | 用途 |
|-------|------|------|
| report_date | 报告日期 | 时间序列 |
| operating_cash_flow | 经营现金流 | 现金流质量 |
| investing_cash_flow | 投资现金流 | 投资活动 |
| financing_cash_flow | 融资现金流 | 融资活动 |
| net_profit | 净利润 | 净现比计算 |

---

## 三、查询优化原则

### 1. 按需查询
- ❌ 避免: `v-invest income 600519 -y 10`（返回所有字段，数据量大）
- ✅ 推荐: `v-invest income 600519 -y 10 -f report_date,total_revenue,net_profit`（仅返回所需字段）

### 2. 分步查询
- 先查询核心指标（`indicator`命令）
- 再按需查询具体报表字段
- 避免一次性查询过多字段

### 3. 常用组合

| 分析目的 | 推荐查询 |
|---------|---------|
| ROE分析 | `indicator roe,roa,net_profit_margin -s 600519 -y 10` |
| 费用分析 | `income 600519 -y 10 -f report_date,total_revenue,selling_expenses,admin_expenses` |
| 现金流分析 | `cashflow 600519 -y 10 -f report_date,operating_cash_flow,net_profit` |
| 资产结构 | `balance 600519 -y 10 -f report_date,total_assets,total_equity,total_liabilities` |

---

## 四、字段查询方法

如果不确定字段名，可以先查询所有字段，然后筛选：

```bash
# 查看所有可用字段
v-invest fields A income

# 示例输出：
# total_revenue
# operating_cost
# gross_profit
# ...
```

---

## 五、实战示例

### 示例1: 茅台10年ROE趋势

```bash
v-invest indicator roe -s 600519 -y 10
```

### 示例2: 茅台10年费用趋势

```bash
v-invest income 600519 -y 10 -f \
  report_date,total_revenue,selling_expenses,admin_expenses,rd_expenses
```

### 示例3: 茅台10年现金流质量

```bash
v-invest cashflow 600519 -y 10 -f \
  report_date,operating_cash_flow,net_profit
```

---

*最后更新: 2026-03-12*
