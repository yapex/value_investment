---
title: Pipeline Architecture
tags: [pipeline, handler, provider, architecture]
keywords: [pipeline, handler, provider, message_bus, calculator, validator]
importance: 55
maturity: draft
accessCount: 1
createdAt: '2026-03-19T07:30:00.000Z'
updatedAt: '2026-03-19T07:30:00.000Z'
---
## Raw Concept
**Task:**
Document the new Pipeline architecture for financial data processing

**Architecture:**
Handler + Provider 解耦模式，通过 MessageBus 路由消息

## Overview
Pipeline 是项目的新架构，采用 **Handler + Provider** 解耦模式:
- Handler: 业务逻辑（市场识别、字段路由）
- Provider: 数据获取（Tushare/AkShare API）
- MessageBus: 消息总线（协调 Handler）

## Core Components

### 1. PipelineAPI (入口)
- **文件**: src/value_investment/pipeline/api.py
- **方法**:
  - `get_data(symbol, fields, end, years, market)`: 获取数据
  - `validate(symbol, fields, market)`: Dry run 验证
- **功能**:
  - 自动市场检测 (A股/港股/美股)
  - 字段扩展 (Calculator 依赖)
  - 派生字段计算

### 2. Container (DI 容器)
- **文件**: src/value_investment/pipeline/container.py
- **依赖**: dependency_injector
- **单例模式**: `Container.create()`
- **注册内容**:
  - 9 个 Handler
  - 3 个 Provider
  - 缓存实例

### 3. MessageBus (消息总线)
- **文件**: src/value_investment/pipeline/bus/message_bus.py
- **功能**: 
  - 消息路由到所有 Handler
  - 多轮执行直到没有新字段可处理
- **核心方法**: `process(message)`

### 4. Message (消息)
- **文件**: src/value_investment/pipeline/bus/message.py
- **字段**:
  - `symbol`: 股票代码
  - `market`: 市场 (A股/港股/美股)
  - `require`: 需要的字段集合
  - `results`: 结果字典 {field: {year: value}}

### 5. Handlers (9个)
- **基类**: src/value_investment/pipeline/handlers/base_handler.py
- **快速拒绝模式**: 市场不匹配或无可处理字段时直接返回
- **Handler 列表**:

| 市场 | StatementHandler | IndicatorHandler | MarketHandler |
|------|------------------|------------------|---------------|
| A股 | AStockStatementHandler | AStockIndicatorHandler | AStockMarketHandler |
| 港股 | HKStockStatementHandler | HKStockIndicatorHandler | HKStockMarketHandler |
| 美股 | USStockStatementHandler | USStockIndicatorHandler | USStockMarketHandler |

### 6. Providers (数据源)
- **Protocol**: src/value_investment/pipeline/data/provider.py
- **方法**:
  - `fetch_financial_data()`: 财务报表
  - `fetch_indicators()`: 财务指标
  - `fetch_market_data()`: 市值数据
- **实现**:

| Provider | 市场 | 数据源 |
|----------|------|--------|
| TushareProvider | A股 | Tushare API |
| HKProvider | 港股 | AkShare |
| USProvider | 美股 | AkShare 东财数据 |

### 7. Calculators (派生字段)
- **文件**: src/value_investment/pipeline/calculators/
- **装饰器**: `@calculator`
- **已有计算器**:
  - GrossProfit: 毛利润
  - ImpliedGrowth: 隐含增长率
  - InventoryTurnover: 存货周转率
  - OperatingProfitMargin: 营业利润率

### 8. Fields (字段定义)
- **文件**: src/value_investment/pipeline/fields.py
- **IFRSFields**: 国际标准字段 (已冻结，禁止新增)
- **CustomFields**: 自定义字段
- **ALL_FIELDS**: IFRSFields + CustomFields

### 9. Validator (验证器)
- **文件**: src/value_investment/pipeline/validator.py
- **功能**:
  - 字段注册检查
  - Handler 声明一致性检查
  - Calculator 依赖检查
  - 市场覆盖检查
- **输出**: ValidationReport

## Data Flow
```
1. PipelineAPI.get_data(symbol, fields)
2. 自动检测市场
3. 创建 Message，扩展 require 字段 (Calculator 依赖)
4. MessageBus.process(message)
5. 遍历所有 Handler:
   - 快速拒绝: 市场不匹配 → 返回
   - 快速拒绝: 无可处理字段 → 返回
   - 处理: 调用 Provider 获取数据
   - 添加结果: message.add_result(field, values)
6. 重复步骤 5 直到没有新字段可处理
7. PipelineAPI._apply_calculators(message)
8. 返回 message.results
```

## Quick Reject Pattern
Handler 使用快速拒绝模式避免无效处理:
```python
async def handle(self, message):
    # 快速拒绝: 市场不匹配
    if not self._can_handle_market(message):
        return
    # 快速拒绝: 无支持的字段
    if not self._can_handle_fields(message):
        return
    # 交给子类处理具体逻辑
    await self._handle_impl(message)
```

## Migration Status
- ✅ A股 TushareProvider: 完成
- ✅ 美股 USProvider: 完成
- ⚠️ 港股 HKProvider: 待完善 (fetch_financial_data 未实现)

## Key Files
```
src/value_investment/pipeline/
├── api.py                    # PipelineAPI
├── container.py             # DI Container
├── validator.py             # Validator
├── fields.py                # Field definitions
├── bus/
│   ├── message_bus.py      # MessageBus
│   └── message.py           # Message
├── handlers/
│   ├── base_handler.py      # BaseHandler
│   ├── base.py              # Handler Protocol
│   ├── a_statement.py       # A股 Statement
│   ├── a_indicator.py       # A股 Indicator
│   ├── a_market.py          # A股 Market
│   ├── hk_statement.py      # 港股 Statement
│   ├── hk_indicator.py      # 港股 Indicator
│   ├── hk_market.py         # 港股 Market
│   ├── us_statement.py     # 美股 Statement
│   ├── us_indicator.py      # 美股 Indicator
│   └── us_market.py         # 美股 Market
├── data/
│   ├── provider.py          # DataProvider Protocol
│   ├── tushare_provider.py  # A股 Provider
│   ├── hk_provider.py       # 港股 Provider
│   └── us_provider.py       # 美股 Provider
└── calculators/
    ├── __init__.py          # Calculator registry
    ├── registry.py          # @calculator decorator
    ├── gross_profit.py
    ├── implied_growth.py
    ├── inventory_turnover.py
    └── operating_profit_margin.py
```

## Facts
- **pipeline_api**: PipelineAPI 是高层入口 [project]
- **pipeline_container**: Container 使用 dependency_injector [project]
- **pipeline_message_bus**: MessageBus 支持多轮执行 [project]
- **handler_quick_reject**: Handler 使用快速拒绝模式 [project]
- **calculator_decorator**: 使用 @calculator 装饰器注册 [project]
- **ifrs_fields_frozen**: IFRSFields 已冻结禁止新增 [project]
