# Akshare 常用 API 及使用简介 - 美股

本文档整理了 Akshare 中常用的美股数据查询接口。行情和财务数据来源于**东方财富**，个股信息来源于**雪球**。

---

## 1. 美股个股信息 - 雪球

**接口:** `stock_individual_basic_info_xq`

**目标地址:** https://xueqiu.com/S/AAPL

**描述:** 雪球 - 个股基本信息查询，支持 A 股、港股和美股

**限量:** 单次返回指定股票的个股基本信息

### 输入参数

| 名称   | 类型   | 描述                                                                      |
|--------|--------|---------------------------------------------------------------------------|
| symbol | str    | 股票代码，如 `AAPL`（美股）、`TSLA`（美股）、`BABA`（美股中概股）、`00700`（港股） |

### 输出参数

返回包含以下字段的 DataFrame：

| 名称        | 类型   | 描述           |
|-------------|--------|----------------|
| item        | object | 信息项目       |
| value       | object | 信息值         |

包含公司概况、员工人数、公司介绍等信息。

### 接口示例

```python
import akshare as ak

# 获取苹果公司基本信息
stock_individual_basic_info_xq_df = ak.stock_individual_basic_info_xq(symbol="AAPL")
print(stock_individual_basic_info_xq_df)

# 获取特斯拉基本信息
stock_individual_basic_info_xq_df = ak.stock_individual_basic_info_xq(symbol="TSLA")
print(stock_individual_basic_info_xq_df)

# 获取阿里巴巴基本信息
stock_individual_basic_info_xq_df = ak.stock_individual_basic_info_xq(symbol="BABA")
print(stock_individual_basic_info_xq_df)
```

---

## 2. 美股实时行情 - 东方财富

**接口:** `stock_us_hist`

**目标地址:** http://quote.eastmoney.com/us/ENTX.html#fullScreenChart

**描述:** 东方财富 - 美股历史行情数据；设定 `adjust="qfq"` 则返回前复权的数据，hfq"` 则设定 `adjust="返回后复权的数据；默认返回未复权的数据；历史数据按日频率更新

**限量:** 单次返回指定上市公司的指定周期和指定日期间的历史行情日频率数据

### 输入参数

| 名称       | 类型   | 描述                                                                 |
|------------|--------|----------------------------------------------------------------------|
| symbol     | str    | 股票代码，如 `AAPL`、`TSLA`、`BABA`                                    |
| period     | str    | 周期选择：`daily`（日线）、`weekly`（周线）、`monthly`（月线）       |
| start_date | str    | 开始查询日期，格式 `YYYYMMDD`，如 `20170301`                         |
| end_date   | str    | 结束查询日期，格式 `YYYYMMDD`，如 `20240528`                        |
| adjust     | str    | 复权类型：空字符串（默认不复权）、`qfq`（前复权）、`hfq`（后复权）    |

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
| 股票代码 | object  | 股票代码 |
| 开盘     | float64 | 开盘价           |
| 收盘     | float64 | 收盘价           |
| 最高     | float64 | 最高价           |
| 最低     | float64 | 最低价           |
| 成交量   | int64   | 成交量（单位：股）|
| 成交额   | float64 | 成交额（单位：美元）|
| 振幅     | float64 | 振幅（单位：%）  |
| 涨跌幅   | float64 | 涨跌幅（单位：%）|
| 涨跌额   | float64 | 涨跌额（单位：美元）|
| 换手率   | float64 | 换手率（单位：%）|

### 接口示例（不复权）

```python
import akshare as ak

stock_us_hist_df = ak.stock_us_hist(
    symbol="AAPL",
    period="daily",
    start_date="20170301",
    end_date="20240528",
    adjust=""
)
print(stock_us_hist_df)
```

### 接口示例（前复权）

```python
import akshare as ak

stock_us_hist_qfq_df = ak.stock_us_hist(
    symbol="AAPL",
    period="daily",
    start_date="20170301",
    end_date="20240528",
    adjust="qfq"
)
print(stock_us_hist_qfq_df)
```

---

## 5. 美股财务报表 - 东方财富

**接口:** `stock_financial_us_report_em`

**目标地址:** https://emweb.eastmoney.com/PC_USF10/pages/index.html?code=TSLA&type=web&color=w#/cwfx

**描述:** 东方财富 - 美股 - 财务分析 - 三大报表（资产负债表、综合损益表、现金流量表）

**限量:** 单次获取指定美股公司的财务报表数据

### 输入参数

| 名称      | 类型 | 描述                                      |
|-----------|------|-------------------------------------------|
| stock     | str  | 股票代码，如 `TSLA`、`AAPL`、`BABA`       |
| symbol    | str  | 报表类型：`资产负债表`、`综合损益表`、`现金流量表` |
| indicator | str  | 报告类型：`年报`、`单季报`、`累计季报`    |

### 输出参数

返回包含以下字段的 DataFrame：

| 名称            | 类型    | 描述             |
|-----------------|---------|------------------|
| SECUCODE        | object  | 股票代码（带后缀）|
| SECURITY_CODE   | object  | 股票代码         |
| SECURITY_NAME   | object  | 股票名称         |
| REPORT_DATE     | object  | 报告日期         |
| REPORT_TYPE     | object  | 报告类型         |
| STD_ITEM_CODE   | object  | 会计科目代码     |
| AMOUNT          | float64 | 金额             |
| ITEM_NAME       | object  | 会计科目名称     |

### 接口示例

```python
import akshare as ak

# 获取特斯拉资产负债表（年报）
stock_financial_us_report_em_df = ak.stock_financial_us_report_em(
    stock="TSLA",
    symbol="资产负债表",
    indicator="年报"
)
print(stock_financial_us_report_em_df)

# 获取阿里巴巴综合损益表（单季报）
stock_financial_us_report_em_df = ak.stock_financial_us_report_em(
    stock="BABA",
    symbol="综合损益表",
    indicator="单季报"
)
print(stock_financial_us_report_em_df)

# 获取苹果公司现金流量表（累计季报）
stock_financial_us_report_em_df = ak.stock_financial_us_report_em(
    stock="AAPL",
    symbol="现金流量表",
    indicator="累计季报"
)
print(stock_financial_us_report_em_df)
```

---

## 6. 美股财务指标 - 东方财富

**接口:** `stock_financial_us_analysis_indicator_em`

**目标地址:** https://emweb.eastmoney.com/PC_USF10/pages/index.html?code=TSLA&type=web&color=w#/cwfx

**描述:** 东方财富 - 美股 - 财务分析 - 主要指标

**限量:** 单次获取指定美股公司的主要财务指标数据

### 输入参数

| 名称      | 类型 | 描述                                      |
|-----------|------|-------------------------------------------|
| symbol    | str  | 股票代码，如 `TSLA`、`AAPL`、`BABA`       |
| indicator | str  | 报告类型：`年报`、`单季报`、`累计季报`    |

### 输出参数

返回包含以下主要字段的 DataFrame：

| 名称                   | 类型    | 描述                     |
|------------------------|---------|--------------------------|
| SECURITY_CODE          | object  | 股票代码                 |
| SECURITY_NAME_ABBR     | object  | 股票名称                 |
| REPORT_DATE            | object  | 报告日期                 |
| TOTAL_INCOME           | float64 | 营业总收入               |
| TOTAL_INCOME_YOY       | float64 | 营业总收入同比增长（%）  |
| PARENT_HOLDER_NETPROFIT| float64 | 归属净利润               |
| PARENT_HOLDER_NETPROFIT_YOY | float64 | 归属净利润同比增长（%） |
| BASIC_EPS_CS           | float64 | 基本每股收益             |
| BASIC_EPS_CS_YOY       | float64 | 基本每股收益同比增长（%）|
| DILUTED_EPS_CS         | float64 | 稀释每股收益             |
| ROE                    | float64 | 净资产收益率（%）        |
| ROE_YOY                | float64 | 净资产收益率同比增长（%）|
| ROA                    | float64 | 总资产收益率（%）        |
| ROA_YOY                | float64 | 总资产收益率同比增长（%）|
| DEBT_RATIO             | float64 | 资产负债率（%）          |
| DEBT_RATIO_YOY         | float64 | 资产负债率同比增长（%）  |
| EQUITY_RATIO           | float64 | 权益比率                 |

### 接口示例

```python
import akshare as ak

# 获取特斯拉主要财务指标（年报）
stock_financial_us_analysis_indicator_em_df = ak.stock_financial_us_analysis_indicator_em(
    symbol="TSLA",
    indicator="年报"
)
print(stock_financial_us_analysis_indicator_em_df)

# 获取阿里巴巴主要财务指标（单季报）
stock_financial_us_analysis_indicator_em_df = ak.stock_financial_us_analysis_indicator_em(
    symbol="BABA",
    indicator="单季报"
)
print(stock_financial_us_analysis_indicator_em_df)

# 获取苹果公司主要财务指标（累计季报）
stock_financial_us_analysis_indicator_em_df = ak.stock_financial_us_analysis_indicator_em(
    symbol="AAPL",
    indicator="累计季报"
)
print(stock_financial_us_analysis_indicator_em_df)
```

---
