---
name: financial-risk-scan
description: 企业财务排雷手册 v1.0.8 - 排雷（造假）+ 排险（生存）+ 排优（长期价值），A/H/美股通用
---

# 企业财务排雷手册

> **版本**：v1.0.8
>
> **框架定位**：排雷（造假）+ 排险（生存）+ 排优（长期价值）
>
> **适用对象**：A 股/港股/美股上市公司（金融行业除外）
>
> **核心理念**：投资的第一原则是不亏钱，第二原则才是赚钱

## 使用方式

```
用户: "对 {股票代码} 进行财务风险扫描"
Skill: 执行以下数据获取，然后阅读 [REFERENCE.md](./REFERENCE.md) 输出分析报告
```

## 数据获取（10年）

```bash
v-invest query {股票} -r "total_revenue,operating_cost,operating_profit,net_profit,parent_net_profit,interest_expense,interest_income,non_operating_income,investment_income,fair_value_change,total_assets,total_liabilities,total_equity,cash_and_equivalents,short_term_borrowings,long_term_debt,bond_payable,current_assets,current_liabilities,inventory,accounts_receivable,prepayment,other_receivables,construction_in_progress,goodwill,long_term_investment,fixed_assets,intangible_assets,accounts_payable,adv_receipts,contract_assets,contract_liab,non_current_liabilities_due_1y,operating_cash_flow,investing_cash_flow,financing_cash_flow,capital_expenditure,free_cash_flow_to_firm,free_cash_flow_to_equity,roe,roa,gross_margin,net_profit_margin,debt_ratio,current_ratio,quick_ratio,cash_ratio,net_debt,net_debt_to_equity,ebitda,ebit,asset_turnover,receivable_turnover,inventory_turnover,debt_to_equity,total_asset_turnover,revenue_yoy,net_profit_yoy,equity_yoy,operating_cash_flow_yoy,total_assets_yoy,total_shares,market_cap,book_value_per_share,basic_eps,diluted_eps,pe_ratio,pb_ratio,ocf_to_debt,currentdebt_to_debt,long_term_debt_ratio,interest_bearing_debt,long_term_investment_ratio,operating_profit_margin,cash_short_debt_ratio,prepayment_ratio,other_receivables_ratio,goodwill_to_net_assets_ratio,capex_to_revenue_ratio,interest_coverage_ratio,interest_income_rate,financing_cost_rate,non_operating_income_ratio,investment_income_ratio,fair_value_change_ratio,implied_growth,net_margin,net_profit_cagr_10y,roe_volatility,gross_margin_volatility,growth_consistency,revenue_cagr_10y,crisis_period_cagr,post_crisis_recovery,capex_stability,cash_to_profit_volatility,net_profit_cagr_5y,revenue_cagr_5y,receivable_revenue_growth_gap,inventory_growth_rate,accounts_receivable_growth_rate,cumulative_ocf_to_nprofit,debt_to_ebitda,free_cash_flow_to_debt,core_business_ratio" -e {年份} -y 10
```

## 执行

**必须按 [REFERENCE.md](./REFERENCE.md) 中的要求执行分析！**

1. 获取 10 年财务数据
2. 阅读 [REFERENCE.md](./REFERENCE.md)（分析师文档）
3. **严格按 REFERENCE.md 中的 10 个段落结构、阈值标准、判定规则执行分析**
4. 输出完整报告（46 项自检清单）

## 分析流程

| 段落 | 内容 | 定位 | 自检项数 |
|------|------|------|---------|
| 第一段 | 数据提取汇总 | 基础数据 | 6 项 |
| 第二段 | 偿债能力分析 | 排险（生存） | 6 项 |
| 第三段 | 组合信号排查（C01-C10） | 排雷（造假） | 4 项 |
| 第四段 | 单字段排查（P0/P1/P2） | 排雷 + 排险 | 5 项 |
| 第五段 | 长期价值分析 | 排优（投资） | 6 项 |
| 第六段 | 时间序列分析 | 趋势验证 | 3 项 |
| 第七段 | 特殊项目分析 | 补充风险 | 4 项 |
| 第八段 | 综合判定 | 汇总判定 | 4 项 |
| 第九段 | 结论与建议 | 行动建议 | 4 项 |
| 第十段 | 局限性说明 | 风险提示 | 4 项 |
| **合计** | - | - | **46 项** |

## 字段说明

| 类别 | 字段数 | 说明 |
|------|--------|------|
| 利润表 | 11 | 营收、成本、利润、利息、营业外、投资收益、公允价值等 |
| 资产负债表 | 18 | 资产、负债、权益、存货、应收、预付、在建工程、商誉等 |
| 现金流量表 | 5 | 经营/投资/筹资现金流、资本开支、自由现金流 |
| 偿债指标 | 10 | 资产负债率、流动/速动/现金比率、净负债、利息保障等 |
| 风险指标 | 9 | 商誉占比、利息保障、现金流覆盖、预付/其他应收占比等 |
| 增长指标 | 6 | 营收/净利润增长率、CAGR、增长一致性 |
| 稳定性指标 | 8 | ROE/毛利率波动率、现金流波动、资本开支稳定性、危机表现等 |
| 估值指标 | 6 | 市值、PE、PB、EPS等 |

## 快速排雷（8 项）

如果时间有限，可使用快速排雷清单（8 项），任何一项🔴 = 直接排除：

| 序号 | 检查项 | 阈值 |
|------|--------|------|
| 1 | 审计意见 | 非标准无保留🔴 |
| 2 | 现金流/净利润（连续2年） | <0.5🔴 |
| 3 | 资产负债率 | >70%🔴 |
| 4 | 利息保障倍数 | <3🔴 |
| 5 | CFO 更换频率（5年） | >3次🔴 |
| 6 | 关联交易占比 | >30%🔴 |
| 7 | 主营业务变更（5年） | >2次🔴 |
| 8 | 长期价值评分 | <60分🔴 |

## 验证

```bash
v-invest validate {股票} -r "roe,gross_margin,net_profit_margin,debt_ratio,current_ratio"
```

如果出现 `Missing fields`，说明该市场暂不支持此字段，需换用其他字段。

## 判定标准

| 判定 | 符号 | 说明 |
|------|:----:|------|
| 未触发（安全） | ✅ | 无风险信号 |
| 部分触发 | ⚠️ | 需进一步核实 |
| 已触发（危险） | 🔴 | 高风险信号，一票否决 |
| 数据不足 | 🟡 | 无法判定 |

## 安全边际原则

| 原则 | 说明 | 应用示例 |
|------|------|---------|
| **数据保守原则** | 宁可低估，不可高估 | 现金流用 5 年最低值 |
| **结论保守原则** | 宁可错杀，不可放过 | 一项🔴即警示，两项🔴即排除 |
| **决策保守原则** | 宁可错过，不可错投 | 不确定时选择观望 |
