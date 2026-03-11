# IFRS 标准财务字段参考

**更新**: 2026-03-06 | **范围**: A 股 / 港股 / 美股

---

## 一、资产负债表 (Balance Sheet)

| IFRS 字段 | 中文 | A 股 | 港股 | 美股 |
|-----------|------|-----|------|------|
| total_assets | 总资产 | 资产总计 | 资产总值 | totalAssets |
| total_liabilities | 总负债 | 负债合计 | 总负债 | totalLiabilities |
| total_equity | 股东权益 | 股东权益合计 | 权益总额 | totalStockholdersEquity |
| current_assets | 流动资产 | 流动资产合计 | 流动资产合计 | totalCurrentAssets |
| current_liabilities | 流动负债 | 流动负债合计 | 流动负债合计 | totalCurrentLiabilities |
| cash_and_equivalents | 货币资金 | 货币资金 | 现金及等价物 | cashAndCashEquivalents |
| inventory | 存货 | 存货 | 存货 | inventory |
| accounts_receivable | 应收账款 | 应收账款 | 应收帐款 | accountsReceivable |
| fixed_assets | 固定资产 | 固定资产 | 固定资产 | propertyPlantEquipment |

---

## 二、利润表 (Income Statement)

| IFRS 字段 | 中文 | A 股 | 港股 | 美股 |
|-----------|------|-----|------|------|
| total_revenue | 营业总收入 | 营业总收入 | 收益 | totalRevenue |
| net_profit | 净利润 | 净利润 | 期内溢利 | netIncome |
| operating_profit | 营业利润 | 营业利润 | 营业溢利 | operatingIncome |
| gross_profit | 毛利润 | 毛利 | 毛利 | grossProfit |
| operating_cost | 营业成本 | 营业成本 | 已售存货成本 | costOfRevenue |

---

## 三、现金流量表 (Cash Flow Statement)

| IFRS 字段 | 中文 | A 股 | 港股 | 美股 |
|-----------|------|-----|------|------|
| operating_cash_flow | 经营现金流 | 经营活动现金流量净额 | 经营业务现金净额 | operatingCashFlow |
| investing_cash_flow | 投资现金流 | 投资活动现金流量净额 | 投资业务现金净额 | investingCashFlow |
| financing_cash_flow | 融资现金流 | 筹资活动现金流量净额 | 融资业务现金净额 | financingCashFlow |
| capital_expenditure | 资本支出 | 购建固定资产支付的现金 | 购建固定资产 | capitalExpenditure |

---

## 四、关键比率

| IFRS 字段 | 中文 | A 股 | 港股 | 美股 |
|-----------|------|-----|------|------|
| roe | 净资产收益率 | 净资产收益率 (%) | 股东权益回报率 (%) | returnOnEquity |
| roa | 总资产收益率 | 总资产收益率 (%) | 总资产回报率 (%) | returnOnAssets |
| gross_margin | 毛利率 | 销售毛利率 (%) | 毛利率 | grossMargin |
| net_profit_margin | 净利率 | 销售净利率 (%) | 销售净利率 (%) | netProfitMargin |
| current_ratio | 流动比率 | 流动比率 | 流动比率 | currentRatio |
| quick_ratio | 速动比率 | 速动比率 | 速动比率 | quickRatio |
| debt_ratio | 资产负债率 | 资产负债率 (%) | 资产负债率 | debtToAssetsRatio |

---

## 五、使用示例

```python
from value_investment.data.mapper import DataMapper

# 正向查找：标准字段 → 市场字段
DataMapper.get_market_field("total_revenue", "A 股")    # "营业总收入"
DataMapper.get_market_field("total_revenue", "港股")    # "收益"
DataMapper.get_market_field("total_revenue", "美股")    # "totalRevenue"

# 反向查找：市场字段 → 标准字段
DataMapper.get_standard_field("营业总收入", "A 股")  # "total_revenue"
DataMapper.get_standard_field("收益", "港股")        # "total_revenue"
DataMapper.get_standard_field("totalRevenue", "美股")  # "total_revenue"

# 映射财务报表
balance_std = DataMapper.map_balance_sheet(balance_raw)
income_std = DataMapper.map_income_statement(income_raw)
cashflow_std = DataMapper.map_cash_flow(cashflow_raw)
```

---

## 六、计算字段

以下字段需通过计算获得：

| 字段 | 公式 |
|-----|------|
| gross_profit | operating_income - operating_cost |
| ebit | net_profit + income_tax + financial_expense |
| free_cash_flow | operating_cash_flow - investing_cash_flow |

---

**完整映射表**: 参见 `src/value_investment/data/mapper.py` 中的 `CORE_FIELD_MAPPING`
