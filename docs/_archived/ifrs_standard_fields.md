# IFRS 标准财务字段参考

本文档定义了A股三张报表字段到国际财务报告标准(IFRS)字段的映射关系。

## 资产负债表 (Balance Sheet) - IFRS/IAS 1

| IFRS 字段 | 中文名称 | A股原始字段 | 说明 |
|-----------|----------|-------------|------|
| total_assets | 资产总计 | TOTAL_ASSETS | 资产总计 |
| total_liabilities | 负债合计 | TOTAL_LIABILITIES | 负债合计 |
| total_equity | 股东权益合计 | TOTAL_EQUITY | 股东权益合计 |
| current_assets | 流动资产合计 | TOTAL_CURRENT_ASSETS | 流动资产合计 |
| non_current_assets | 非流动资产合计 | TOTAL_NONCURRENT_ASSETS | 非流动资产合计 |
| current_liabilities | 流动负债合计 | TOTAL_CURRENT_LIAB | 流动负债合计 |
| non_current_liabilities | 非流动负债合计 | TOTAL_NONCURRENT_LIAB | 非流动负债合计 |
| cash_and_equivalents | 货币资金 | MONETARYFUNDS | 货币资金 |
| accounts_receivable | 应收账款 | ACCOUNTS_RECE | 应收账款 |
| inventory | 存货 | INVENTORY | 存货 |
| fixed_assets | 固定资产 | FIXED_ASSET | 固定资产 |
| intangible_assets | 无形资产 | INTANGIBLE_ASSET | 无形资产 |
| right_of_use_assets | 使用权资产 | USERIGHT_ASSET | 使用权资产 |
| accounts_payable | 应付账款 | ACCOUNTS_PAYABLE | 应付账款 |
| short_term_debt | 短期借款 | SHORT_LOAN | 短期借款 |
| long_term_debt | 长期借款 | LONG_LOAN | 长期借款 |
| bonds_payable | 应付债券 | BOND_PAYABLE | 应付债券 |
| prepaid_expenses | 预付款项 | PREPAID_EXP | 预付款项 |
| other_current_assets | 其他流动资产 | OTHER_CURRENT_ASSET | 其他流动资产 |
| deferred_tax_assets | 递延所得税资产 | DEFERRED_TAX_ASSETS | 递延所得税资产 |
| long_term_equity_invest | 长期股权投资 | LONG_EQUITY_INVEST | 长期股权投资 |
| construction_in_progress | 在建工程 | CONSTRUCT_PROGRESS | 在建工程 |
| other_non_current_assets | 其他非流动资产 | OTHER_NONCURRENT_ASSET | 其他非流动资产 |
| advance_receipts | 预收款项 | ADVANCE_RECEIPTS | 预收款项 |
| other_current_liabilities | 其他流动负债 | OTHER_CURRENT_LIAB | 其他流动负债 |
| deferred_tax_liabilities | 递延所得税负债 | DEFERRED_TAX_LIAB | 递延所得税负债 |

## 利润表 (Income Statement) - IFRS/IAS 1

| IFRS 字段 | 中文名称 | A股原始字段 | 说明 |
|-----------|----------|-------------|------|
| total_revenue | 营业总收入 | TOTAL_OPERATE_INCOME | 营业总收入 |
| operating_income | 营业收入 | OPERATE_INCOME | 营业收入 |
| total_operating_cost | 营业总成本 | TOTAL_OPERATE_COST | 营业总成本 |
| operating_cost | 营业成本 | OPERATE_COST | 营业成本 |
| gross_profit | 毛利润 | (计算: operating_income - operating_cost) | 需计算 |
| operating_profit | 营业利润 | OPERATE_PROFIT | 营业利润 |
| total_profit | 利润总额 | TOTAL_PROFIT | 利润总额 |
| net_profit | 净利润 | NETPROFIT | 净利润 |
| parent_net_profit | 归属于母公司净利润 | PARENT_NETPROFIT | 归属于母公司所有者的净利润 |
| research_expense | 研发费用 | RESEARCH_EXPENSE | 研发费用 |
| sales_expense | 销售费用 | SALE_EXPENSE | 销售费用 |
| management_expense | 管理费用 | MANAGE_EXPENSE | 管理费用 |
| financial_expense | 财务费用 | FINANCE_EXPENSE | 财务费用 |
| income_tax | 所得税费用 | INCOME_TAX | 所得税费用 |
| ebit | 息税前利润 | (计算: net_profit + income_tax + financial_expense) | 需计算 |
| ebitda | 息税折旧摊销前利润 | (计算: ebit + depreciation + amortization) | 需计算 |
| non_operating_income | 营业外收入 | NON_OPERATE_INCOME | 营业外收入 |
| non_operating_cost | 营业外支出 | NON_OPERATE_COST | 营业外支出 |
| investment_income | 投资收益 | INVEST_INCOME | 投资收益 |
| asset_disposal_gain | 资产处置收益 | ASSET_DISPOSAL_GAIN | 资产处置收益 |
| other_profit | 其他收益 | OTHER_PROFIT | 其他收益 |
| weighted_roe | 加权平均净资产收益率 | WEIGHTED_AVG_ROE | 加权平均净资产收益率 |
| basic_eps | 基本每股收益 | BASIC_EPS | 基本每股收益 |
| diluted_eps | 稀释每股收益 | DILUTED_EPS | 稀释每股收益 |

## 现金流量表 (Cash Flow Statement) - IFRS/IAS 7

| IFRS 字段 | 中文名称 | A股原始字段 | 说明 |
|-----------|----------|-------------|------|
| operating_cash_flow | 经营活动产生的现金流量净额 | NETCASH_OPERATE | 经营活动产生的现金流量净额 |
| investing_cash_flow | 投资活动产生的现金流量净额 | NETCASH_INVEST | 投资活动产生的现金流量净额 |
| financing_cash_flow | 筹资活动产生的现金流量净额 | NETCASH_FINANCE | 筹资活动产生的现金流量净额 |
| free_cash_flow | 自由现金流 | (计算: operating_cash_flow - investing_cash_flow) | 需计算 |
| capital_expenditure | 购建固定资产、无形资产和其他长期资产支付的现金 | CONSTRUCT_LONG_ASSET | 购建固定资产、无形资产和其他长期资产支付的现金 |
| cash_and_equivalents_end | 期末现金及现金等价物余额 | END_CCE | 期末现金及现金等价物余额 |
| cash_and_equivalents_begin | 期初现金及现金等价物余额 | BEGIN_CCE | 期初现金及现金等价物余额 |
| cash_received_from_sales | 销售商品、提供劳务收到的现金 | CASH_SALES | 销售商品、提供劳务收到的现金 |
| cash_paid_for_goods | 购买商品、接受劳务支付的现金 | CASH_PURCHASE | 购买商品、接受劳务支付的现金 |
| cash_paid_to_employees | 支付给职工以及为职工支付的现金 | CASH_TO_STAFF | 支付给职工以及为职工支付的现金 |
| taxes_paid | 支付的各项税费 | TAXES_PAYMENT | 支付的各项税费 |
| dividend_received | 取得投资收益收到的现金 | DIVIDEND_INCOME | 取得投资收益收到的现金 |
| debt_acquisition | 取得借款收到的现金 | BORROW_RECEIVE | 取得借款收到的现金 |
| bond_issuance | 发行债券收到的现金 | BOND_ISSUE | 发行债券收到的现金 |
| debt_repayment | 偿还债务支付的现金 | DEBT_REPAYMENT | 偿还债务支付的现金 |
| dividend_paid | 分配股利、利润或偿付利息支付的现金 | DIVIDEND_PAYMENT | 分配股利、利润或偿付利息支付的现金 |

## 字段命名规范

- **标准字段**: 使用小写字母 + 下划线 (snake_case)
- **原始字段**: A股字段保持原有大写格式
- **后缀规范**:
  - `*_original`: 保留原始字段值
  - `*_calculated`: 计算字段

## 使用示例

```python
from value_investment.data.mapper import DataMapper

# 原始数据
balance = ak.stock_balance_sheet_by_yearly_em(symbol="SH600519")

# 转换为标准格式
balance_std = DataMapper.map_balance_sheet(balance)
print(balance_std.columns)  # 显示标准字段名
```

## 计算字段说明

以下字段需要通过计算获得，不存在于原始数据中：

| 计算字段 | 计算公式 |
|----------|----------|
| gross_profit | operating_income - operating_cost |
| ebit | net_profit + income_tax + financial_expense |
| free_cash_flow | operating_cash_flow - investing_cash_flow |
| net_profit_margin | net_profit / total_revenue |
| roe | net_profit / total_equity |
| debt_to_assets | total_liabilities / total_assets |
