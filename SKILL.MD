---
name: v-invest
description: |
  A股/港股/美股基本面分析工具。触发场景：(1) 股票基本信息/市值/行业查询 (2) 历史股价 (3) 财务报表（资产负债表/利润表/现金流量表）(4) 财务指标计算（ROE/ROA/ROIC/毛利率/CAGR/PE百分位等）(5) 基本面/价值投资分析
---

# v-invest

## ⚠️ 执行前必读

**在执行 `uv run` 命令前，必须先切换到本技能的根目录（即 SKILL.md 所在的目录层级）。**

```bash
# 1. Agent 执行流程
#    - 调用 read_file 读取 SKILL.md，获取文件路径
#    - 提取文件所在目录（例如：/path/to/skills/value_investment/）
#    - cd 到该目录后执行命令

# 2. 正确的执行方式（动态获取 SKILL.md 所在目录）
cd <SKILL.md所在目录> && uv run python -m value_investment.cli info 600519
```

**原因**：`uv run` 会从当前目录加载项目依赖和配置，必须在技能根目录执行才能正常工作。

## 快速命令

| 需求 | 命令 |
|------|------|
| 股票基本信息 | `uv run python -m value_investment.cli info 600519` |
| 历史股价 | `uv run python -m value_investment.cli hist 600519 --end 20241231` |
| 利润表（净利润） | `uv run python -m value_investment.cli income 600519` |
| 资产负债表 | `uv run python -m value_investment.cli balance 600519` |
| 现金流量表 | `uv run python -m value_investment.cli cashflow 600519` |
| 财务指标 | `uv run python -m value_investment.cli finind 600519 -m A` |
| 单个指标 | `uv run python -m value_investment.cli indicator ROIC -s 00700 -m HK` |
| 完整分析 | `uv run python -m value_investment.cli analyze 600519` |

### 股票代码

- A股: `600519`
- 港股: `00700`
- 美股: `AAPL`

### 财务报表查询

查询财务报表可以获取原始数据，适合需要特定字段的场景（如净利润、总资产等）。

```bash
# 利润表 - 获取净利润、营收等
uv run python -m value_investment.cli income 600519 -m A

# 资产负债表 - 获取总资产、净资产等
uv run python -m value_investment.cli balance 600519 -m A

# 现金流量表 - 获取经营性现金流等
uv run python -m value_investment.cli cashflow 600519 -m A
```

### 常用指标

```bash
# 港股示例
uv run python -m value_investment.cli indicator ROIC -s 00700 -m HK           # 投资资本回报率
uv run python -m value_investment.cli indicator CAGR -s 00700 -m HK            # 营收复合增长率
uv run python -m value_investment.cli indicator ImpliedGrowth -s 00700 -m HK  # 市场隐含增长率
uv run python -m value_investment.cli indicator PEPct -s 00700 -m HK -y 10   # PE历史百分位
uv run python -m value_investment.cli indicator latest_market_cap -s 00700 -m HK  # 最新市值

# A股示例
uv run python -m value_investment.cli indicator ROIC -s 600519 -m A
uv run python -m value_investment.cli indicator PEPct -s 600519 -m A -y 10
```

---

## 🚀 高效查询原则

### 核心原则：最少查询，最大化信息

**问题场景**：用户问"茅台近10年营收增长率"，错误做法是：
1. 先查财务报表获取营收 → 2. 再单独查增长率

**正确做法**：
- 优先使用 `indicator CAGR` 直接获取增长率
- 或使用 `financial` 一次性获取所有数据（包含增长率）

### 查询策略决策树

```
用户需求
    ├─ 股票基本信息/市值/行业 → info
    ├─ 历史股价数据 → hist
    ├─ 财务报表原始数据（特定字段）
    │   ├─ 利润表 → income
    │   ├─ 资产负债表 → balance
    │   └─ 现金流量表 → cashflow
    ├─ 增长率/估值指标/复合指标
    │   ├─ 单个指标 → indicator <指标名>
    │   ├─ 多个综合数据 → financial --years N
    │   └─ 完整基本面分析 → analyze
    └─ 隐含增长率 → indicator ImpliedGrowth
```

### 必须避免的查询模式

❌ **低效模式：多次拆分查询**
```bash
# 第1次：查财务报表获取营收
uv run python -m value_investment.cli income 600519 -m A
# 第2次：再单独查增长率
uv run python -m value_investment.cli indicator CAGR -s 600519 -m A
```

✅ **高效模式：一次性获取**
```bash
# 方法A：直接获取增长率（最简洁）
uv run python -m value_investment.cli indicator CAGR -s 600519 -m A

# 方法B：获取完整财务数据（包含增长率）
uv run python -m value_investment.cli financial 600519 --end 2024 --years 10
# 输出已包含：营收、利润、CAGR、ROE、ROIC 等
```

### 优先级指南

| 优先级 | 命令 | 适用场景 | 返回内容 |
|-------|------|---------|---------|
| ⭐⭐⭐ | `indicator <指标名>` | 单个特定指标（CAGR/ROIC/PE百分位等） | 直接返回指标值 |
| ⭐⭐⭐ | `financial --years N` | 多年财务综合分析（营收、利润、增长率、指标） | 完整数据 + 计算结果 |
| ⭐⭐ | `analyze` | 完整基本面/价值投资分析 | 综合报告 |
| ⭐ | `income/balance/cashflow` | 需要特定报表字段 | 原始报表数据 |

### 记住：理解工具能力是关键

`financial` 和 `analyze` 命令已经内部计算了：
- CAGR（营收/利润复合增长率）
- ROE/ROIC/ROA
- 毛利率/净利率
- 现金流质量指标

**不要手动计算或单独查询这些指标！**

---

### 数据格式说明

- **CLI输出格式**: 使用Markdown表格格式（易于解析和阅读）
- **查看格式**: 使用 `head -n 5` 先查看数据格式
- **解析提示**: Agent可使用正则或简单字符串解析Markdown表格

---

## 参考文档

- **指标体系**: [references/indicators.md](references/indicators.md)
- **ROIC计算**: [references/roic.md](references/roic.md)
- **市场字段**: [references/a-stock.md](references/a-stock.md) / [references/hk-stock.md](references/hk-stock.md)
- **财务报表**: [references/balance.md](references/balance.md) / [references/profit.md](references/profit.md)
