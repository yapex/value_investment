# CLAUDE.md

## 项目

价值投资分析工具，支持 A 股/港股/美股基本面分析。数据来源 akshare。

## 命令

```bash
# 测试
uv run python -m pytest tests/ -v

# CLI
uv run python -m value_investment.cli --help
uv run python -m value_investment.cli hist 600519 --end 20241231
uv run python -m value_investment.cli financial 600519 --end 2024
```

## 架构

- `src/value_investment/api.py` - Python API 入口
- `src/value_investment/cli.py` - 命令行接口
- `src/value_investment/data/providers/` - 数据获取 (A 股/港股/美股)
- `src/value_investment/indicators/` - 指标计算
- `src/value_investment/data/mapper.py` - 字段映射 (CORE_FIELD_MAPPING)

## 市场识别

| 市场 | 代码格式 | 示例 |
|-----|---------|------|
| A 股 | 6 位数字 (0/3/6 开头) | 600519, 000001 |
| 港股 | 5 位数字 | 00700, 09988 |
| 美股 | 字母代码 | AAPL, TSLA |

## 缓存策略

| 数据类型 | TTL |
|---------|-----|
| 个股信息 | 次日凌晨 (A 股) / 次年 6 月底 (港/美) |
| 历史价格 | 1 年 |
| 财务报表 | 次年 6 月底 |

## 文档

- [`docs/README.md`](docs/README.md) - 文档索引
- [`docs/market_indicator_differences.md`](docs/market_indicator_differences.md) - 三市场指标差异对齐
- [`docs/ifrs_standard_fields.md`](docs/ifrs_standard_fields.md) - IFRS 标准字段映射
