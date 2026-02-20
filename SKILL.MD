---
name: v-invest
description: |
  A股/港股/美股基本面分析工具。触发场景：(1) 股票基本信息/市值/行业 (2) 历史股价 (3) 财务报表 (4) 财务指标计算（ROE/ROIC/CAGR/PE百分位等）(5) 基本面分析
---

# v-invest

## 执行前提

> 开始前：获取当前日期（判断财报年份）

## ⚠️ 执行前必读

**在执行 `uv run` 命令前，必须使用 `--directory .` 参数指定当前目录（SKILL.md 所在的目录）。**

```bash
# Agent 执行流程
# 1. 读取 SKILL.md 得知项目在当前目录
# 2. 使用 --directory . 执行命令

# 正确的执行方式
uv run --directory . python -m value_investment.cli info 600519
```

**原因**：`uv run` 会从指定目录加载项目依赖和配置，必须在技能根目录执行才能正常工作。

### 强制刷新缓存

所有查询命令支持 `--refresh` / `-r` 参数强制从数据源重新获取数据并更新缓存：

```bash
uv run --directory . python -m value_investment.cli info 600519 --refresh
uv run --directory . python -m value_investment.cli hist 600519 -r
```

## 快速查询

```bash
# 基本信息 | 历史股价 | 完整分析
uv run --directory . python -m value_investment.cli info 600519
uv run --directory . python -m value_investment.cli hist 600519
uv run --directory . python -m value_investment.cli analyze 600519

# 财务指标
uv run --directory . python -m value_investment.cli indicator ROIC -s 600519
uv run --directory . python -m value_investment.cli indicator PEPct -s 600519 -y 10

# 财务报表
uv run --directory . python -m value_investment.cli profit 600519
uv run --directory . python -m value_investment.cli balance 600519
uv run --directory . python -m value_investment.cli cashflow 600519
```

**市场代码**：A股`600519` | 港股`00700` | 美股`AAPL`

---

## 完整命令参考

### 快速命令

| 需求 | 命令 |
|------|------|
| 股票基本信息 | `uv run --directory . python -m value_investment.cli info 600519` |
| 历史股价 | `uv run --directory . python -m value_investment.cli hist 600519 --end 20241231` |
| 利润表（净利润） | `uv run --directory . python -m value_investment.cli income 600519` |
| 资产负债表 | `uv run --directory . python -m value_investment.cli balance 600519` |
| 现金流量表 | `uv run --directory . python -m value_investment.cli cashflow 600519` |
| 财务指标 | `uv run --directory . python -m value_investment.cli finind 600519 -m A` |
| 单个指标 | `uv run --directory . python -m value_investment.cli indicator ROIC -s 00700 -m HK` |
| 完整分析 | `uv run --directory . python -m value_investment.cli analyze 600519` |

### 常用指标

```bash
# 港股示例
uv run --directory . python -m value_investment.cli indicator ROIC -s 00700 -m HK           # 投资资本回报率
uv run --directory . python -m value_investment.cli indicator CAGR -s 00700 -m HK            # 营收复合增长率
uv run --directory . python -m value_investment.cli indicator ImpliedGrowth -s 00700 -m HK  # 市场隐含增长率
uv run --directory . python -m value_investment.cli indicator PEPct -s 00700 -m HK -y 10   # PE历史百分位
uv run --directory . python -m value_investment.cli indicator latest_market_cap -s 00700 -m HK  # 最新市值

# A股示例
uv run --directory . python -m value_investment.cli indicator ROIC -s 600519 -m A
uv run --directory . python -m value_investment.cli indicator PEPct -s 600519 -m A -y 10
```

---

## Agent 查询流程

```
主Agent
  ├─ sub_agent_a: 制定计划
  │   ├─ 查 indicators.md 确认现成指标
  │   └─ 无 → 查字段文档，制定计划（Markdown格式）
  │
  ├─ sub_agent_b: 执行计划
  │   ├─ 执行CLI命令
  │   └─ 计算并返回结果（Markdown格式）
  │
  └─ 主Agent: 展示结果
```

### sub_agent_a 任务

1. 查 `references/indicators.md`
2. 有指标 → 直接查
3. 无 → 制定计划：
   - 确定三表字段（balance/profit/cashflow）
   - 查字段文档确认字段名
   - 输出 Markdown 格式计划

### sub_agent_b 任务

1. 执行 CLI 命令
2. 提取目标字段
3. 计算（如同比增长率）
4. 返回 Markdown 结果

### 数据格式

- Agent 间用 Markdown 表格交换数据
- CLI 输出已是 Markdown 格式

---

## 参考文档

- **指标体系**: [references/indicators.md](references/indicators.md)
- **财务报表字段**: [references/profit.md](references/profit.md) / [references/balance.md](references/balance.md)
- **ROIC计算**: [references/roic.md](references/roic.md)
