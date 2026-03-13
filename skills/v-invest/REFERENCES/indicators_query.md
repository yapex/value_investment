# 财务指标查询

查询股票财务指标，支持计算型和直接查询型指标。

## 命令

```bash
# 查看市场可用指标
v-invest indicators <market>

# 查询单个指标
v-invest indicator <indicator_name> -s <stock_code> -m <market>
```

## 参数说明

### indicators 命令

| 参数 | 说明 | 可选值 |
|------|------|--------|
| market | 市场 | `A`, `HK`, `US` |

### indicator 命令

| 参数 | 说明 | 必填 |
|------|------|------|
| indicator_name | 指标名称 | 是 |
| -s / --stock | 股票代码 | 是 |
| -m / --market | 市场 | 否（可自动识别） |
| -y / --years | 年数 | 否（默认10） |

## 示例

```bash
# 查看A股可用指标
v-invest indicators A

# 查看港股可用指标
v-invest indicators HK

# 查询ROE
v-invest indicator ROE -s 600519 -m A

# 查询ROIC
v-invest indicator ROIC -s 600519 -m A

# 查询PE百分位（10年）
v-invest indicator PEPct -s 600519 -m A -y 10

# 查询港股指标
v-invest indicator ROE -s 00700 -m HK
```

## 常用指标

| 指标 | 说明 | 适用市场 |
|------|------|----------|
| ROE | 净资产收益率 | A, HK, US |
| ROIC | 投资资本回报率 | A, HK |
| PE | 市盈率 | A, HK, US |
| PEPct | PE百分位 | A |
| PB | 市净率 | A, HK, US |
| market_cap | 市值 | A, HK, US |
| revenue_growth | 营业收入增长率 | A, HK |
| net_profit_growth | 净利润增长率 | A, HK |
| gross_profit_margin | 毛利率 | A, HK |
| debt_to_asset | 资产负债率 | A, HK |

## 指标分类

### 估值指标
- PE, PB, PS, PCF
- PEPct, PBPct（市净率百分位）

### 盈利能力
- ROE, ROA, ROIC
- gross_profit_margin, net_profit_margin

### 成长能力
- revenue_growth, net_profit_growth
- operating_profit_growth

### 财务健康
- debt_to_asset, current_ratio
- quick_ratio, cash_ratio
