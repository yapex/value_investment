---
name: financial-risk-scan
description: 企业财务排雷手册 - 排雷（造假）+ 排险（生存）+ 排优（长期价值），A/H/美股通用
---

# 企业财务排雷手册

## 使用方式

```
用户: "对贵州茅台进行财务风险扫描"
Skill: 执行以下数据获取，然后阅读 [REFERENCE.md](./REFERENCE.md) 输出分析报告
```

## 数据获取（10年）

```bash
v-invest query {股票} -r "total_revenue,operating_cost,operating_profit,net_profit,interest_expense,interest_income,non_operating_income,investment_income,fair_value_change,total_assets,total_liabilities,total_equity,cash_and_equivalents,short_term_borrowings,long_term_debt,bond_payable,current_assets,current_liabilities,inventory,accounts_receivable,prepayment,other_receivables,construction_in_progress,goodwill,long_term_investment,fixed_assets,intangible_assets,accounts_payable,operating_cash_flow,investing_cash_flow,financing_cash_flow,capital_expenditure,roe,gross_margin,net_profit_margin,debt_ratio,current_ratio,quick_ratio,cash_ratio,net_debt,ebitda,ebit,asset_turnover,receivable_turnover,inventory_turnover,debt_to_equity,total_asset_turnover,revenue_yoy,net_profit_yoy,equity_yoy,operating_cash_flow_yoy,total_assets_yoy,cash_to_net_profit_ratio,cash_short_debt_ratio,prepayment_ratio,other_receivables_ratio,goodwill_to_net_assets_ratio,capex_to_revenue_ratio,interest_coverage_ratio,interest_income_rate,financing_cost_rate,non_operating_income_ratio,investment_income_ratio,fair_value_change_ratio,operating_profit_margin,long_term_investment_ratio,net_profit_cagr_10y,roe_volatility,gross_margin_volatility,growth_consistency,revenue_cagr_10y,crisis_period_cagr,post_crisis_recovery,capex_stability,cash_to_profit_volatility,ocf_to_debt,currentdebt_to_debt,long_term_debt_ratio" -e {年份} -y 10
```

## 执行

**必须按 [REFERENCE.md](./REFERENCE.md) 中的要求执行分析！**

1. 获取 10 年财务数据
2. 阅读 [REFERENCE.md](./REFERENCE.md)（分析师文档）
3. **严格按 REFERENCE.md 中的 10 个段落结构、阈值标准、判定规则执行分析**
4. 输出报告

## 字段说明

| 类别 | 字段数 | 说明 |
|------|--------|------|
| 利润表 | 9 | 营收、成本、利润、利息、营业外等 |
| 资产负债表 | 17 | 资产、负债、权益、存货、应收等 |
| 现金流量表 | 4 | 经营/投资/筹资现金流、资本开支 |
| 财务指标 | 12 | ROE、毛利率、资产负债率、流动比率等 |
| 增长指标 | 5 | 营收/净利润增长率、CAGR |
| 风险指标 | 12 | 商誉占比、利息保障、现金流覆盖等 |
| 稳定性指标 | 8 | 波动率、一致性、危机表现等 |

## 验证

```bash
v-invest validate {股票} -r "roe,gross_margin,net_profit_margin,debt_ratio,current_ratio"
```

如果出现 `Missing fields`，说明该市场暂不支持此字段，需换用其他字段。
