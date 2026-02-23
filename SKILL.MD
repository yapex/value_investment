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

## Quick Reference

| 需求 | 命令 |
|------|------|
| 基本信息 | `cli info 600519` |
| 历史股价 | `cli hist 600519 --end 20241231` |
| 利润表 | `cli income 600519` |
| 资产负债表 | `cli balance 600519` |
| 财务指标 | `cli finind 600519 -m A` |
| 单个指标 | `cli indicator ROIC -s 00700 -m HK` |
| PE百分位 | `cli indicator PEPct -s 600519 -m A -y 10` |
| 完整分析 | `cli analyze 600519` |

**市场代码**：A股 `600519` | 港股 `00700` | 美股 `AAPL`

## 参考文档

- 指标体系: `references/indicators.md`
- 财务报表字段: `references/profit.md` / `references/balance.md`
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
