# 财务指标添加计划 - 分阶段实施

> **最后更新**: 2026-03-20
> **数据源**: Tushare fina_indicator API
> **⚠️ 重要**: 添加字段必须使用 `add-new-field` skill，创建计算器必须使用 `add-calculator` skill

## 使用的 Skills

| Skill | 用途 |
|-------|------|
| `add-new-field` | 添加新字段到 CustomFields、Provider 映射、Handler 注册 |
| `add-calculator` | 创建新的 Calculator（指标计算器） |

## 核心理念

**先直接可用，再计算得出**

优先级：
1. **P0**: Tushare `fina_indicator` 直接提供的字段，只需添加映射
2. **P1**: 额外有用的 Tushare 字段，建议一并添加
3. **P2**: 需要计算器实现的指标，后续迭代

---

## 指标总览

| 来源 | 数量 | 说明 | 状态 |
|------|:----:|------|:----:|
| ✅ Tushare 直接提供 | 18 | 只需添加映射 | ✅ 全部完成 |
| ✅ 额外有用字段 | 14 | 建议一并添加 | ✅ 全部完成 |
| ⚠️ 需要计算 | 32 | 后续实现计算器 | 🔄 进行中 |
| ❌ 暂不支持 | 3 | Tushare 无数据 | ⬜ 待处理 |
| **合计** | **67** | | |

---

## 第一阶段：Tushare 直接提供（只需添加映射）

**目标**: 补充 Tushare `fina_indicator` API 已有的指标映射

**状态**: ✅ 全部完成

### 1.1 偿债能力指标

| 序号 | Tushare 字段 | 标准字段 | 中文名 | 状态 |
|:----:|-------------|---------|-------|:----:|
| 1 | `cash_ratio` | `cash_ratio` | 现金比率 | ✅ 已完成 |
| 2 | `current_ratio` | `current_ratio` | 流动比率 | ✅ 已有 |
| 3 | `quick_ratio` | `quick_ratio` | 速动比率 | ✅ 已有 |
| 4 | `debt_to_assets` | `debt_ratio` | 资产负债率 | ✅ 已有 |
| 5 | `ocf_to_debt` | `ocf_to_debt` | 经营现金流/债务 | ✅ 已完成 |
| 6 | `currentdebt_to_debt` | `currentdebt_to_debt` | 短期债务占比 | ✅ 已完成 |
| 7 | `interestdebt` | `interest_bearing_debt` | 有息负债 | ✅ 已完成 |
| 8 | `ebitda` | `ebitda` | EBITDA | ✅ 已完成 |

### 1.2 盈利能力指标

| 序号 | Tushare 字段 | 标准字段 | 中文名 | 状态 |
|:----:|-------------|---------|-------|:----:|
| 9 | `grossprofit_margin` | `gross_margin` | 毛利率 | ✅ 已有 |
| 10 | `netprofit_margin` | `net_profit_margin` | 净利率 | ✅ 已有 |
| 11 | `roe` | `roe` | ROE | ✅ 已有 |
| 12 | `roa` | `roa` | ROA | ✅ 已有 |
| 13 | `op_of_gr` | `operating_profit_margin` | 营业利润率 | ✅ 已完成 |
| 14 | `roic` | `roic` | ROIC | ✅ 已有 |

### 1.3 增长指标

| 序号 | Tushare 字段 | 标准字段 | 中文名 | 状态 |
|:----:|-------------|---------|-------|:----:|
| 15 | `tr_yoy` | `revenue_yoy` | 营收同比增长率 | ✅ 已完成 |
| 16 | `netprofit_yoy` | `net_profit_yoy` | 净利润同比增长率 | ✅ 已完成 |

### 1.4 运营效率指标

| 序号 | Tushare 字段 | 标准字段 | 中文名 | 状态 |
|:----:|-------------|---------|-------|:----:|
| 17 | `ar_turn` | `receivable_turnover` | 应收账款周转率 | ✅ 已有 |
| 18 | `assets_turn` | `asset_turnover` | 资产周转率 | ✅ 已有 |

### 阶段汇总

| 类别 | 总数 | 已有 | 已完成 | 完成度 |
|------|:----:|:----:|:------:|:------:|
| 偿债能力 | 8 | 3 | 5 | 100% |
| 盈利能力 | 6 | 4 | 2 | 100% |
| 增长指标 | 2 | 0 | 2 | 100% |
| 运营效率 | 2 | 2 | 0 | 100% |
| **合计** | **18** | **9** | **9** | **100%** |

---

## 第二阶段：额外有用字段

**目标**: 添加 Tushare 提供但计划未列出的有用指标

**状态**: ✅ 全部完成

| 序号 | Tushare 字段 | 标准字段 | 中文名 | 用途 | 状态 |
|:----:|-------------|---------|-------|------|:----:|
| 1 | `netdebt` | `net_debt` | 净债务 | 偿债能力 | ✅ 已完成 |
| 2 | `ebit` | `ebit` | EBIT | 息税前利润 | ✅ 已完成 |
| 3 | `fcff` | `free_cash_flow_to_firm` | 企业FCF | 现金流 | ✅ 已完成 |
| 4 | `fcfe` | `free_cash_flow_to_equity` | 股权FCF | 现金流 | ✅ 已完成 |
| 5 | `ocf_to_shortdebt` | `ocf_to_short_debt` | OCF/短期债务 | 偿债能力 | ✅ 已完成 |
| 6 | `debt_to_eqt` | `debt_to_equity` | 产权比率 | 资本结构 | ✅ 已完成 |
| 7 | `longdeb_to_debt` | `long_term_debt_ratio` | 长期债务占比 | 债务结构 | ✅ 已完成 |
| 8 | `ca_to_assets` | `current_assets_ratio` | 流动资产占比 | 资产结构 | ✅ 已完成 |
| 9 | `saleexp_to_gr` | `selling_expense_ratio` | 销售费用率 | 费用分析 | ✅ 已完成 |
| 10 | `adminexp_of_gr` | `admin_expense_ratio` | 管理费用率 | 费用分析 | ✅ 已完成 |
| 11 | `finaexp_of_gr` | `finance_expense_ratio` | 财务费用率 | 费用分析 | ✅ 已完成 |
| 12 | `assets_yoy` | `total_assets_yoy` | 总资产同比增长 | 增长分析 | ✅ 已完成 |
| 13 | `eqt_yoy` | `equity_yoy` | 净资产同比增长 | 增长分析 | ✅ 已完成 |
| 14 | `ocf_yoy` | `operating_cash_flow_yoy` | OCF同比增长 | 现金流增长 | ✅ 已完成 |

### 阶段汇总

| 类别 | 总数 | 已完成 | 完成度 |
|------|:----:|:------:|:------:|
| **合计** | **14** | **14** | **100%** |

---

## 第三阶段：需要计算器实现

**目标**: 实现需要计算的指标

**预计工作量**: 每个指标 0.5-1 天，迭代实现

**状态**: 🔄 进行中 (11/32 完成)

### 3.1 简单计算（2 个字段）

| 序号 | 指标名 | 字段名 | 计算公式 | 状态 |
|:----:|--------|--------|---------|:----:|
| 1 | 自由现金流 | `free_cash_flow` | OCF - CAPEX | ✅ 已有 |
| 2 | 现金净额 | `net_cash_position` | 货币资金 - 有息负债 | ✅ 已有 |

### 3.2 偿债能力指标（需计算）

| 序号 | 指标名 | 字段名 | 计算公式 | 状态 |
|:----:|--------|--------|---------|:----:|
| 3 | 净负债率 | `net_debt_to_equity` | 净债务/净资产 | ✅ 已完成 |
| 4 | 利息保障倍数 | `interest_coverage_ratio` | 营业利润/利息支出 | ✅ 已完成 |
| 5 | 自由现金流/债务 | `free_cash_flow_to_debt` | 自由现金流/总债务 | ✅ 已完成 |
| 6 | 债务/EBITDA | `debt_to_ebitda` | 总债务/EBITDA | ✅ 已完成 |
| 7 | 1年内到期占比 | `debt_due_within_1y_ratio` | 1年内到期/总债务 | ✅ 已完成 |
| 8 | 融资成本 | `financing_cost_rate` | 财务成本/有息负债 | ✅ 已完成 |

### 3.3 增长指标（需计算）

| 序号 | 指标名 | 字段名 | 计算公式 | 状态 |
|:----:|--------|--------|---------|:----:|
| 9 | 存货增长率 | `inventory_growth_rate` | (本期-上期)/上期 | ✅ 已完成 |
| 10 | 应收账款增长率 | `accounts_receivable_growth_rate` | (本期-上期)/上期 | ✅ 已完成 |
| 11 | 营收 CAGR(5年) | `revenue_cagr_5y` | (终值/初值)^(1/5)-1 | ✅ 已完成 |
| 12 | 营收 CAGR(10年) | `revenue_cagr_10y` | (终值/初值)^(1/10)-1 | ✅ 已完成 |
| 13 | 净利润 CAGR(5年) | `net_profit_cagr_5y` | (终值/初值)^(1/5)-1 | ✅ 已完成 |
| 14 | 净利润 CAGR(10年) | `net_profit_cagr_10y` | (终值/初值)^(1/10)-1 | ✅ 已完成 |

### 3.4 组合信号指标（排雷专用）

| 序号 | 指标名 | 字段名 | 计算公式 | 状态 |
|:----:|--------|--------|---------|:----:|
| 15 | 现金流/净利润比 | `cash_to_net_profit_ratio` | 经营现金流/净利润 | ✅ 已完成 |
| 16 | 存货营收增速差 | `inventory_revenue_growth_gap` | 存货增速-营收增速 | ✅ 已完成 |
| 17 | 应收营收增速差 | `receivable_revenue_growth_gap` | 应收增速-营收增速 | ✅ 已完成 |
| 18 | 利息收入率 | `interest_income_rate` | 利息收入/货币资金 | ✅ 已完成 |
| 19 | 其他应收款占比 | `other_receivables_ratio` | 其他应收款/总资产 | ✅ 已完成 |
| 20 | 商誉净资产比 | `goodwill_to_net_assets_ratio` | 商誉/净资产 | ✅ 已完成 |

### 3.5 结构占比指标

| 序号 | 指标名 | 字段名 | 计算公式 | 状态 |
|:----:|--------|--------|---------|:----:|
| 21 | 主营业务占比 | `core_business_ratio` | 主营业务/总收入 | ✅ 已完成 |
| 22 | 预付款占比 | `prepayment_ratio` | 预付款/总资产 | ✅ 已完成 |
| 23 | 长期投资占比 | `long_term_investment_ratio` | 长投/总资产 | ✅ 已完成 |
| 24 | 营业外收入占比 | `non_operating_income_ratio` | 营业外收入/利润 | ✅ 已完成 |
| 25 | 公允价值变动占比 | `fair_value_change_ratio` | 公允价值变动/利润 | ✅ 已完成 |
| 26 | 投资收益占比 | `investment_income_ratio` | 投资收益/利润 | ✅ 已完成 |
| 27 | 资本开支营收比 | `capex_to_revenue_ratio` | 资本开支/营收 | ✅ 已完成 |

### 3.6 稳定性/波动率指标（需时间序列）

| 序号 | 指标名 | 字段名 | 计算公式 | 状态 |
|:----:|--------|--------|---------|:----:|
| 28 | 增长一致性 | `growth_consistency` | 正增长年数/总年数 | ✅ 已完成 |
| 29 | ROE 波动率 | `roe_volatility` | 标准差/均值 | ✅ 已完成 |
| 30 | 毛利率波动率 | `gross_margin_volatility` | 标准差 | ✅ 已完成 |
| 31 | 现金流净利润波动率 | `cash_to_profit_volatility` | 比值标准差/均值 | ✅ 已完成 |
| 32 | 资本开支稳定性 | `capex_stability` | 占比标准差 | ✅ 已完成 |

### 3.7 危机期指标

| 序号 | 指标名 | 字段名 | 计算公式 | 状态 |
|:----:|--------|--------|---------|:----:|
| 33 | 危机期 CAGR | `crisis_period_cagr` | (终值/初值)^(1/n)-1 | ✅ 已完成 |
| 34 | 危机后恢复速度 | `post_crisis_recovery` | 恢复年数 | ✅ 已完成 |

### 阶段汇总

| 类别 | 总数 | 已有 | 已完成 | 待添加 | 完成度 |
|------|:----:|:----:|:------:|:------:|:------:|
| 简单计算 | 2 | 2 | 0 | 0 | 100% |
| 偿债能力 | 6 | 0 | 4 | 2 | 67% |
| 增长指标 | 6 | 0 | 4 | 2 | 67% |
| 组合信号 | 6 | 0 | 6 | 0 | 100% |
| 结构占比 | 7 | 0 | 7 | 0 | 100% |
| 稳定性/波动率 | 5 | 0 | 5 | 0 | 100% |
| 危机期 | 2 | 0 | 2 | 0 | 100% |
| **合计** | **34** | **2** | **28** | **4** | **82%** |

---

## 第四阶段：暂不支持（需其他数据源）

**说明**: 以下指标 Tushare `fina_indicator` 无数据，需其他数据源或手动获取

| 序号 | 指标名 | 字段名 | 说明 | 状态 |
|:----:|--------|--------|------|:----:|
| 1 | 授信使用率 | `credit_utilization` | 需查看附注/银行授信协议 | ⬜ 待处理 |
| 2 | 关联交易占比 | `related_party_transaction_ratio` | 需查看附注 | ⬜ 待处理 |
| 3 | 股东回报比 | `shareholder_return_ratio` | 需回购数据（美股 yfinance 有） | ⬜ 待处理 |

---

## 实施任务分解

### Task 1-Task 2: ✅ 已完成

第一阶段和第二阶段所有字段映射已添加完成。

### Task 3: 添加计算器（进行中）

> **⚠️ 必须使用 `add-calculator` skill**

**已完成计算器**:
| Calculator | 状态 | 完成日期 |
|------------|:----:|----------|
| `net_debt_to_equity` | ✅ | 2026-03-20 |
| `interest_coverage_ratio` | ✅ | 2026-03-20 |
| `free_cash_flow_to_debt` | ✅ | 2026-03-20 |
| `debt_to_ebitda` | ✅ | 2026-03-20 |
| `financing_cost_rate` | ✅ | 2026-03-20 |
| `cash_to_net_profit_ratio` | ✅ | 2026-03-20 |
| `inventory_growth_rate` | ✅ | 2026-03-20 |
| `accounts_receivable_growth_rate` | ✅ | 2026-03-20 |
| `interest_income_rate` | ✅ | 2026-03-20 |
| `revenue_cagr_10y` | ✅ | 2026-03-20 |
| `net_profit_cagr_10y` | ✅ | 2026-03-20 |
| `other_receivables_ratio` | ✅ | 2026-03-20 |
| `goodwill_to_net_assets_ratio` | ✅ | 2026-03-20 |
| `long_term_investment_ratio` | ✅ | 2026-03-20 |
| `non_operating_income_ratio` | ✅ | 2026-03-20 |
| `prepayment_ratio` | ✅ | 2026-03-20 |
| `capex_to_revenue_ratio` | ✅ | 2026-03-20 |
| `debt_due_within_1y_ratio` | ✅ | 2026-03-20 |
| `revenue_cagr_5y` | ✅ | 2026-03-20 |
| `net_profit_cagr_5y` | ✅ | 2026-03-20 |
| `roe_volatility` | ✅ | 2026-03-20 |
| `fair_value_change_ratio` | ✅ | 2026-03-20 |
| `investment_income_ratio` | ✅ | 2026-03-20 |
| `core_business_ratio` | ✅ | 2026-03-20 |
| `growth_consistency` | ✅ | 2026-03-20 |
| `gross_margin_volatility` | ✅ | 2026-03-20 |
| `cash_to_profit_volatility` | ✅ | 2026-03-20 |
| `capex_stability` | ✅ | 2026-03-20 |
| `crisis_period_cagr` | ✅ | 2026-03-20 |
| `post_crisis_recovery` | ✅ | 2026-03-20 |

**待添加计算器**（按优先级）:
1. `inventory_revenue_growth_gap` - 存货营收增速差
2. `receivable_revenue_growth_gap` - 应收营收增速差
3. ...（剩余 2 个指标）

---

## 验收标准

### 第一阶段验收 ✅

- [x] 所有 Tushare 直接提供字段完成映射（18个）
- [x] 额外有用字段完成映射（14个）
- [x] API 可以查询新字段
- [x] 测试通过

### 第二阶段验收 ✅

- [x] 按优先级逐步实现复杂计算指标
- [x] 每个指标有独立测试
- [x] 时间序列计算正确
- [x] 排雷手册中的组合信号可以计算

### 第三阶段验收 🔄

- [x] 净负债率 (net_debt_to_equity) - 完成
- [x] 利息保障倍数 (interest_coverage_ratio) - 完成
- [x] 自由现金流/债务 (free_cash_flow_to_debt) - 完成
- [x] 债务/EBITDA (debt_to_ebitda) - 完成
- [x] 融资成本 (financing_cost_rate) - 完成
- [x] 现金流/净利润比 (cash_to_net_profit_ratio) - 完成
- [x] 存货增长率 (inventory_growth_rate) - 完成
- [x] 应收账款增长率 (accounts_receivable_growth_rate) - 完成
- [x] 利息收入率 (interest_income_rate) - 完成
- [x] 预付款占比 (prepayment_ratio) - 完成
- [x] 资本开支营收比 (capex_to_revenue_ratio) - 完成
- [x] 一年内到期债务占比 (debt_due_within_1y_ratio) - 完成
- [x] 营收CAGR 5年 (revenue_cagr_5y) - 完成
- [x] 净利润CAGR 5年 (net_profit_cagr_5y) - 完成
- [x] ROE波动率 (roe_volatility) - 完成
- [x] 存货营收增速差 (inventory_revenue_growth_gap) - 完成
- [x] 应收营收增速差 (receivable_revenue_growth_gap) - 完成
- [x] 公允价值变动占比 (fair_value_change_ratio) - 完成
- [x] 投资收益占比 (investment_income_ratio) - 完成
- [x] 主营业务占比 (core_business_ratio) - 完成
- [x] 增长一致性 (growth_consistency) - 完成
- [x] 毛利率波动率 (gross_margin_volatility) - 完成
- [x] 现金流净利润波动率 (cash_to_profit_volatility) - 完成
- [x] 资本开支稳定性 (capex_stability) - 完成
- [x] 危机期CAGR (crisis_period_cagr) - 完成
- [x] 危机后恢复速度 (post_crisis_recovery) - 完成
- [ ] ...（剩余 0 个指标）

---

## 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Tushare 字段变更 | 中 | 建立字段映射测试，及时发现变更 |
| 计算器依赖循环 | 高 | 引入依赖图，自动检测循环依赖 |
| 时间序列计算性能 | 中 | 缓存计算结果，避免重复计算 |

---

## 后续优化

1. **依赖图管理**: 自动排序计算器执行顺序
2. **跨期计算支持**: 支持 `calculate(results, window=5)` 参数
3. **配置化阈值**: 将排雷手册的阈值配置化
