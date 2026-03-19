# IFRS 标准财务字段

> 项目的标准财务字段定义。所有字段必须在 `src/value_investment/pipeline/fields.py` 中定义。

**约束**: 禁止向 IFRSFields 添加新字段，只能添加到 CustomFields

---

## 一、资产负债表 (Balance Sheet)

| 字段名 | 中文名称 | 说明 |
|--------|---------|------|
| total_assets | 总资产 | 资产总计 |
| total_liabilities | 总负债 | 负债合计 |
| total_equity | 股东权益 | 股东权益合计 |
| current_assets | 流动资产 | 流动资产合计 |
| current_liabilities | 流动负债 | 流动负债合计 |
| cash_and_equivalents | 货币资金 | 现金及等价物 |
| inventory | 存货 | 存货 |
| accounts_receivable | 应收账款 | 应收款项 |
| accounts_payable | 应付账款 | 应付款项 |
| fixed_assets | 固定资产 | 固定资产净值 |
| prepayment | 预付款项 | 预付账款 |
| adv_receipts | 预收款项 | 预收账款 |
| contract_assets | 合同资产 | ASC 606 相关 |
| contract_liab | 合同负债 | ASC 606 相关 |

---

## 二、利润表 (Income Statement)

| 字段名 | 中文名称 | 说明 |
|--------|---------|------|
| total_revenue | 营业总收入 | 营业收入 |
| net_profit | 净利润 | 税后利润 |
| operating_profit | 营业利润 | 营业利润 |
| operating_cost | 营业成本 | 已售商品成本 |

---

## 三、现金流量表 (Cash Flow Statement)

| 字段名 | 中文名称 | 说明 |
|--------|---------|------|
| operating_cash_flow | 经营活动现金流 | 经营活动现金流量净额 |
| investing_cash_flow | 投资活动现金流 | 投资活动现金流量净额 |
| financing_cash_flow | 筹资活动现金流 | 筹资活动现金流量净额 |
| capital_expenditure | 资本支出 | 购建固定资产、无形资产支付的现金 |

---

## 四、财务指标 (Financial Ratios)

> 这些指标直接从数据源获取，非计算得出。

| 字段名 | 中文名称 | 说明 |
|--------|---------|------|
| roe | 净资产收益率 | Return on Equity (%) |
| roa | 总资产收益率 | Return on Assets (%) |
| gross_margin | 毛利率 | 销售毛利率 (%) |
| net_profit_margin | 净利率 | 销售净利率 (%) |
| current_ratio | 流动比率 | 流动资产/流动负债 |
| quick_ratio | 速动比率 | (流动资产-存货)/流动负债 |
| debt_ratio | 资产负债率 | 负债/资产 (%) |
| asset_turnover | 资产周转率 | 收入/资产 |
| receivable_turnover | 应收账款周转率 | 收入/应收账款 |

---

## 五、市场数据 (Market Data)

| 字段名 | 中文名称 | 说明 |
|--------|---------|------|
| market_cap | 总市值 | 市值 |
| total_shares | 总股本 | 股份总数 |
| pe_ratio | 市盈率 | Price/Earnings |
| pb_ratio | 市净率 | Price/Book |
| basic_eps | 基本每股收益 | Basic EPS |
| diluted_eps | 稀释每股收益 | Diluted EPS |
| book_value_per_share | 每股净资产 | Book Value Per Share |

---

## 六、字段统计

| 类别 | 数量 |
|-----|------|
| 资产负债表 | 14 |
| 利润表 | 4 |
| 现金流量表 | 4 |
| 财务指标 | 9 |
| 市场数据 | 7 |
| **总计** | **38** |

---

## 七、代码引用

```python
from value_investment.pipeline.fields import IFRSFields

# 使用示例
required_fields = {
    IFRSFields.TOTAL_REVENUE,
    IFRSFields.NET_PROFIT,
    IFRSFields.ROE,
}
```
