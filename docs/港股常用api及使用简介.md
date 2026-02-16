# Akshare 常用 API 及使用简介 - 港股

本文档整理了 Akshare 中常用的港股数据查询接口。

---

## 2. 历史行情数据 - 东财

**接口:** `stock_zh_hk_hist_em`

**目标地址:** https://quote.eastmoney.com/hk/00001.html

**描述:** 东方财富 - 沪深京 A 股日频率数据；历史数据按日频率更新，当日收盘价请在收盘后获取

**限量:** 单次返回指定港股上市公司、指定周期和指定日期间的历史行情日频率数据

### 输入参数

| 名称       | 类型   | 描述                                                                 |
|------------|--------|----------------------------------------------------------------------|
| symbol     | str    | 港股代码，如 `00001`（无需前缀）                                      |
| period     | str    | 周期选择：`daily`（日线）、`weekly`（周线）、`monthly`（月线）       |
| start_date | str    | 开始查询日期，格式 `YYYYMMDD`，如 `20210101`                         |
| end_date   | str    | 结束查询日期，格式 `YYYYMMDD`，如 `20210616`                        |
| adjust     | str    | 复权类型：空字符串（默认不复权）、`qfq`（前复权）、`hfq`（后复权）    |

### 港股数据复权说明

港股与 A 股类似，存在配股、分拆、合并和发放股息等事件会导致股价出现缺口。Akshare 提供了前复权和后复权两种方式来调整价格序列。

#### 前复权

保持当前价格不变，将历史价格进行增减，从而使股价连续。前复权用来看盘非常方便，能一眼看出股价的历史走势。

#### 后复权

保证历史价格不变，在每次股票权益事件发生后，调整当前的股票价格。后复权价格可以反映投资者的真实收益率情况。

### 输出参数

| 名称     | 类型    | 描述             |
|----------|---------|------------------|
| 日期     | object  | 交易日           |
| 股票代码 | object  | 港股代码         |
| 开盘     | float64 | 开盘价           |
| 收盘     | float64 | 收盘价           |
| 最高     | float64 | 最高价           |
| 最低     | float64 | 最低价           |
| 成交量   | int64   | 成交量           |
| 成交额   | float64 | 成交额           |
| 振幅     | float64 | 振幅（单位：%）  |
| 涨跌幅   | float64 | 涨跌幅（单位：%）|
| 涨跌额   | float64 | 涨跌额           |
| 换手率   | float64 | 换手率（单位：%）|

### 接口示例

```python
import akshare as ak

stock_zh_hk_hist_em_df = ak.stock_zh_hk_hist_em(
    symbol="00001",
    period="daily",
    start_date="20210101",
    end_date="20210616",
    adjust=""
)
print(stock_zh_hk_hist_em_df)
```

---

## 4. 财务指标 - 东方财富

**接口:** `stock_hk_financial_indicator_em`

**目标地址:** https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=hk00001

**描述:** 东方财富 - 港股 - 财务分析 - 主要指标

**限量:** 单次获取指定港股的财务指标数据

### 输入参数

| 名称   | 类型 | 描述                |
|--------|------|---------------------|
| symbol | str  | 港股代码，如 `00001` |

### 输出参数

| 名称               | 类型    | 描述                     |
|--------------------|---------|--------------------------|
| 股票代码           | object  | 港股代码                 |
| 股票名称           | object  | 港股名称                 |
| 报告日期           | object  | 报告日期                 |
| 报告类型           | object  | 报告类型                 |
| 每股收益           | float64 | 每股收益（元）           |
| 每股净资产         | float64 | 每股净资产（元）         |
| 净资产收益率       | float64 | 净资产收益率（%）         |
| 净利润             | float64 | 净利润                   |
| 净利润同比增长     | float64 | 净利润同比增长（%）      |
| 营业总收入         | float64 | 营业总收入               |
| 营业总收入同比增长 | float64 | 营业总收入同比增长（%） |
| ...               | ...     | ...                     |

### 接口示例

```python
import akshare as ak

stock_hk_financial_indicator_em_df = ak.stock_hk_financial_indicator_em(symbol="00001")
print(stock_hk_financial_indicator_em_df)
```

---

## 5. 财务报表 - 东方财富

**接口:** `stock_hk_financial_report_em`

**目标地址:** https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=hk00001

**描述:** 东方财富 - 港股 - 财务报表（合并报表）

**限量:** 单次获取指定港股的财务报表数据

### 输入参数

| 名称   | 类型 | 描述                |
|--------|------|---------------------|
| symbol | str  | 港股代码，如 `00001` |
| indicator | str | 报表类型：`利润表`、`资产负债表`、`现金流量表` |

### 输出参数

包含资产负债表、利润表、现金流量表的主要数据项，具体字段根据报表类型而定。

### 接口示例

```python
import akshare as ak

# 获取利润表
stock_hk_financial_report_em_df = ak.stock_hk_financial_report_em(
    symbol="00001",
    indicator="利润表"
)
print(stock_hk_financial_report_em_df)
```

---

## 6. 个股资料 - 东方财富

**接口:** `stock_hk_company_profile_em`

**目标地址:** https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code=hk00001&color=b#/gszl

**描述:** 东方财富 - 港股 - 公司资料

**限量:** 单次获取指定港股的公司资料

### 输入参数

| 名称   | 类型 | 描述                |
|--------|------|---------------------|
| symbol | str  | 港股代码，如 `00001` |

### 输出参数

| 名称          | 类型   | 描述         |
|---------------|--------|--------------|
| 公司名称      | object | 公司全称     |
| 英文名称      | object | 公司英文名称 |
| 所属行业      | object | 所属行业     |
| 上市日期      | object | 上市日期     |
| 总股本        | object | 总股本       |
| 港股股本      | object | 港股股本     |
| 市值          | object | 市值         |
| 港股市值      | object | 港股市值     |
| 市盈率        | object | 市盈率       |
| 市净率        | object | 市净率       |
| 主席          | object | 公司主席     |
| 行政总裁      | object | 行政总裁     |
| 注册地址      | object | 注册地址     |
| 办公地址      | object | 办公地址     |
| 公司简介      | object | 公司简介     |
| ...          | ...    | ...          |

### 接口示例

```python
import akshare as ak

stock_hk_company_profile_em_df = ak.stock_hk_company_profile_em(symbol="00001")
print(stock_hk_company_profile_em_df)
```

---

## 7. 分红派息 - 东方财富

**接口:** `stock_hk_dividend_payout_em`

**目标地址:** https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code=hk00001&color=b#/fhsp

**描述:** 东方财富 - 港股 - 分红派息

**限量:** 单次获取指定港股的历史分红派息数据

### 输入参数

| 名称   | 类型 | 描述                |
|--------|------|---------------------|
| symbol | str  | 港股代码，如 `00001` |

### 输出参数

| 名称         | 类型   | 描述       |
|--------------|--------|------------|
| 公告日期     | object | 公告日期   |
| 派息日       | object | 派息日     |
| 拆细日       | object | 拆细日     |
| 红利         | object | 红利       |
| 红股         | object | 红股       |
| 配股         | object | 配股       |
| 配股价       | object | 配股价     |
| ...         | ...    | ...        |

### 接口示例

```python
import akshare as ak

stock_hk_dividend_payout_em_df = ak.stock_hk_dividend_payout_em(symbol="00001")
print(stock_hk_dividend_payout_em_df)
```

---
