# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

价值投资分析工具，支持A股/港股/美股的基本面分析。数据来源于akshare，核心功能：个股信息、历史行情、财务报表、指标计算。

## 常用命令

```bash
# 运行测试
uv run python -m pytest tests/ -v

# 运行单个测试
uv run python -m pytest tests/test_provider.py::TestAkshareProviderHistorical -v

# CLI使用
uv run python -m value_investment.cli --help
uv run python -m value_investment.cli hist 600519 --end 20241231
uv run python -m value_investment.cli financial 600519 --end 2024

# 启动Python交互
uv run python -c "from value_investment import ValueInvestment; vi = ValueInvestment()"
```

## 架构

```
api.py          # 统一入口ValueInvestment类
cli.py          # CLI命令入口
data/
  providers/    # AkshareProvider - 各市场数据获取
  cache.py      # SmartCache - 缓存层
indicators/
  factory.py    # IndicatorFactory - 指标工厂
  base.py       # BaseIndicator基类
  simple.py     # 简单指标(ROE/ROA等)
  complex.py    # 复杂指标(DCF/CAGR)
```

## 关键模式

- **Provider层**: 各市场数据获取，通过market参数区分A股/港股/美股
- **Indicator模式**: data-passing模式，指标接收预获取的DataFrame进行计算
- **缓存策略**: 个股信息-次日凌晨失效，历史数据-1年，财务数据-次年6月底

## 注意事项

- Python 3.11+，使用uv管理依赖
- 测试使用pytest，mock akshare API
- 文档见docs/目录，API文档见docs/plans/
