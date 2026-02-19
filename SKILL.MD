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

## Agent 查询流程

### 流程概述

```
主Agent收到查询请求
    │
    ├─ sub_agent_a: 制定查询计划
    │   ├─ 查询 indicators.md 确认是否有现成指标
    │   ├─ 如满足 → 直接返回结果
    │   └─ 如不满足 → 制定查询计划
    │       ├─ 确定需要用到的三表字段（balance/profit/cashflow）
    │       ├─ 查询相关字段文档确认字段名
    │       └─ 返回 Markdown 格式的查询计划
    │
    ├─ sub_agent_b: 执行查询计划
    │   ├─ 执行 CLI 命令获取原始数据
    │   ├─ 如需要 → 进行计算
    │   └─ 返回 Markdown 格式的结果
    │
    └─ 主Agent: 展示最终结果
```

### sub_agent_a 任务：制定查询计划

**输入**：用户的查询需求（如"查询002027最近10年营收情况"）

**步骤**：
1. 查询 `references/indicators.md`，确认是否有现成指标满足需求
2. 如有 → 执行查询并返回结果
3. 如无 → 制定查询计划：
   - 确定需要用到的三表（balance/profit/cashflow）
   - 查询对应字段文档（balance.md/profit.md/cashflow.md）确认字段名
   - 输出 Markdown 格式的查询计划

**输出格式**：
```markdown
## 查询计划

| 项目 | 内容 |
|------|------|
| 命令 | `profit <股票代码> -e <年份>` |
| 目标字段 | `<字段名>`（<字段说明>） |
| 需要计算 | <如有计算需求> |
| 返回格式 | 年份 | 数值 | 同比增长率 |
```

### sub_agent_b 任务：执行查询

**输入**：sub_agent_a 制定的查询计划

**步骤**：
1. 确认当前项目目录，使用 `pwd` 获取路径后执行 `uv run` 命令
2. 执行计划中的 CLI 命令
3. 提取目标字段数据
4. 如需要 → 进行计算（如同比增长率、复合增长率等）
5. 返回 Markdown 格式结果

**输出格式**：
```markdown
## 查询结果

| 年份 | 营收(亿元) | 同比增长率 |
|------|-----------|------------|
| 2024 | xxx | xx% |
| ... | ... | ... |
```

### 数据格式规范

- **所有agent间交换数据使用 Markdown 表格格式**
- **CLI输出本身已是Markdown格式**
- **主Agent展示时直接使用agent返回的Markdown内容**

---

## 参考文档

- **指标体系**: [references/indicators.md](references/indicators.md)
- **ROIC计算**: [references/roic.md](references/roic.md)
- **市场字段**: [references/a-stock.md](references/a-stock.md) / [references/hk-stock.md](references/hk-stock.md)
- **财务报表**: [references/balance.md](references/balance.md) / [references/profit.md](references/profit.md)
