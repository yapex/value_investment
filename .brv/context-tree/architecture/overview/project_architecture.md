---
title: Project Architecture
tags: []
keywords: []
importance: 53
recency: 2
maturity: draft
accessCount: 3
createdAt: '2026-03-12T05:01:51.468Z'
updatedAt: '2026-03-19T07:30:00.000Z'
---
## Raw Concept
**Task:**
Value investment analysis tool supporting A-share/HK-share/US-share fundamental analysis

**Changes (2026-03-19):**
- 新增 Pipeline 架构 (src/value_investment/pipeline/)
- Pipeline 采用 Handler + Provider 解耦模式

**Files:**
- src/value_investment/api.py - Python API 入口
- src/value_investment/cli.py - 命令行接口
- src/value_investment/pipeline/ - 新架构 (Handler + Provider)
- src/value_investment/data/providers/ - 旧架构 providers (待迁移)
- src/value_investment/indicators/ - 指标计算
- src/value_investment/data/mapper.py - 字段映射 (CORE_FIELD_MAPPING)

**Flow:**
User input -> CLI/API -> Pipeline (MessageBus + Handlers) -> Providers -> Calculators -> Analysis output

## Narrative
### Architecture: Two Layers
项目存在两层架构:

1. **Pipeline 层 (新架构)** - src/value_investment/pipeline/
   - Handler + Provider 解耦模式
   - MessageBus 路由消息
   - 自动市场检测

2. **旧架构** - src/value_investment/data/
   - 直接使用 Providers
   - 待迁移/废弃

### Dependencies
- 数据源: akshare + tushare
- DI 容器: dependency_injector
- Python 项目使用 uv 管理

### Highlights
- 支持三市场: A股(6位数字), 港股(5位数字), 美股(字母)
- 不同数据类型有不同的缓存策略
- 新架构支持 dry run 验证

### Examples
CLI commands:
```bash
uv run python -m value_investment.cli --help
uv run python -m value_investment.cli hist 600519 --end 20241231
uv run python -m value_investment.cli financial 600519 --end 2024
```

Test command:
```bash
uv run python -m pytest tests/ -v
```

## Facts
- **data_source**: Data sources are akshare + tushare [project]
- **tech_stack**: Project uses Python and uv package manager [project]
- **a_share_format**: A-share codes are 6-digit numbers (starting with 0/3/6) [project]
- **hk_share_format**: HK-share codes are 5-digit numbers [project]
- **us_share_format**: US-share codes are letter codes [project]
- **pipeline_architecture**: 新架构使用 Handler + Provider 解耦模式 [project]
- **di_container**: 使用 dependency_injector 作为 DI 容器 [project]

## Architecture Details

### Pipeline Components
```
PipelineAPI (入口)
    ↓
Container (DI 容器)
    ↓
MessageBus (消息总线)
    ↓
9 Handlers (3市场 × 3类型)
    ↓
3 Providers (Tushare/HK/US)
    ↓
Calculators (派生字段计算)
```

### Handler Types (per market)
- StatementHandler: 资产负债表 + 利润表 + 现金流量表
- IndicatorHandler: 财务指标 (ROE/ROA/毛利率等)
- MarketHandler: 市值数据 (PE/PB/市值)

### Migration Status (2026-03-19)
- A股 TushareProvider: ✅ 完成
- 美股 USProvider: ✅ 完成
- 港股 HKProvider: ⚠️ 待完善 (fetch_financial_data 未实现)
