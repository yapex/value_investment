---
name: value-investment
description: Use when analyzing A股/港股/美股基本面，需要查询股票信息、历史股价、财务报表、财务指标（ROIC/ROE/CAGR/PE百分位）或进行价值投资分析
---

# value-investment

## Overview

价值投资分析工具，支持A股/港股/美股基本面分析，数据来源 akshare。

## When to Use

- 股票基本信息/市值/行业查询
- 历史股价查询
- 财务报表（利润表/资产负债表/现金流量表）
- 财务指标计算（ROIC/ROE/CAGR/PE百分位）
- 基本面分析

## ⚠️ 执行要点

```bash
v-invest info 600519
```

**强制刷新缓存使用 `--refresh` / `-r`：**

```bash
v-invest info 600519 --refresh
```

**字段筛选使用 `--fields` / `-f`（三表命令）：**

```bash
# 利润表筛选字段
v-invest income 600519 --fields "REPORT_DATE,NETPROFIT"

# 资产负债表筛选字段
v-invest balance 600519 --fields "TOTAL_ASSETS,TOTAL_LIABILITIES"

# 现金流量表筛选字段
v-invest cashflow 600519 --fields "NETCASH_OPERATE,NETCASH_INVEST"
```

**查询字段名**：
1. 使用 `fields <market> <report>` 命令查看可用标准字段
2. 支持的报告类型：`balance`（资产负债表）、`income`（利润表）、`cashflow`（现金流量表）、`finind`（财务指标）、`quarterly`（季度数据）
3. 例如：`fields A balance`、`fields HK finind`

```bash
# 查看A股资产负债表可用字段
v-invest fields A balance

# 查看港股财务指标可用字段
v-invest fields HK finind

# 查看美股利润表可用字段
v-invest fields US income
```

## Quick Reference

| 需求 | 命令 |
|------|------|
| 基本信息 | `v-invest info 600519` |
| **市值（港股）** | `v-invest indicator latest_market_cap -s 00700 -m HK` |
| 历史股价 | `v-invest hist 600519 --end 20241231` |
| 利润表 | `v-invest income 600519` |
| 资产负债表 | `v-invest balance 600519` |
| 现金流量表 | `v-invest cashflow 600519` |
| 财务指标 | `v-invest finind 600519 -m A` |
| 单个指标 | `v-invest indicator ROIC -s 00700 -m HK` |
| PE百分位 | `v-invest indicator PEPct -s 600519 -m A -y 10` |
| 完整分析 | `v-invest analyze 600519` |
| **查看可用字段** | `v-invest fields A balance` |
| **查看可用指标** | `v-invest indicators` |
| 美股财务指标 | `v-invest finind AAPL -m US` |
| 美股历史股价 | `v-invest hist AAPL -m US --end 20241231 --start 20150101` |
| 美股完整分析 | `v-invest analyze AAPL -m US` |

**字段筛选**（用于三表命令）：
- 使用 `fields <market> <report>` 查看可用字段

```bash
# 只返回指定字段
v-invest income 600519 --fields "NETPROFIT"
v-invest balance 600519 --fields "TOTAL_ASSETS,REPORT_DATE"
v-invest cashflow 600519 --fields "NETCASH_OPERATE"
```

**市场代码**：A股 `600519` | 港股 `00700` | 美股 `AAPL`

> 美股自动检测：纯字母股票代码自动识别为美股（如 `AAPL`、`TSLA`）

## 市值查询

**注意：** `indicators` 显示 `market_cap`，但实际应使用 `latest_market_cap`：

```bash
# 港股市值
v-invest indicator latest_market_cap -s 00700 -m HK

# A股市值（通过 finind 获取）
v-invest finind 600519 -m A
```

**查看所有可用指标：**
```bash
v-invest indicators
```

**市值单位：** 港股市值为港元，A股市值为人民币

**美股字段说明**：
- 财务指标字段映射见 `src/value_investment/data/mapper.py` 中的 `FINANCIAL_INDICATOR_MAPPING`
- 美股特有字段：`total_revenue`, `net_profit`, `roe`, `roa`, `debt_ratio` 等

## 参考文档

- 指标体系: `references/indicators.md`
- 财务报表字段: 使用 `v-invest fields <market> <report>` 命令查看
- ROIC计算: `references/roic.md`

---

## Agent 查询流程

```
主Agent → sub_agent_a(制定计划) → sub_agent_b(执行) → 返回结果
```

### sub_agent_a: 制定计划

1. 查 `references/indicators.md` 确认现成指标
2. 有 → 直接执行
3. 无 → 制定计划（确定三表字段、确认字段名）

### sub_agent_b: 执行

1. 执行 CLI 命令
2. 提取目标字段
3. 计算并返回 Markdown 结果
