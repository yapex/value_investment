# 现金流量表字段参考

## A股 (cashflow 命令)

数据格式：**宽格式**，每个财务项是一个列，返回 DataFrame。

### 基础列
| 列名 | 说明 |
|------|------|
| SECUCODE | 证券代码 (如 600519.SH) |
| SECURITY_CODE | 股票代码 |
| SECURITY_NAME_ABBR | 股票简称 |
| REPORT_DATE | 报告日期 |
| REPORT_TYPE | 报告类型 |

### 常用经营活动列名
| 列名 | 说明 |
|------|------|
| SALES_SERVICES | 销售商品、提供劳务收到的现金 |
| RECEIVE_TAX_REFUND | 收到的税费返还 |
| RECEIVE_OTHER_OPERATE | 收到其他与经营活动有关的现金 |
| TOTAL_OPERATE_INFLOW | 经营活动现金流入小计 |
| BUY_SERVICES | 购买商品、接受劳务支付的现金 |
| PAY_STAFF_CASH | 支付给职工的现金 |
| PAY_ALL_TAX | 支付的各项税费 |
| PAY_OTHER_OPERATE | 支付其他与经营活动有关的现金 |
| TOTAL_OPERATE_OUTFLOW | 经营活动现金流出小计 |
| NET_OPERATE_CASH_FLOW | 经营活动产生的现金流量净额 |

### 常用投资活动列名
| 列名 | 说明 |
|------|------|
| WITHDRAW_INVEST | 收回投资收到的现金 |
| RECEIVE_INVEST_INCOME | 取得投资收益收到的现金 |
| DISPOSAL_LONG_ASSET | 处置固定资产收到的现金 |
| TOTAL_INVEST_INFLOW | 投资活动现金流入小计 |
| CONSTRUCT_LONG_ASSET | 购建固定资产支付的现金 |
| INVEST_PAY_CASH | 投资支付的现金 |
| TOTAL_INVEST_OUTFLOW | 投资活动现金流出小计 |
| NET_INVEST_CASH_FLOW | 投资活动产生的现金流量净额 |

### 常用筹资活动列名
| 列名 | 说明 |
|------|------|
| ACCEPT_INVEST_CASH | 吸收投资收到的现金 |
| TOTAL_FINANCE_INFLOW | 筹资活动现金流入小计 |
| PAY_OFF_DEBT | 偿还债务支付的现金 |
| ASSIGN_DIVIDEND_PROFIT | 分配股利支付的现金 |
| TOTAL_FINANCE_OUTFLOW | 筹资活动现金流出小计 |
| NET_FINANCE_CASH_FLOW | 筹资活动产生的现金流量净额 |

### 现金净增加列名
| 列名 | 说明 |
|------|------|
| CASH_CASH_EQUIVALENT_INCREASE | 现金及现金等价物净增加额 |
| BEGIN_CASH_EQUIVALENTS | 期初现金及现金等价物余额 |
| END_CASH_EQUIVALENTS | 期末现金及现金等价物余额 |

---

## 港股 (cashflow 命令)

数据格式：**长格式**，通过 STD_ITEM_NAME + AMOUNT 存储数据。

### 列说明
| 列名 | 说明 |
|------|------|
| SECUCODE | 证券代码 |
| SECURITY_CODE | 股票代码 |
| REPORT_DATE | 报告日期 |
| STD_ITEM_NAME | 项目名称 (用于筛选) |
| AMOUNT | 金额 |

### 常用经营活动项目名
| STD_ITEM_NAME |
|---------------|
| 除税前溢利(业务利润) |
| 加:折旧及摊销 |
| 加:减值及拨备 |
| 存货(增加)减少 |
| 应收帐款减少 |
| 应付帐款及应计费用增加(减少) |
| 经营产生现金 |
| 已付税项 |
| 经营业务现金净额 |

### 常用投资活动项目名
| STD_ITEM_NAME |
|---------------|
| 已收利息(投资) |
| 已收股息(投资) |
| 处置固定资产 |
| 购建固定资产 |
| 购建无形资产及其他资产 |
| 出售附属公司 |
| 收购附属公司 |
| 投资支付现金 |
| 投资业务现金净额 |

### 常用筹资活动项目名
| STD_ITEM_NAME |
|---------------|
| 新增借款 |
| 偿还借款 |
| 发行股份 |
| 回购股份 |
| 发行债券 |
| 已付股息(融资) |
| 融资业务现金净额 |

### 现金净增加项目名
| STD_ITEM_NAME |
|---------------|
| 期初现金 |
| 期末现金 |
| 现金净额 |

---

## 美股 (cashflow 命令)

数据格式：**长格式**，通过 ITEM_NAME + AMOUNT 存储数据。

### 列说明
| 列名 | 说明 |
|------|------|
| SECUCODE | 证券代码 |
| SECURITY_CODE | 股票代码 |
| REPORT_DATE | 报告日期 |
| ITEM_NAME | 项目名称 (用于筛选) |
| AMOUNT | 金额 |

### 常用经营活动项目名
| ITEM_NAME |
|-----------|
| 净利润 |
| 折旧及摊销 |
| 减值及拨备 |
| 基于股票的补偿费 |
| 递延所得税 |
| 存货 |
| 应收账款及票据 |
| 应付账款及票据 |
| 递延收入 |
| 经营活动产生的现金流量净额 |

### 常用投资活动项目名
| ITEM_NAME |
|-----------|
| 购买固定资产 |
| 处置固定资产 |
| 购建无形资产及其他资产 |
| 投资支付现金 |
| 收购附属公司 |
| 投资活动产生的现金流量净额 |

### 常用筹资活动项目名
| ITEM_NAME |
|-----------|
| 发行股份 |
| 回购股份 |
| 发行债券 |
| 赎回债券 |
| 股息支付 |
| 筹资活动产生的现金流量净额 |

### 现金净增加项目名
| ITEM_NAME |
|-----------|
| 现金及现金等价物期初余额 |
| 现金及现金等价物期末余额 |
| 现金及现金等价物增加(减少)额 |
