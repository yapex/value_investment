---
name: financial_data
description: Use when querying A股/港股/美股 financial fields, indicators (ROE/ROIC/PE/gross_profit_margin/net_profit_margin), or screening stocks with financial filters. Includes balance sheet, income statement, cash flow fields, financial indicator queries, and stock screening with conditions like "roe 连续5年 ≥15%".
---

# financial_data

财务数据查询工具，支持 A 股/港股/美股的基本面数据查询。

## 市场代码格式

| 市场 | 代码格式 | 示例 | 参数 |
|-----|---------|------|------|
| A股 | 6位数字 | 600519 | `A` |
| 港股 | 5位数字 | 00700 | `HK` |
| 美股 | 字母 | AAPL | `US` |

---

## 模块一：财务字段查询

查询资产负债表、利润表、现金流量表的可用字段。

### 命令

```bash
# 查看报表可用字段
v-invest fields <market> <report>
```

### 参数说明

| 参数 | 说明 | 可选值 |
|------|------|--------|
| market | 市场 | `A`, `HK`, `US` |
| report | 报表类型 | `balance`, `income`, `cashflow`, `finind`, `quarterly` |

### 示例

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

### 常用字段速查

#### A股-资产负债表 (balance)

| 字段 | 说明 |
|------|------|
| total_assets | 资产总计 |
| total_liab | 负债合计 |
| total_hldr_eqy_excl_min_int | 归属股东权益合计 |
| cash_and_equivalents | 货币资金 |
| accounts_receivable | 应收账款 |
| inventory | 存货 |
| total_cur_assets | 流动资产合计 |
| total_cur_liab | 流动负债合计 |

#### A股-利润表 (income)

| 字段 | 说明 |
|------|------|
| revenue | 营业总收入 |
| operating_profit | 营业利润 |
| total_profit | 利润总额 |
| net_profit | 净利润 |
| parent_netprofit | 归属净利润 |
| gross_profit | 毛利 |

#### A股-财务指标 (finind)

| 字段 | 说明 |
|------|------|
| roe | 净资产收益率 |
| roe_weighted | 净资产收益率(加权) |
| net_profit_margin | 净利率 |
| gross_profit_margin | 毛利率 |
| debt_to_asset | 资产负债率 |
| asset_turnover | 总资产周转率 |
| revenue_growth | 营业收入增长率 |

---

## 模块二：财务指标查询

基于财务字段计算或直接查询的指标，如 ROE、ROIC、PE 等。

### 命令

```bash
# 列出所有可用指标
v-invest indicators A

# 获取单个指标（当前值）
v-invest indicator roe -s 600519 -m A

# 获取指标多年历史数据（重点！）
v-invest indicator roe -s 00700 -m HK -y 10
v-invest indicator roe,roa,operating_profit_margin -s 00700 -m HK -y 10
```

### 参数说明

| 参数 | 说明 |
|------|------|
| -s / --stock | 股票代码 |
| -m / --market | 市场 (A/HK/US) |
| -y / --years | 年数 (当 > 1 时返回多年历史数据) |

### 常用指标

| 指标 | 说明 |
|------|------|
| roe | 净资产收益率 |
| roe_weighted_avg | 净资产收益率(加权平均) |
| roa | 总资产收益率 |
| roic | 投入资本回报率 |
| gross_profit_margin | 毛利率 |
| net_profit_margin | 净利率 |
| expense_ratio | 费用率 |
| debt_ratio | 资产负债率 |
| current_ratio | 流动比率 |
| quick_ratio | 速动比率 |
| asset_turnover | 总资产周转率 |
| inventory_turnover | 存货周转率 |
| receivables_turnover | 应收账款周转率 |
| revenue_growth | 营业收入增长率 |
| net_profit_yoy | 净利润同比增长率 |
| PEPct | PE 百分位 |
| PCFPct | PCF 百分位 |
| PBPct | PB 百分位 |

### 输出格式

- 当 `-y` 参数 = 1 时，返回当前值
- 当 `-y` 参数 > 1 时，返回多年历史数据表格

---

## 模块三：股票筛选

批量获取全市场股票数据，使用文本条件进行筛选。

### 命令

```bash
# 基本筛选
v-invest scan --filter "roe 连续5年 ≥15%"

# 多条件 AND
v-invest scan --filter "roe 连续5年 ≥15% 且 毛利率 连续5年 ≥30%"

# 输出到文件
v-invest scan --filter "roe 连续5年 ≥15%" -o result.csv

# 缓存机制：首次扫描自动缓存结果，再次运行相同条件直接返回缓存
v-invest scan --filter "roic 5年至少4年 ≥15%, 平均≥15%" -m A --fields roic -y 5 -l 0

# 强制重新扫描（不使用缓存）
v-invest scan --filter "roe 连续5年 ≥15%" --no-cache

# 查看已缓存的扫描结果
v-invest scan-list
v-invest scan-list -m A    # 查看 A 股市场缓存
v-invest scan-list -m HK    # 查看港股市场缓存
```

### 筛选条件语法

| 语法 | 说明 |
|------|------|
| `roe 连续5年 ≥15%` | ROE 连续 5 年都 ≥15% |
| `roic 5年至少4年 ≥15%, 平均≥15%` | 5 年中至少 4 年 ROIC ≥15%，且平均值 ≥15% |
| `且` | 多个条件 AND |
| `或` | 多个条件 OR |

### 常用筛选条件

```bash
# 高 ROE 筛选
v-invest scan --filter "roe 连续5年 ≥15%"

# 高 ROE + 高毛利
v-invest scan --filter "roe 连续5年 ≥15% 且 毛利率 连续5年 ≥30%"

# 低估值筛选
v-invest scan --filter "pe 百分位 ≤20% 且 roe ≥15%"

# 稳定增长筛选
v-invest scan --filter "营收增速 3年CAGR ≥10% 且 净利润增速 3年CAGR ≥10%"
```

### 常用选项

| 选项 | 说明 |
|------|------|
| --filter | 筛选条件 |
| -m / --market | 市场 (A/HK/US) |
| --fields | 指定输出字段 |
| -y / --years | 指标年数 |
| -o / --output | 输出文件 |
| --no-cache | 强制不使用缓存 |
| -r / --refresh | 强制刷新缓存 |

---

## 常用命令速查

| 需求 | 命令 |
|------|------|
| 基本信息 | `v-invest info 600519` |
| 历史股价 | `v-invest hist 600519 --end 20241231` |
| 利润表 | `v-invest income 600519` |
| 资产负债表 | `v-invest balance 600519` |
| 现金流量表 | `v-invest cashflow 600519` |
| 财务指标 | `v-invest finind 600519 -m A` |
| 指标当前值 | `v-invest indicator roe -s 00700 -m HK` |
| **指标10年历史** | `v-invest indicator roe,roa,operating_profit_margin -s 00700 -m HK -y 10` |
| PE百分位 | `v-invest indicator PEPct -s 600519 -m A -y 10` |
| 股票筛选 | `v-invest scan --filter "roe 连续5年 ≥15%"` |
| 查看缓存 | `v-invest scan-list` |
| 查看A股缓存 | `v-invest scan-list -m A` |

---

## 校验清单

- [ ] 字段查询使用正确的市场参数 (A/HK/US)
- [ ] 指标查询指定了正确的市场 (A/HK/US)
- [ ] 多年历史数据使用 -y 参数 > 1
- [ ] 筛选条件语法正确（连续X年 / 至少X年 / 且/或）
- [ ] 输出文件使用 -o 参数指定
