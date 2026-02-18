---
name: v-invest
description: |
  A股/港股/美股基本面分析工具。触发场景：(1) 股票基本信息/市值/行业查询 (2) 历史股价 (3) 财务报表（资产负债表/利润表/现金流量表）(4) 财务指标计算（ROE/ROA/ROIC/毛利率/DCF等）(5) 基本面/价值投资分析
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
| 单个指标 | `v-invest indicator ROIC -s 00700 -m HK` |
| 完整分析 | `v-invest analyze 600519` |

### 股票代码格式

- A股: 6位数字 (600519)
- 港股: 5位数字 (00700)
- 美股: 字母 (AAPL)

### 常用指标命令

```bash
# ROIC (资本回报率) - 支持港股/A股
v-invest indicator ROIC -s 00700 -m HK   # 港股腾讯
v-invest indicator ROIC -s 600519 -m A   # A股茅台

# ROE (股东权益回报率)
v-invest indicator ROE -s 00700 -m HK

# PE百分位
v-invest indicator PEPct -s 00700 -m HK -y 10
```

### 重要提示

- **`indicator` 命令自包含**：自动获取财务数据
- **避免冗余**：查询单个指标时只执行 `indicator`
- **`analyze` 适用场景**：用户明确要求"完整分析"时使用

---

## 参考文档

- **指标体系**: [references/indicators.md](references/indicators.md)
- **ROIC计算说明**: [references/roic.md](references/roic.md) - 公式、参数、港股字段映射
- **市场字段**: [a-stock.md](references/a-stock.md) / [hk-stock.md](references/hk-stock.md) / [us-stock.md](references/us-stock.md)
- **财务报表**: [balance.md](references/balance.md) / [profit.md](references/profit.md) / [cashflow.md](references/cashflow.md)
