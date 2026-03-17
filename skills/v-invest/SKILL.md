---
name: v-invest
description: Use when analyzing A股/港股/美股基本面，需要查询股票信息、历史股价、财务报表、财务指标（ROIC/ROE/CAGR/PE百分位）或进行价值投资分析
---

# v-invest

价值投资分析工具，支持A股/港股/美股基本面分析。

## 市场代码格式

| 市场 | 代码格式 | 示例 | 参数 |
|-----|---------|------|------|
| A股 | 6位数字 | 600519 | `A` |
| 港股 | 5位数字 | 00700 | `HK` |
| 美股 | 字母 | AAPL | `US` |

---

## 模块一：财务字段

财务报表的原始字段（资产负债表、利润表、现金流量表）。

```bash
v-invest fields A balance
v-invest fields A income
v-invest fields HK finind
```

**详细参考**: [REFERENCES/fields.md](./REFERENCES/fields.md)

---

## 模块二：财务指标

基于财务字段计算或直接查询的指标，如 ROE、ROIC、PE 等。

```bash
# 列出所有可用指标
v-invest indicators A

# 获取单个指标（当前值）
v-invest indicator roe -s 600519 -m A

# 获取指标多年历史数据（重点！）
v-invest indicator roe -s 00700 -m HK -y 10
v-invest indicator roe,roa,operating_profit_margin -s 00700 -m HK -y 10
```

**注意**: 当 `-y` 参数 > 1 时，返回多年历史数据表格

**详细参考**: [REFERENCES/indicators_query.md](./REFERENCES/indicators_query.md)

---

## 模块三：财务分析框架

系统化的分析方法论，基于指标进行深度分析。

**递进关系**: 字段 → 指标 → 分析框架

---

### 框架一：ROE 分析

聚焦 ROE 单指标的深度拆解，适合快速判断股票质量。

| 模式 | 适用场景 | 文件 |
|------|---------|------|
| 快速分析 | 5-6 个核心指标，快速判断 | [quick_analysis.md](./REFERENCES/roe_analysis_framework/quick_analysis.md) |
| 深入分析 | 15+ 指标 + 10年历史，全面评估 | [deep_analysis.md](./REFERENCES/roe_analysis_framework/deep_analysis.md) |
| 同业对比 | 与竞争对手对比分析 | [peer_comparison.md](./REFERENCES/roe_analysis_framework/peer_comparison.md) |

**入口**: [roe_analysis_framework/README.md](./REFERENCES/roe_analysis_framework/README.md)

---

### 框架二：七看八问企业分析 ⭐

完整的企业分析框架，覆盖财务 + 非财务 + 偏见校验。

**执行流程**:
```
准备数据 → 七看财务 → 八问非财务 → 偏见校验 → 输出报告
```

**七看财务**（按顺序执行）:
| 步骤 | 内容 | 核心产出 |
|------|------|---------|
| 1️⃣ 看营收 | 收入/利润/现金流趋势 | 盈利质量评级 |
| 2️⃣ 看成本 | 毛利率/费用率/非经常性损益 | 成本结构拆解 |
| 3️⃣ 看增长 | 收入CAGR/利润CAGR | 增长能力评级 |
| 4️⃣ 看业务 | 业务板块占比/增长来源 | 核心引擎识别 |
| 5️⃣ 看资产 | 资产结构/债务风险 | 资产健康度 |
| 6️⃣ 看效率 | 流动资金/周转率/人均效率 | 投入产出效率 |
| 7️⃣ 看收益 | ROE/ROA/ROIC | 盈利能力评级 |

**八问非财务**（逐一回答）:
| 问题 | 核心关注点 |
|------|-----------|
| 1. 生意模式 | 靠什么赚钱？客户类型？ |
| 2. 外部环境 | 行业周期？政策态度？ |
| 3. 行业空间 | 市场规模？增长潜力？ |
| 4. 竞争格局 | 集中度？市占率？ |
| 5. 护城河 | 核心优势？可持续性？ |
| 6. 管理层 | 能力？诚信？执行力？ |
| 7. 风险因素 | 3个核心风险？ |
| 8. 未来展望 | 增长驱动？路径清晰？ |

**详细文件**:
| 模块 | 文件 |
|------|------|
| 七看财务 | [7_looks_financial.md](./REFERENCES/financial_analysis_7n8/7_looks_financial.md) |
| 八问非财务 | [8_questions_nonfinancial.md](./REFERENCES/financial_analysis_7n8/8_questions_nonfinancial.md) |
| 偏见校验 | [bias_check.md](./REFERENCES/financial_analysis_7n8/bias_check.md) |
| 报告模板 | [report_template.md](./REFERENCES/financial_analysis_7n8/report_template.md) |

**入口**: [financial_analysis_7n8/README.md](./REFERENCES/financial_analysis_7n8/README.md)

---

### 框架选择指南

```
分析目标是什么？
    ├─ 仅评估 roe 质量 → 框架一：ROE 分析
    │   ├─ 快速判断 → quick_analysis.md
    │   └─ 深度研究 → deep_analysis.md
    │
    └─ 完整企业分析 → 框架二：七看八问
        └─ 按流程执行：准备 → 七看 → 八问 → 校验 → 报告
```

---

## 模块四：股票筛选

批量获取全市场股票数据，使用文本条件进行筛选。

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

**详细参考**: [REFERENCES/scanner.md](./REFERENCES/scanner.md)

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

## 常用选项

- `--refresh` / `-r`：强制刷新缓存
- `-m` / `--market`：指定市场（A/HK/US）
- `-y` / `--years`：指定年数（当 > 1 时返回多年历史数据）
