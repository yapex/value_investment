# CLAUDE.md

## 项目

价值投资分析工具，支持A股/港股/美股基本面分析。数据来源akshare。

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

- `api.py` - 入口
- `cli.py` - CLI
- `data/providers/` - 数据获取
- `indicators/` - 指标计算

## 模式

- Provider: market参数区分市场
- Indicator: data-passing模式
- 缓存: 个股信息次日凌晨失效，历史1年，财务次年6月底
