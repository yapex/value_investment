# 资产负债表字段参考

## A股 (balance 命令)

数据格式：**宽格式**，每个财务项是一个列，返回 DataFrame。

### 基础列
| 列名 | 说明 |
|------|------|
| SECUCODE | 证券代码 (如 600519.SH) |
| SECURITY_CODE | 股票代码 |
| SECURITY_NAME_ABBR | 股票简称 |
| REPORT_DATE | 报告日期 |
| REPORT_TYPE | 报告类型 |

### 常用资产类列名
| 列名 | 说明 |
|------|------|
| TOTAL_ASSETS | 资产总计 |
| TOTAL_CURRENT_ASSETS | 流动资产合计 |
| TOTAL_NONCURRENT_ASSETS | 非流动资产合计 |
| MONETARYFUNDS | 货币资金 |
| ACCOUNTS_RECE | 应收账款 |
| INVENTORY | 存货 |
| FIXED_ASSET | 固定资产 |
| INTANGIBLE_ASSET | 无形资产 |
| GOODWILL | 商誉 |
| LONG_EQUITY_INVEST | 长期股权投资 |
| PREPAYMENT | 预付款项 |

### 常用负债类列名
| 列名 | 说明 |
|------|------|
| TOTAL_LIABILITIES | 负债合计 |
| TOTAL_CURRENT_LIAB | 流动负债合计 |
| TOTAL_NONCURRENT_LIAB | 非流动负债合计 |
| ACCOUNTS_PAYABLE | 应付账款 |
| ADVANCE_RECEIVABLES | 预收款项 |

### 常用权益类列名
| 列名 | 说明 |
|------|------|
| TOTAL_EQUITY | 所有者权益合计 |
| TOTAL_PARENT_EQUITY | 归属母公司所有者权益 |
| MINORITY_INTEREST | 少数股东权益 |
| PAIDIN_CAPITAL | 实收资本(或股本) |
| CAPITAL_RESERVE | 资本公积 |
| SURPLUS_RESERVE | 盈余公积 |
| UNASSIGN_PROFIT | 未分配利润 |

---

## 港股 (balance 命令)

数据格式：**长格式**，通过 STD_ITEM_NAME + AMOUNT 存储数据。

### 列说明
| 列名 | 说明 |
|------|------|
| SECUCODE | 证券代码 |
| SECURITY_CODE | 股票代码 |
| REPORT_DATE | 报告日期 |
| STD_ITEM_NAME | 项目名称 (用于筛选) |
| AMOUNT | 金额 |

### 常用资产类项目名
| STD_ITEM_NAME |
|---------------|
| 总资产 |
| 流动资产合计 |
| 非流动资产合计 |
| 现金及等价物 |
| 存货 |
| 应收帐款 |
| 物业厂房及设备 |
| 无形资产 |
| 联营公司权益 |
| 合营公司权益 |
| 预付款按金及其他应收款 |

### 常用负债类项目名
| STD_ITEM_NAME |
|---------------|
| 总负债 |
| 流动负债合计 |
| 非流动负债合计 |
| 应付帐款 |
| 应付票据 |
| 应付税项 |
| 长期贷款 |
| 短期贷款 |

### 常用权益类项目名
| STD_ITEM_NAME |
|---------------|
| 股东权益 |
| 净资产 |
| 总权益 |
| 股本 |
| 储备 |
| 保留溢利(累计亏损) |
| 少数股东权益 |

---

## 美股 (balance 命令)

数据格式：**长格式**，通过 ITEM_NAME + AMOUNT 存储数据。

### 列说明
| 列名 | 说明 |
|------|------|
| SECUCODE | 证券代码 |
| SECURITY_CODE | 股票代码 |
| REPORT_DATE | 报告日期 |
| ITEM_NAME | 项目名称 (用于筛选) |
| AMOUNT | 金额 |

### 常用资产类项目名
| ITEM_NAME |
|-----------|
| 总资产 |
| 流动资产合计 |
| 非流动资产合计 |
| 现金及现金等价物 |
| 短期投资 |
| 应收账款 |
| 存货 |
| 物业、厂房及设备 |
| 无形资产 |
| 商誉 |
| 长期投资 |

### 常用负债类项目名
| ITEM_NAME |
|-----------|
| 总负债 |
| 流动负债合计 |
| 非流动负债合计 |
| 应付账款 |
| 短期债务 |
| 长期负债 |
| 预收及预提费用 |

### 常用权益类项目名
| ITEM_NAME |
|-----------|
| 股东权益合计 |
| 归属于母公司股东权益 |
| 普通股 |
| 留存收益 |
| 其他综合收益 |
| 优先股 |
