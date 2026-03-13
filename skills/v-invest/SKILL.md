---
name: value-investment
description: Use when analyzing A股/港股/美股基本面，需要查询股票信息、历史股价、财务报表、财务指标（ROIC/ROE/CAGR/PE百分位）或进行价值投资分析
---

# value-investment

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
v-invest indicator ROE -s 600519 -m A

# 获取指标多年历史数据（重点！）
v-invest indicator ROE -s 00700 -m HK -y 10
v-invest indicator roe,roa,net_profit_margin -s 00700 -m HK -y 10
```

**注意**: 当 `-y` 参数 > 1 时，返回多年历史数据表格

**详细参考**: [REFERENCES/indicators_query.md](./REFERENCES/indicators_query.md)

---

## 模块三：财务分析框架

系统化的分析方法论，基于指标进行深度分析。

| 框架 | 说明 |
|------|------|
| [roe_analysis_framework/README.md](./REFERENCES/roe_analysis_framework/README.md) | ROE 分析框架（快速分析、深入分析、同业对比等） |

**递进关系**: 字段 → 指标 → 分析框架

---

## 模块四：股票筛选

批量获取全市场股票数据，使用文本条件进行筛选。

```bash
# 基本筛选
v-invest scan --filter "ROE 连续5年 ≥15%"

# 多条件 AND
v-invest scan --filter "ROE 连续5年 ≥15% 且 毛利率 连续5年 ≥30%"

# 输出到文件
v-invest scan --filter "ROE 连续5年 ≥15%" -o result.csv
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
| **指标10年历史** | `v-invest indicator roe,roa -s 00700 -m HK -y 10` |
| PE百分位 | `v-invest indicator PEPct -s 600519 -m A -y 10` |

## 常用选项

- `--refresh` / `-r`：强制刷新缓存
- `-m` / `--market`：指定市场（A/HK/US）
- `-y` / `--years`：指定年数（当 > 1 时返回多年历史数据）
