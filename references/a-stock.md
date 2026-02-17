# A股参考文档

本文档包含 A 股市场的详细字段和指标信息。

## 个股信息字段

`info` 命令返回以下信息（来源：东方财富）：

| 字段 | 说明 | 示例 |
|------|------|------|
| 最新 | 最新股价 | 1485.3 |
| 股票代码 | 6位股票代码 | 600519 |
| 股票简称 | 股票名称 | 贵州茅台 |
| 总股本 | 总股本(股) | 1252270215 |
| 流通股 | 流通股本(股) | 1252270215 |
| 总市值 | 总市值(元) | 1.86万亿 |
| 流通市值 | 流通市值(元) | 1.86万亿 |
| 行业 | 所属行业 | 白酒Ⅱ |
| 上市时间 | 上市日期 | 20010827 |

## 历史行情字段

`hist` 命令返回以下字段（来源：东方财富）：

| 字段 | 说明 | 示例 |
|------|------|------|
| 日期 | 交易日 | 2025-01-02 |
| 股票代码 | 6位股票代码 | 600519 |
| 开盘 | 开盘价 | 1524.0 |
| 收盘 | 收盘价 | 1488.0 |
| 最高 | 最高价 | 1524.49 |
| 最低 | 最低价 | 1480.00 |
| 成交量 | 成交量(手) | 50029 |
| 成交额 | 成交额(元) | 7.49e+09 |
| 振幅 | 振幅(%) | 2.92 |
| 涨跌幅 | 涨跌幅(%) | -2.36 |
| 涨跌额 | 涨跌额(元) | -36.0 |
| 换手率 | 换手率(%) | 0.40 |

## 财务数据字段

`financial` 命令返回三张财务报表的合并数据，按年份组织。

### 资产负债表

| 字段 | 说明 |
|------|------|
| total_assets | 总资产 |
| current_assets | 流动资产 |
| non_current_assets | 非流动资产 |
| total_liabilities | 总负债 |
| current_liabilities | 流动负债 |
| non_current_liabilities | 非流动负债 |
| total_equity | 所有者权益 |
| cash_and_equivalents | 货币资金 |
| accounts_receivable | 应收账款 |
| inventory | 存货 |
| fixed_assets | 固定资产 |
| intangible_assets | 无形资产 |
| long_term_equity_invest | 长期股权投资 |

### 利润表

| 字段 | 说明 |
|------|------|
| total_revenue | 营业总收入 |
| operating_income | 营业收入 |
| total_operating_cost | 营业总成本 |
| operating_cost | 营业成本 |
| sales_expense | 销售费用 |
| management_expense | 管理费用 |
| financial_expense | 财务费用 |
| research_expense | 研发费用 |
| operating_profit | 营业利润 |
| total_profit | 利润总额 |
| net_profit | 净利润 |
| parent_net_profit | 归属母公司净利润 |
| income_tax | 所得税 |
| basic_eps | 基本每股收益 |
| gross_profit | 毛利润 |
| ebit | 息税前利润 |

### 现金流量表

| 字段 | 说明 |
|------|------|
| operating_cash_flow | 经营活动现金流 |
| investing_cash_flow | 投资活动现金流 |
| financing_cash_flow | 筹资活动现金流 |
| capital_expenditure | 资本支出 |
| free_cash_flow | 自由现金流 |
| cash_and_equivalents_end | 期末现金及等价物 |

## 直接查询指标 (东方财富)

这些指标由东方财富直接计算，通过 `stock_financial_analysis_indicator_em` 接口获取：

### 每股指标

| 代码 | 说明 |
|------|------|
| EPSJB | 基本每股收益(元) |
| EPSKCJB | 扣非每股收益(元) |
| EPSXS | 稀释每股收益(元) |
| BPS | 每股净资产(元) |
| MGZBGJ | 每股公积金(元) |
| MGWFPLR | 每股未分配利润(元) |
| MGJYXJJE | 每股经营现金流(元) |

### 盈利能力

| 代码 | 说明 |
|------|------|
| ROEJQ | 净资产收益率-加权(%) |
| ROEKCJQ | 净资产收益率-扣非/加权(%) |
| ZZCJLL | 总资产收益率-加权(%) |
| ROIC | 投资资本回报率(%) |
| XSJLL | 净利率(%) |
| XSMLL | 毛利率(%) |

### 成长能力

| 代码 | 说明 |
|------|------|
| TOTALOPERATEREVETZ | 营业总收入同比增长(%) |
| PARENTNETPROFITTZ | 归属净利润同比增长(%) |
| KCFJCXSYJLRTZ | 扣非净利润同比增长(%) |
| YYZSRGDHBZC | 营业总收入滚动环比增长(%) |
| NETPROFITRPHBZC | 归属净利润滚动环比增长(%) |

### 偿债能力

| 代码 | 说明 |
|------|------|
| LD | 流动比率 |
| SD | 速动比率 |
| XJLLB | 现金流量比率 |
| ZCFZL | 资产负债率(%) |
| QYCS | 权益系数 |
| CQBL | 产权比率 |

### 营运能力

| 代码 | 说明 |
|------|------|
| ZZCZZTS | 总资产周转天数(天) |
| CHZZTS | 存货周转天数(天) |
| YSZKZZTS | 应收账款周转天数(天) |
| TOAZZL | 总资产周转率(次) |
| CHZZL | 存货周转率(次) |
| YSZKZZL | 应收账款周转率(次) |
