---
name: value-investment
description: Use when analyzing A股/港股/美股基本面，需要查询股票信息、历史股价、财务报表、财务指标（ROIC/ROE/CAGR/PE百分位）或进行价值投资分析
---

# value-investment

价值投资分析工具，支持A股/港股/美股基本面分析，数据来源 akshare。

## 市场与代码格式

| 市场 | 代码格式 | 示例 | 市场参数 |
|-----|---------|------|---------|
| A股 | 6位数字 | 600519 | `A` |
| 港股 | 5位数字 | 00700 | `HK` |
| 美股 | 字母 | AAPL | `US` |

> 美股自动检测：纯字母代码自动识别为美股

## 常用命令

| 需求 | 命令 |
|------|------|
| 基本信息 | `v-invest info 600519` |
| 历史股价 | `v-invest hist 600519 --end 20241231` |
| 利润表 | `v-invest income 600519` |
| 资产负债表 | `v-invest balance 600519` |
| 现金流量表 | `v-invest cashflow 600519` |
| 财务指标 | `v-invest finind 600519 -m A` |
| 单个指标 | `v-invest indicator ROIC -s 00700 -m HK` |
| PE百分位 | `v-invest indicator PEPct -s 600519 -m A -y 10` |
| 完整分析 | `v-invest analyze 600519` |
| **可用字段** | `v-invest fields A balance` |
| **可用指标** | `v-invest indicators A` |

## 查询可用字段/指标

```bash
# 查看报表字段：fields <market> <report>
v-invest fields A balance   # A股资产负债表
v-invest fields HK finind   # 港股财务指标
v-invest fields US income   # 美股利润表

# 查看可用指标：indicators <market>（必须指定市场）
v-invest indicators A       # A股指标
v-invest indicators HK      # 港股指标
v-invest indicators US      # 美股指标
```

## 常用选项

- `--refresh` / `-r`：强制刷新缓存
- `--fields` / `-f`：筛选字段（三表命令）
- `-m` / `--market`：指定市场（A/HK/US）
- `-y` / `--years`：指定年数

```bash
v-invest income 600519 --fields "NETPROFIT,REPORT_DATE"
v-invest indicator PEPct -s 600519 -m A -y 10
```

## 市值查询

```bash
v-invest indicator latest_market_cap -s 00700 -m HK  # 港股
v-invest finind 600519 -m A                          # A股（在 finind 中）
```

---

## Agent 查询流程

1. `v-invest indicators <market>` 确认可用指标
2. `v-invest fields <market> <report>` 确认可用字段
3. 有现成指标 → 直接执行
4. 无现成指标 → 制定计算计划
