# ROE 分析框架

ROE 深度分析的操作指南，按需选择分析模式。

## 快速入口

| 模式 | 适用场景 | 文件 |
|------|---------|------|
| **快速分析** | 5-6 个核心指标，快速判断 | [quick_analysis.md](./quick_analysis.md) |
| **深入分析** | 15+ 指标 + 10年历史，全面评估 | [deep_analysis.md](./deep_analysis.md) |
| **同业对比** | 与竞争对手对比分析 | [peer_comparison.md](./peer_comparison.md) |

## 选择指南

```
需要快速判断股票质量？
    ├─ 是 → quick_analysis.md（5-6个指标）
    └─ 否 → 需要深度分析？
              ├─ 是 → deep_analysis.md（15+指标，10年数据）
              └─ 需对比同业？ → peer_comparison.md
```

## 命令速查

```bash
# 快速分析（5个核心指标，5年数据）
v-invest indicator "roe,roa,net_profit_margin,debt_ratio,total_assets_turnover" -s 00700 -m HK -y 5

# 深入分析（核心指标，10年数据）
v-invest indicator "roe,roa,net_profit_margin,gross_margin,total_assets_turnover,equity_multiplier" -s 00700 -m HK -y 10
```
