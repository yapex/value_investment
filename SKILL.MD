---
name: v-invest
description: |
  A股/港股/美股基本面分析工具。触发场景：(1) 股票基本信息/市值/行业查询 (2) 历史股价 (3) 财务报表（资产负债表/利润表/现金流量表）(4) 财务指标计算（ROE/ROA/毛利率/DCF等）(5) 基本面/价值投资分析
---

# v-invest

## 场景化命令

| 需求 | 命令 |
|------|------|
| 股票基本信息 | `v-invest info 600519` |
| 历史股价 | `v-invest hist 600519 --end 20241231` |
| 资产负债表 | `v-invest balance 600519 --end 2024` |
| 利润表 | `v-invest profit 600519 --end 2024` |
| 现金流量表 | `v-invest cashflow 600519 --end 2024` |
| 财务指标 | `v-invest finind 600519 -m A` |
| 单个指标 | `v-invest indicator ROE -s 600519` |
| 完整分析 | `v-invest analyze 600519` |

### 代码格式

- A股: 6位数字 (600519)
- 港股: 5位数字 (00700)
- 美股: 字母 (AAPL)

### 示例

```bash
# A股财务指标
v-invest finind 600519 -m A

# 港股财务指标
v-invest finind 00700 -m HK

# 单个指标（自包含）
v-invest indicator ROE -s 600519
v-invest indicator PEPct -s 600519 -y 5
```

### 重要提示

- **`indicator` 命令自包含**：自动获取财务数据
- **避免冗余**：查询单个指标时只执行 `indicator`
- **`analyze` 适用场景**：用户明确要求"完整分析"时使用

---

## 参考文档

- **指标体系**: [references/indicators.md](references/indicators.md)
- **市场字段**: [a-stock.md](references/a-stock.md) / [hk-stock.md](references/hk-stock.md) / [us-stock.md](references/us-stock.md)
- **财务报表**: [balance.md](references/balance.md) / [profit.md](references/profit.md) / [cashflow.md](references/cashflow.md)
