# 财务三表字段查询

查询资产负债表、利润表、现金流量表的可用字段。

## 命令

```bash
# 查看报表可用字段
v-invest fields <market> <report>
```

## 参数说明

| 参数 | 说明 | 可选值 |
|------|------|--------|
| market | 市场 | `A`, `HK`, `US` |
| report | 报表类型 | `balance`, `income`, `cashflow`, `finind`, `quarterly` |

## 示例

```bash
# A股资产负债表字段
v-invest fields A balance

# A股利润表字段
v-invest fields A income

# 港股财务指标字段
v-invest fields HK finind

# 美股现金流量表字段
v-invest fields US cashflow
```

## 报表类型说明

| report | 说明 |
|--------|------|
| balance | 资产负债表 |
| income | 利润表 |
| cashflow | 现金流量表 |
| finind | 财务指标 |
| quarterly | 季报 |

## 常用字段速查

### A股-资产负债表 (balance)

| 字段 | 说明 |
|------|------|
| total_assets | 资产总计 |
| total_liab | 负债合计 |
| total_hldr_eqy_excl_min_int | 归属股东权益合计 |
| total_hldr_eqy_inc_min_int | 股东权益合计 |
| cash_and_equivalents | 货币资金 |
| tradable_fi_assets | 交易性金融资产 |
| accounts_receivable | 应收账款 |
| inventory | 存货 |
| total_cur_assets | 流动资产合计 |
| total_cur_liab | 流动负债合计 |
| longterm_loan | 长期借款 |

### A股-利润表 (income)

| 字段 | 说明 |
|------|------|
| revenue | 营业总收入 |
| operating_profit | 营业利润 |
| total_profit | 利润总额 |
| net_profit | 净利润 |
| parent_netprofit | 归属净利润 |
| basic_eps | 基本每股收益 |
| diluted_eps | 稀释每股收益 |

### A股-财务指标 (finind)

| 字段 | 说明 |
|------|------|
| roe | 净资产收益率 |
| roe_weighted | 净资产收益率(加权) |
| net_profit_margin | 净利率 |
| gross_profit_margin | 毛利率 |
| debt_to_asset | 资产负债率 |
| asset_turnover | 总资产周转率 |
| revenue_growth | 营业收入增长率 |
