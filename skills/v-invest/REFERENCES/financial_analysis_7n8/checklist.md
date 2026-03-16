# 财务分析标准清单

> 确保每次基本面分析不遗漏任何重要项目

---

## 一、基础信息收集

| 项目 | 命令 | 说明 |
|------|------|------|
| 股票信息 | `v-invest info {code} -m {market}` | 基本信息、行业 |
| 核心指标 | `v-invest indicator "roe,roa,roic,gross_margin,net_profit_margin,debt_ratio,current_ratio" -s {code} -m {market} -y 5` | 5年历史 |
| 增长指标 | `v-invest indicator "revenue_growth,net_profit_growth" -s {code} -m {market} -y 5` | 增速 |
| 营运指标 | `v-invest indicator "working_capital,wc_to_revenue" -s {code} -m {market} -y 5` | 营运效率 |

---

## 二、七看分析清单

### 1️⃣ 看营收数据
- [ ] 营业收入趋势（5年）
- [ ] 净利润趋势（5年）
- [ ] 扣非净利润对比
- [ ] 经营现金流/净利润（盈利质量）
- [ ] 自由现金流（OCF - CAPEX）

### 2️⃣ 看成本费用
- [ ] 毛利率（5年）
- [ ] 净利率（5年）
- [ ] 销售费用率 = 销售费用/营收
- [ ] 管理费用率 = 管理费用/营收
- [ ] 研发费用率 = 研发费用/营收
- [ ] 财务费用率 = 财务费用/营收
- [ ] 非经常性损益占比

### 3️⃣ 看增长
- [ ] 营收CAGR（3年/5年）
- [ ] 净利润CAGR（3年/5年）
- [ ] 增速稳定性（波动）

### 4️⃣ 看业务构成
- [ ] 主营业务占比
- [ ] 子公司/分部收入（若有）
- [ ] 上下游依赖度

### 5️⃣ 看资产负债
- [ ] 资产负债率（5年）
- [ ] 流动比率
- [ ] 速动比率
- [ ] 有息负债占比
- [ ] 存货周转天数
- [ ] 应收账款周转天数

### 6️⃣ 看投入产出
- [ ] 资产周转率
- [ ] 存货周转天数
- [ ] Working Capital（营运资金）
- [ ] WC/营收比率
- [ ] 固定资产周转率
- [ ] 人均收入（需外部数据）

### 7️⃣ 看收益率
- [ ] ROE（5年）
- [ ] ROA（5年）
- [ ] ROIC（5年）
- [ ] 与行业对比

---

## 三、数据获取速查

```bash
# 盈利能力
v-invest indicator "roe,roa,roic,gross_margin,net_profit_margin" -s {code} -m {market} -y 5

# 费用率
v-invest indicator "expense_ratio,fee_rate" -s {code} -m {market} -y 5

# 营运效率
v-invest indicator "working_capital,wc_to_revenue,asset_turnover" -s {code} -m {market} -y 5

# 增长
v-invest indicator "revenue_growth" -s {code} -m {market} -y 5

# 详细财务报表（用于计算各项费用率）
v-invest income {code} -m {market} -y 3
v-invest balance {code} -m {market} -y 3
v-invest cashflow {code} -m {market} -y 3
```

---

## 四、分析输出模板

```
# {股票名称} ({代码}) 基本面分析

## 一、核心数据
| 指标 | 2024 | 2023 | 2022 | 变化 |
|------|------|------|------|------|
| 营收 |      |      |      |      |
| 净利润 |   |      |      |      |
| ROE |       |      |      |      |
| ...

## 二、各维度分析结论
1. 营收：...
2. 成本费用：...
3. 增长：...
4. 业务构成：...
5. 资产负债：...
6. 投入产出：...
7. 收益率：...

## 三、综合评级
- 核心优势：...
- 风险关注：...
- 综合评级：...
```
