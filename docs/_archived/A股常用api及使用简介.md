# Akshare 常用 API 及使用简介 - A 股

本文档整理了 Akshare 中常用的 A 股数据查询接口。

---

## 1. 个股信息查询 - 东财

**接口:** `stock_individual_info_em`

**目标地址:** http://quote.eastmoney.com/concept/sh603777.html?from=classic

**描述:** 东方财富 - 个股 - 股票信息

**限量:** 单次返回指定 symbol 的个股信息

### 输入参数

| 名称    | 类型   | 描述                           |
|---------|--------|--------------------------------|
| symbol  | str    | 股票代码，如 `603777`          |
| timeout | float  | 超时时间，默认 `None`          |

### 输出参数

| 名称  | 类型   | 描述 |
|-------|--------|------|
| item  | object | -    |
| value | object | -    |

### 接口示例

```python
import akshare as ak

stock_individual_info_em_df = ak.stock_individual_info_em(symbol="000001")
print(stock_individual_info_em_df)
```

---

## 2. 历史行情数据 - 东财

**接口:** `stock_zh_a_hist`

**目标地址:** https://quote.eastmoney.com/concept/sh603777.html (示例)

**描述:** 东方财富 - 沪深京 A 股日频率数据；历史数据按日频率更新，当日收盘价请在收盘后获取

**限量:** 单次返回指定沪深京 A 股上市公司、指定周期和指定日期间的历史行情日频率数据

### 输入参数

| 名称       | 类型   | 描述                                                                 |
|------------|--------|----------------------------------------------------------------------|
| symbol     | str    | 股票代码，可在 `ak.stock_zh_a_spot_em()` 中获取                      |
| period     | str    | 周期选择：`daily`（日线）、`weekly`（周线）、`monthly`（月线）       |
| start_date | str    | 开始查询日期，格式 `YYYYMMDD`，如 `20210301`                         |
| end_date   | str    | 结束查询日期，格式 `YYYYMMDD`，如 `20210616`                        |
| adjust     | str    | 复权类型：空字符串（默认不复权）、`qfq`（前复权）、`hfq`（后复权）    |
| timeout    | float  | 超时时间，默认 `None`                                                |

### 股票数据复权说明

由于股票存在配股、分拆、合并和发放股息等事件，会导致股价出现较大的缺口。若使用不复权的价格处理数据、计算各种指标，将会导致它们失去连续性，且使用不复权价格计算收益也会出现错误。为了保证数据连贯性，常通过前复权和后复权对价格序列进行调整。

#### 前复权

保持当前价格不变，将历史价格进行增减，从而使股价连续。前复权用来看盘非常方便，能一眼看出股价的历史走势，叠加各种技术指标也比较顺畅，是各种行情软件默认的复权方式。

这种方法虽然很常见，但也有两个缺陷需要注意：

1. 为了保证当前价格不变，每次股票除权除息，均需要重新调整历史价格，因此其历史价格是时变的。这会导致在不同时点看到的历史前复权价可能出现差异。
2. 对于有持续分红的公司来说，前复权价可能出现负值。

#### 后复权

保证历史价格不变，在每次股票权益事件发生后，调整当前的股票价格。后复权价格和真实股票价格可能差别较大，不适合用来看盘。

其优点在于，可以被看作投资者的长期财富增长曲线，反映投资者的真实收益率情况。**在量化投资研究中普遍采用后复权数据。**

### 输出参数

| 名称     | 类型    | 描述             |
|----------|---------|------------------|
| 日期     | object  | 交易日           |
| 股票代码 | object  | 不带市场标识的股票代码 |
| 开盘     | float64 | 开盘价           |
| 收盘     | float64 | 收盘价           |
| 最高     | float64 | 最高价           |
| 最低     | float64 | 最低价           |
| 成交量   | int64   | 成交量（单位：手）|
| 成交额   | float64 | 成交额（单位：元）|
| 振幅     | float64 | 振幅（单位：%）  |
| 涨跌幅   | float64 | 涨跌幅（单位：%）|
| 涨跌额   | float64 | 涨跌额（单位：元）|
| 换手率   | float64 | 换手率（单位：%）|

### 接口示例（不复权）

```python
import akshare as ak

stock_zh_a_hist_df = ak.stock_zh_a_hist(
    symbol="000001",
    period="daily",
    start_date="20170301",
    end_date="20240528",
    adjust=""
)
print(stock_zh_a_hist_df)
```

---

## 3. 资产负债表 - 按年度

**接口:** `stock_balance_sheet_by_yearly_em`

**目标地址:** https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0

**描述:** 东方财富 - 股票 - 财务分析 - 资产负债表 - 按年度

**限量:** 单次获取指定 symbol 的资产负债表 - 按年度数据

### 输入参数

| 名称   | 类型 | 描述                    |
|--------|------|-------------------------|
| symbol | str  | 股票代码，如 `SH600519` |

### 输出参数

共 319 项数据，不逐一列出。

### 接口示例

```python
import akshare as ak

stock_balance_sheet_by_yearly_em_df = ak.stock_balance_sheet_by_yearly_em(symbol="SH600519")
print(stock_balance_sheet_by_yearly_em_df)
```

---

## 4. 利润表 - 按年度

**接口:** `stock_profit_sheet_by_yearly_em`

**目标地址:** https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0

**描述:** 东方财富 - 股票 - 财务分析 - 利润表 - 按年度

**限量:** 单次获取指定 symbol 的利润表 - 按年度数据

### 输入参数

| 名称   | 类型 | 描述                    |
|--------|------|-------------------------|
| symbol | str  | 股票代码，如 `SH600519` |

### 输出参数

共 203 项数据，不逐一列出。

### 接口示例

```python
import akshare as ak

stock_profit_sheet_by_yearly_em_df = ak.stock_profit_sheet_by_yearly_em(symbol="SH600519")
print(stock_profit_sheet_by_yearly_em_df)
```

---

## 5. 现金流量表 - 按年度

**接口:** `stock_cash_flow_sheet_by_yearly_em`

**目标地址:** https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0

**描述:** 东方财富 - 股票 - 财务分析 - 现金流量表 - 按年度

**限量:** 单次获取指定 symbol 的现金流量表 - 按年度数据

### 输入参数

| 名称   | 类型 | 描述                    |
|--------|------|-------------------------|
| symbol | str  | 股票代码，如 `SH600519` |

### 输出参数

共 314 项数据，不逐一列出。

### 接口示例

```python
import akshare as ak

stock_cash_flow_sheet_by_yearly_em_df = ak.stock_cash_flow_sheet_by_yearly_em(symbol="SH600519")
print(stock_cash_flow_sheet_by_yearly_em_df)
```

---

## 6. 主要指标 - 东方财富

**接口:** `stock_financial_analysis_indicator_em`

**目标地址:** https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code=SZ301389&color=b#/cwfx

**描述:** 东方财富 - A股 - 财务分析 - 主要指标

**限量:** 单次获取指定 symbol 的所有数据

### 输入参数

| 名称      | 类型 | 描述                                      |
|-----------|------|-------------------------------------------|
| symbol    | str  | 股票代码，如 `301389.SZ`                  |
| indicator | str  | 指标类型：`按报告期` 或 `按单季度`        |

### 输出参数

| 名称                   | 类型    | 描述                     |
|------------------------|---------|--------------------------|
| SECUCODE               | object  | 股票代码（带后缀）       |
| SECURITY_CODE          | object  | 股票代码                 |
| SECURITY_NAME_ABBR     | object  | 股票名称                 |
| REPORT_DATE            | object  | 报告日期                 |
| REPORT_TYPE            | object  | 报告类型                 |
| REPORT_DATE_NAME       | object  | 报告日期名称             |
| EPSJB                 | float64 | 基本每股收益（元）       |
| EPSKCJB               | float64 | 扣非每股收益（元）        |
| EPSXS                 | float64 | 稀释每股收益（元）       |
| BPS                   | float64 | 每股净资产（元）         |
| MGZBGJ                | float64 | 每股公积金（元）         |
| MGWFPLR               | float64 | 每股未分配利润（元）     |
| MGJYXJJE              | float64 | 每股经营现金流（元）     |
| TOTALOPERATEREVE      | float64 | 营业总收入（元）         |
| MLR                   | float64 | 毛利润（元）             |
| PARENTNETPROFIT       | float64 | 归属净利润（元）         |
| KCFJCXSYJLR           | float64 | 扣非净利润（元）         |
| TOTALOPERATEREVETZ    | float64 | 营业总收入同比增长（%）  |
| PARENTNETPROFITTZ     | float64 | 归属净利润同比增长（%）  |
| KCFJCXSYJLRTZ        | float64 | 扣非净利润同比增长（%）  |
| YYZSRGDHBZC          | float64 | 营业总收入滚动环比增长（%）|
| NETPROFITRPHBZC       | float64 | 归属净利润滚动环比增长（%）|
| KFJLRGDHBZC          | float64 | 扣非净利润滚动环比增长（%）|
| ROEJQ                 | float64 | 净资产收益率（加权）（%）|
| ROEKCJQ               | float64 | 净资产收益率（扣非/加权）（%）|
| ZZCJLL               | float64 | 总资产收益率（加权）（%） |
| XSJLL                 | float64 | 净利率（%）              |
| XSMLL                 | float64 | 毛利率（%）              |
| YSZKYYSR              | float64 | 预收账款/营业收入         |
| XSJXLYYSR            | float64 | 销售净现金流/营业收入    |
| JYXJLYYSR            | float64 | 经营净现金流/营业收入    |
| TAXRATE               | float64 | 实际税率（%）            |
| LD                    | float64 | 流动比率                 |
| SD                    | float64 | 速动比率                 |
| XJLLB                 | float64 | 现金流量比率             |
| ZCFZL                 | float64 | 资产负债率（%）          |
| QYCS                  | float64 | 权益系数                 |
| CQBL                  | float64 | 产权比率                 |
| ZZCZZTS               | float64 | 总资产周转天数（天）     |
| CHZZTS                | float64 | 存货周转天数（天）       |
| YSZKZZTS              | float64 | 应收账款周转天数（天）   |
| TOAZZL                | float64 | 总资产周转率（次）       |
| CHZZL                 | float64 | 存货周转率（次）         |
| YSZKZZL               | float64 | 应收账款周转率（次）     |
| ...                   | ...     | ...                     |

### 接口示例

```python
import akshare as ak

stock_financial_analysis_indicator_em_df = ak.stock_financial_analysis_indicator_em(
    symbol="301389.SZ",
    indicator="按报告期"
)
print(stock_financial_analysis_indicator_em_df)
```
