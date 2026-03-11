# 各市场财务指标详细列表

本文档列出A股、港股、美股市场通过akshare可获取的财务指标，供开发参考。

---

## A股 - 主要指标

**接口**: `stock_financial_analysis_indicator_em(symbol="000001.SZ", indicator="按报告期")`

**返回字段** (共140个):

### 基础信息 (14个)
| 字段名 | 中文名称 |
|--------|----------|
| SECUCODE | 股票代码(带后缀) |
| SECURITY_CODE | 股票代码 |
| SECURITY_NAME_ABBR | 股票名称 |
| ORG_CODE | 机构代码 |
| ORG_TYPE | 机构类型 |
| REPORT_DATE | 报告日期 |
| REPORT_TYPE | 报告类型 |
| REPORT_DATE_NAME | 报告日期名称 |
| SECURITY_TYPE_CODE | 证券类型代码 |
| NOTICE_DATE | 公告日期 |
| UPDATE_DATE | 更新日期 |
| CURRENCY | 币种 |
| REPORT_YEAR | 报告年度 |

### 每股收益类 (3个)
| 字段名 | 中文名称 |
|--------|----------|
| EPSJB | 基本每股收益(元) |
| EPSKCJB | 扣非每股收益(元) |
| EPSXS | 稀释每股收益(元) |

### 每股净资产/公积类 (5个)
| 字段名 | 中文名称 |
|--------|----------|
| BPS | 每股净资产(元) |
| MGZBGJ | 每股公积金(元) |
| MGWFPLR | 每股未分配利润(元) |
| MGJYXJJE | 每股经营现金流(元) |

### 收入/利润类 (9个)
| 字段名 | 中文名称 |
|--------|----------|
| TOTALOPERATEREVE | 营业总收入(元) |
| MLR | 毛利润(元) |
| PARENTNETPROFIT | 归属净利润(元) |
| KCFJCXSYJLR | 扣非净利润(元) |
| TOTALOPERATEREVETZ | 营业总收入同比增长(%) |
| PARENTNETPROFITTZ | 归属净利润同比增长(%) |
| KCFJCXSYJLRTZ | 扣非净利润同比增长(%) |
| YYZSRGDHBZC | 营业总收入滚动环比增长(%) |
| NETPROFITRPHBZC | 归属净利润滚动环比增长(%) |
| KFJLRGDHBZC | 扣非净利润滚动环比增长(%) |

### 盈利能力 (5个)
| 字段名 | 中文名称 |
|--------|----------|
| ROEJQ | 净资产收益率-加权(%) |
| ROEKCJQ | 净资产收益率-扣非/加权(%) |
| ZZCJLL | 总资产收益率-加权(%) |
| XSJLL | 净利率(%) |
| XSMLL | 毛利率(%) |

### 流动性比率 (3个)
| 字段名 | 中文名称 |
|--------|----------|
| LD | 流动比率 |
| SD | 速动比率 |
| XJLLB | 现金流量比率 |

### 杠杆/偿债能力 (3个)
| 字段名 | 中文名称 |
|--------|----------|
| ZCFZL | 资产负债率(%) |
| QYCS | 权益系数 |
| CQBL | 产权比率 |

### 周转效率 (6个)
| 字段名 | 中文名称 |
|--------|----------|
| ZZCZZTS | 总资产周转天数(天) |
| CHZZTS | 存货周转天数(天) |
| YSZKZZTS | 应收账款周转天数(天) |
| TOAZZL | 总资产周转率(次) |
| CHZZL | 存货周转率(次) |
| YSZKZZL | 应收账款周转率(次) |

### 现金流相关 (3个)
| 字段名 | 中文名称 |
|--------|----------|
| YSZKYYSR | 预收账款/营业收入 |
| XSJXLYYSR | 销售净现金流/营业收入 |
| JYXJLYYSR | 经营净现金流/营业收入 |

### 税率 (1个)
| 字段名 | 中文名称 |
|--------|----------|
| TAXRATE | 实际税率(%) |

### 银行专用指标 (28个)
| 字段名 | 中文名称 |
|--------|----------|
| TOTALDEPOSITS | 存款总额 |
| GROSSLOANS | 贷款总额 |
| LTDRR | 长期贷款率 |
| NEWCAPITALADER | 核心资本补充 |
| HXYJBCZL | 核心资本充足率 |
| NONPERLOAN | 不良贷款 |
| BLDKBBL | 不良贷款拨备覆盖率 |
| NZBJE | 拨备覆盖率 |
| TOTAL_ROI | 总投资收益率 |
| NET_ROI | 净投资收益 |
| EARNED_PREMIUM | 已赚保费 |
| COMPENSATE_EXPENSE | 赔付支出 |
| SURRENDER_RATE_LIVE | 退保率(人身险) |
| SOLVENCY_AR | 偿付能力充足率 |

### 增长类指标 (18个)
| 字段名 | 中文名称 |
|--------|----------|
| EPSJBTZ | 基本每股收益增长(%) |
| BPSTZ | 每股净资产增长(%) |
| MGZBGJTZ | 每股公积金增长(%) |
| MGWFPLRTZ | 每股未分配利润增长(%) |
| MGJYXJJETZ | 每股经营现金流增长(%) |
| ROEJQTZ | 净资产收益率增长(%) |
| ZZCJLLTZ | 总资产收益率增长(%) |
| ZCFZLTZ | 资产负债率增长(%) |
| ROICTZ | ROIC增长(%) |
| DJD_TOI_YOY | 营收同比增长(%) |
| DJD_DPNP_YOY | 净利润同比增长(%) |
| DJD_DEDUCTDPNP_YOY | 扣非净利润同比增长(%) |
| DJD_TOI_QOQ | 营收环比增长(%) |
| DJD_DPNP_QOQ | 净利润环比增长(%) |
| DJD_DEDUCTDPNP_QOQ | 扣非净利润环比增长(%) |

### 估值指标 (4个)
| 字段名 | 中文名称 |
|--------|----------|
| PER_TOI | 市销率 |
| PER_OI | 市现率 |
| PER_EBIT | 市盈率(EBIT) |

### 运营效率 (10个)
| 字段名 | 中文名称 |
|--------|----------|
| STAFF_NUM | 员工人数 |
| AVG_TOI | 人均营收 |
| AVG_NET_PROFIT | 人均净利润 |
| PREPAID_ACCOUNTS_RATIO | 预付账款占比 |
| ACCOUNTS_PAYABLE_TR | 应付账款周转率 |
| FIXED_ASSET_TR | 固定资产周转率 |
| CURRENT_ASSET_TR | 流动资产周转率 |
| PREPAID_ACCOUNTS_TDAYS | 预付账款周转天数 |
| PAYABLE_TDAYS | 应付账款周转天数 |
| OPERATE_CYCLE | 营业周期 |

### 风险指标 (5个)
| 字段名 | 中文名称 |
|--------|----------|
| GUARD_SPEED_RATIO | 保守速动比率 |
| CASH_RATIO | 现金比率 |
| INTEREST_COVERAGE_RATIO | 利息保障倍数 |
| CA_TA | 现金/总资产 |
| NCA_TA | 非现金资产/总资产 |

### 长期偿债 (8个)
| 字段名 | 中文名称 |
|--------|----------|
| LIQUIDATION_RATIO | 清算价值比率 |
| INTEREST_DEBT_RATIO | 带息负债率 |
| FC_LIABILITIES | 自由负债 |
| FCFF_FORWARD | 企业自由现金流(前瞻) |
| FCFF_BACK | 企业自由现金流(回顾) |
| SS_OI | 股东权益/营业收入 |
| SS_TA | 股东权益/总资产 |
| NCO_OP | 净资本/营业收入 |

### 更多财务指标 (24个)
| 字段名 | 中文名称 |
|--------|----------|
| NCO_NETPROFIT | 净资本/净利润 |
| NCO_FIXED | 净资本/固定资产 |
| FIRST_ADEQUACY_RATIO | 偿付能力充足率(之一) |
| NET_INTEREST_SPREAD | 净利差 |
| NET_INTEREST_MARGIN | 净息差 |
| LOAN_ADVANCES | 垫款 |
| NON_PERFORMING_LOAN | 不良贷款额 |
| OVERDUE_LOANS | 逾期贷款 |
| LOAN_PROVISION_RATIO | 贷款拨备率 |
| REVENUE_RATIO | 保险业务收入占比 |
| LIABILITY | 负债合计 |
| CAPITAL_PROVISIONS_SUM | 资本公积合计 |
| RISK_COVERAGE | 风险覆盖率 |
| CAPITAL_LEVERAGE_RATIO | 资本杠杆率 |
| LIQUIDITY_COVERAGE_RATIO | 流动性覆盖率 |
| NET_FUNDING_RATIO | 净稳定资金比率 |
| NET_CAPITAL_LIABILITIES | 净资本/负债 |
| NET_ASSETS_LIABILITIES | 净资产/负债 |
| PROPRIETARY_CAPITAL | 固有资本 |

### ROIC相关 (4个)
| 字段名 | 中文名称 |
|--------|----------|
| ROIC | 投资资本回报率(%) |
| NBV_LIFE | 寿险内含价值 |
| NBV_RATE | 新业务价值率 |
| NHJZ_CURRENT_AMT | 年化投资收益额 |

### 保险专用 (7个)
| 字段名 | 中文名称 |
|--------|----------|
| JZB | 保费收入 |
| JZC | 提取保险责任准备金 |
| JZBJZC | 已赚保费/提取责任准备金 |
| ZYGPGMJZC | 油气资产/总资产 |
| ZYGDSYLZQJZB | 油气资产/营业收入 |
| YYFXZB | 保险业务收入占比 |
| JJYWFXZB | 证券投资基金占比 |
| ZQZYYWFXZB | 证券投资业务占比 |
| RZRQYWFXZB | 融资融券业务占比 |

---

## 港股 - 主要指标

**接口**: `stock_hk_financial_indicator_em(symbol="00001")`

**返回字段** (共21个):

| 字段名 | 中文名称 |
|--------|----------|
| 基本每股收益(元) | 基本每股收益 |
| 每股净资产(元) | 每股净资产 |
| 法定股本(股) | 法定股本 |
| 每手股 | 每手股数 |
| 每股股息TTM(港元) | 每股股息TTM |
| 派息比率(%) | 派息比率 |
| 已发行股本(股) | 已发行股本 |
| 已发行股本-H股(股) | 已发行H股股本 |
| 每股经营现金流(元) | 每股经营现金流 |
| 股息率TTM(%) | 股息率TTM |
| 总市值(港元) | 总市值 |
| 港股市值(港元) | 港股市值 |
| 营业总收入 | 营业总收入 |
| 营业总收入滚动环比增长(%) | 营收滚动环比增长 |
| 销售净利率(%) | 销售净利率 |
| 净利润 | 净利润 |
| 净利润滚动环比增长(%) | 净利润滚动环比增长 |
| 股东权益回报率(%) | 股东权益回报率 |
| 市盈率 | 市盈率 |
| 市净率 | 市净率 |
| 总资产回报率(%) | 总资产回报率 |

---

## 美股 - 主要指标

**接口**: `stock_financial_us_analysis_indicator_em(symbol="AAPL", indicator="年报")`

**返回字段** (共47个):

### 基础信息 (20个)
| 字段名 | 中文名称 |
|--------|----------|
| SECUCODE | 股票代码(带后缀) |
| SECURITY_CODE | 股票代码 |
| SECURITY_NAME_ABBR | 股票名称 |
| ORG_CODE | 机构代码 |
| SECURITY_INNER_CODE | 证券内部代码 |
| ACCOUNTING_STANDARDS | 会计准则 |
| NOTICE_DATE | 公告日期 |
| START_DATE | 开始日期 |
| REPORT_DATE | 报告日期 |
| FINANCIAL_DATE | 财务日期 |
| STD_REPORT_DATE | 标准报告日期 |
| CURRENCY | 币种 |
| DATE_TYPE | 日期类型 |
| DATE_TYPE_CODE | 日期类型代码 |
| REPORT_TYPE | 报告类型 |
| REPORT_DATA_TYPE | 报告数据类型 |
| ORGTYPE | 机构类型 |
| CURRENCY_ABBR | 货币缩写 |

### 收入利润 (8个)
| 字段名 | 中文名称 |
|--------|----------|
| OPERATE_INCOME | 营业收入 |
| OPERATE_INCOME_YOY | 营业收入同比增长(%) |
| GROSS_PROFIT | 毛利润 |
| GROSS_PROFIT_YOY | 毛利润同比增长(%) |
| PARENT_HOLDER_NETPROFIT | 归属净利润 |
| PARENT_HOLDER_NETPROFIT_YOY | 归属净利润同比增长(%) |
| BASIC_EPS | 基本每股收益 |
| DILUTED_EPS | 稀释每股收益 |

### 盈利能力 (4个)
| 字段名 | 中文名称 |
|--------|----------|
| GROSS_PROFIT_RATIO | 毛利率(%) |
| NET_PROFIT_RATIO | 净利率(%) |
| ROE_AVG | 净资产收益率-平均(%) |
| ROA | 总资产收益率(%) |

### 周转效率 (6个)
| 字段名 | 中文名称 |
|--------|----------|
| ACCOUNTS_RECE_TR | 应收账款周转率 |
| INVENTORY_TR | 存货周转率 |
| TOTAL_ASSETS_TR | 总资产周转率 |
| ACCOUNTS_RECE_TDAYS | 应收账款周转天数 |
| INVENTORY_TDAYS | 存货周转天数 |
| TOTAL_ASSETS_TDAYS | 总资产周转天数 |

### 流动性 (3个)
| 字段名 | 中文名称 |
|--------|----------|
| CURRENT_RATIO | 流动比率 |
| SPEED_RATIO | 速动比率 |
| OCF_LIQDEBT | 经营现金流/流动负债 |

### 杠杆 (3个)
| 字段名 | 中文名称 |
|--------|----------|
| DEBT_ASSET_RATIO | 资产负债率(%) |
| EQUITY_RATIO | 权益比率 |

### 增长类 (7个)
| 字段名 | 中文名称 |
|--------|----------|
| BASIC_EPS_YOY | 基本每股收益同比增长(%) |
| GROSS_PROFIT_RATIO_YOY | 毛利率同比增长(%) |
| NET_PROFIT_RATIO_YOY | 净利率同比增长(%) |
| ROE_AVG_YOY | ROE同比增长(%) |
| ROA_YOY | ROA同比增长(%) |
| DEBT_ASSET_RATIO_YOY | 资产负债率同比增长(%) |
| CURRENT_RATIO_YOY | 流动比率同比增长(%) |
| SPEED_RATIO_YOY | 速动比率同比增长(%) |

---

## 指标覆盖对比

| 指标类别 | A股 | 港股 | 美股 |
|----------|-----|------|------|
| 每股收益 | ✓ (3个) | ✓ | ✓ (2个) |
| 每股净资产 | ✓ | ✓ | - |
| 每股公积金 | ✓ | - | - |
| 每股未分配利润 | ✓ | - | - |
| 每股经营现金流 | ✓ | ✓ | - |
| 营业收入 | ✓ | ✓ | ✓ |
| 毛利润 | ✓ | - | ✓ |
| 净利润 | ✓ | ✓ | ✓ |
| ROE | ✓ (2个) | ✓ | ✓ |
| ROA | ✓ | ✓ | ✓ |
| 毛利率 | ✓ | - | ✓ |
| 净利率 | ✓ | ✓ | ✓ |
| 流动比率 | ✓ | - | ✓ |
| 速动比率 | ✓ | - | ✓ |
| 资产负债率 | ✓ | - | ✓ |
| 存货周转率 | ✓ | - | ✓ |
| 应收账款周转率 | ✓ | - | ✓ |
| 总资产周转率 | ✓ | - | ✓ |
| 营收增长率 | ✓ | ✓ | ✓ |
| 净利润增长率 | ✓ | ✓ | ✓ |
| 市盈率 | - | ✓ | - |
| 市净率 | - | ✓ | - |
| 股息率 | - | ✓ | - |
| 银行/保险专用 | 50+ | - | - |

---

## 后续开发参考

1. **标准化映射**: 如需统一各市场指标，建议创建字段映射表，缺失字段返回null
2. **市场区分**: 自有计算指标应标注市场适用范围
3. **缓存策略**: 财务指标建议与财务报表使用相同的TTL策略(次年6月底)

---

## Indicator Registry 使用

项目提供了Indicator Registry来管理财务指标元数据：

```python
from value_investment import ValueInvestment
from value_investment.indicators import register_defaults, IndicatorRegistry

# 初始化时会自动注册默认指标
vi = ValueInvestment()

# 获取指标元数据
indicator = vi.get_indicator("revenue")
print(indicator.display_name)  # 营业收入

# 列出所有指标
all_indicators = vi.list_indicators()

# 按市场过滤
abc_indicators = vi.list_indicators(market="A股")

# 按类型过滤
raw_indicators = vi.list_indicators(indicator_type="RAW")
```

### 指标类型

- **RAW**: 原始财务数据（来自API）
- **SIMPLE**: 简单计算指标（ROE, ROA, 毛利率等）
- **COMPLEX**: 复杂计算指标（DCF, CAGR等）

### 市场支持

- **A股**: 6位数字代码（如 "600519"）
- **港股**: 5位数字代码（如 "00700"）
- **美股**: 字母代码（如 "AAPL"）
