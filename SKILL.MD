---
name: v-invest
description: |
  A股/港股/美股基本面分析工具。触发场景：(1) 股票基本信息/市值/行业 (2) 历史股价 (3) 财务报表 (4) 财务指标计算（ROE/ROIC/CAGR/PE百分位等）(5) 基本面分析
---

# v-invest

## 执行前提

> 开始前：获取当前日期（判断财报年份），确认项目目录

## 快速查询

```bash
# 基本信息 | 历史股价 | 完整分析
info 600519 | hist 600519 | analyze 600519

# 财务指标
indicator ROIC -s 600519     # 单个指标
indicator PEPct -s 600519 -y 10  # PE百分位

# 财务报表
profit 600519    # 利润表
balance 600519   # 资产负债表
cashflow 600519 # 现金流量表
```

**市场代码**：A股`600519` | 港股`00700` | 美股`AAPL`

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
