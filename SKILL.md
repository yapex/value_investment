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

**必须使用 `--directory .` 指定当前目录：**

```bash
uv run --directory . python -m value_investment.cli info 600519
```

**强制刷新缓存使用 `--refresh` / `-r`：**

```bash
uv run --directory . python -m value_investment.cli info 600519 --refresh
```

**字段筛选使用 `--fields` / `-f`（三表命令）：**

```bash
# 利润表筛选字段
uv run --directory . python -m value_investment.cli income 600519 --fields "REPORT_DATE,NETPROFIT"

# 资产负债表筛选字段
uv run --directory . python -m value_investment.cli balance 600519 --fields "TOTAL_ASSETS,TOTAL_LIABILITIES"

# 现金流量表筛选字段
uv run --directory . python -m value_investment.cli cashflow 600519 --fields "NETCASH_OPERATE,NETCASH_INVEST"
```

**查询字段名**：
1. 查看 `src/value_investment/data/mapper.py` 中的 `INCOME_MAPPING`（利润表）、`BALANCE_MAPPING`（资产负债表）、`CASHFLOW_MAPPING`（现金流量表）
2. 或使用无效字段查询，会报错显示所有可用字段

## Quick Reference

| 需求 | 命令 |
|------|------|
| 基本信息 | `cli info 600519` |
| **市值（港股）** | `cli indicator latest_market_cap -s 00700 -m HK` |
| 历史股价 | `cli hist 600519 --end 20241231` |
| 利润表 | `cli income 600519` |
| 资产负债表 | `cli balance 600519` |
| 现金流量表 | `cli cashflow 600519` |
| 财务指标 | `cli finind 600519 -m A` |
| 单个指标 | `cli indicator ROIC -s 00700 -m HK` |
| PE百分位 | `cli indicator PEPct -s 600519 -m A -y 10` |
| 完整分析 | `cli analyze 600519` |
| 美股财务指标 | `cli finind AAPL -m US` |
| 美股历史股价 | `cli hist AAPL -m US --end 20241231 --start 20150101` |
| 美股完整分析 | `cli analyze AAPL -m US` |

**字段筛选**（用于三表命令）：
- 先查 `src/value_investment/data/mapper.py` 确认字段名，或用无效字段触发错误查看可用字段

```bash
# 只返回指定字段
cli income 600519 --fields "NETPROFIT"
cli balance 600519 --fields "TOTAL_ASSETS,REPORT_DATE"
cli cashflow 600519 --fields "NETCASH_OPERATE"
```

**市场代码**：A股 `600519` | 港股 `00700` | 美股 `AAPL`

> 美股自动检测：纯字母股票代码自动识别为美股（如 `AAPL`、`TSLA`）

## 市值查询

**注意：** `list-indicators` 显示 `market_cap`，但实际应使用 `latest_market_cap`：

```bash
# 港股市值
cli indicator latest_market_cap -s 00700 -m HK

# A股市值（通过 finind 获取）
cli finind 600519 -m A
```

**市值单位：** 港股市值为港元，A股市值为人民币

**美股字段说明**：
- 财务指标字段映射见 `src/value_investment/data/mapper.py` 中的 `FINANCIAL_INDICATOR_MAPPING`
- 美股特有字段：`total_revenue`, `net_profit`, `roe`, `roa`, `debt_ratio` 等

## 参考文档

- 指标体系: `references/indicators.md`
- 财务报表字段: `src/value_investment/data/mapper.py` (INCOME_MAPPING / BALANCE_MAPPING / CASHFLOW_MAPPING)
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
