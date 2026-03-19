# Pipeline 架构指南

> 本文档介绍 value_investment 项目的 Pipeline 架构设计和使用方法。

**更新时间**: 2026-03-19

---

## 目录

1. [架构概述](#1-架构概述)
2. [核心组件](#2-核心组件)
3. [数据流](#3-数据流)
4. [字段系统](#4-字段系统)
5. [Handler 开发](#5-handler-开发)
6. [Calculator 开发](#6-calculator-开发)
7. [测试指南](#7-测试指南)
8. [常见问题](#8-常见问题)

---

## 1. 架构概述

Pipeline 是一个基于消息总线模式的财务数据获取和处理框架，支持 A 股/港股/美股三市场。

### 1.1 设计原则

| 原则 | 说明 |
|-----|------|
| **依赖注入** | 使用 Container 管理组件依赖 |
| **消息总线** | Handler 通过 MessageBus 协作 |
| **快速拒绝** | Handler 通过 `_can_handle_market()` 快速跳过不相关消息 |
| **字段标准化** | 统一使用 IFRS 标准字段名 |
| **计算解耦** | 派生字段通过 Calculator 计算 |

### 1.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         PipelineAPI                              │
│                      (high-level API)                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MessageBus                                 │
│                   (消息总线, 多轮处理)                            │
│              9 个 Handler 注册到总线上                            │
└─────────────────────────────────────────────────────────────────┘
         │            │            │            │            │
         ▼            ▼            ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ AStatement   │ │ AIndicator   │ │ AMarket      │  ← A 股 Handler 组
└──────────────┘ └──────────────┘ └──────────────┘
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ HKStatement  │ │ HKIndicator  │ │ HKMarket     │  ← 港股 Handler 组
└──────────────┘ └──────────────┘ └──────────────┘
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ USStatement  │ │ USIndicator  │ │ USMarket     │  ← 美股 Handler 组
└──────────────┘ └──────────────┘ └──────────────┘
         │            │            │            │            │
         ▼            ▼            ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ TushareProvider│ AkshareProvider│  YFinanceProvider │  ← Data Provider 组
└──────────────┘ └──────────────┘ └──────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Calculator                                │
│              (派生字段计算: gross_profit, inventory_turnover)     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Handler 快速拒绝模式

每个 Handler 实现快速拒绝，避免无效处理：

```python
async def handle(self, message: Message) -> None:
    # 快速拒绝：市场不匹配
    if not self._can_handle_market(message):
        return
    # 快速拒绝：无支持的字段
    if not self._can_handle_fields(message):
        return
    # 真正处理...
    await self._handle_impl(message)
```

---

## 2. 核心组件

### 2.1 Container (依赖注入容器)

```python
from value_investment.pipeline.container import Container

# 创建/获取容器
container = Container.create()

# 访问组件
bus = container.bus()
# 访问 A 股 Handler 组
a_handler = container.a_stock_statement_handler()
# 访问港股 Handler 组
hk_handler = container.hk_stock_indicator_handler()
```

**职责**: 统一管理所有组件的创建和依赖关系。Container.create() 注册 9 个 Handler 到消息总线。

**注册的 9 个 Handler**:

| Handler | 市场 | 数据类型 | Provider |
|---------|------|---------|----------|
| AStockStatementHandler | A 股 | 财务报表 (BS/IS/CF) | Tushare |
| AStockIndicatorHandler | A 股 | 财务指标 | Tushare |
| AStockMarketHandler | A 股 | 市值/PE/PB | Tushare |
| HKStockStatementHandler | 港股 | 财务报表 | Akshare |
| HKStockIndicatorHandler | 港股 | 财务指标 | Akshare |
| HKStockMarketHandler | 港股 | 市值/PE/PB | Akshare |
| USStockStatementHandler | 美股 | 财务报表 | YFinance/Akshare |
| USStockIndicatorHandler | 美股 | 财务指标 | YFinance/Akshare |
| USStockMarketHandler | 美股 | 市值/PE/PB | YFinance/Akshare |

### 2.2 MessageBus (消息总线)

```python
from value_investment.pipeline.bus.message_bus import MessageBus

bus = MessageBus()
bus.register(handler1)
bus.register(handler2)

# 多轮处理: 持续调用 handler 直到没有字段可处理
await bus.process(message)
```

**职责**: 协调多个 Handler 处理消息，实现多轮数据获取。

### 2.3 Message (消息)

```python
from value_investment.pipeline.bus.message import Message

message = Message(
    symbol="600519",
    market="A股",
    end="2024",
    years=10,
    require={"roe", "roic", "gross_profit"},
)
```

**属性**:
- `symbol`: 股票代码
- `market`: 市场 (A股/港股/美股)
- `end`: 截止年份
- `years`: 获取年数
- `require`: 待获取字段集合
- `results`: 已获取字段数据 `{field: {year: value}}`

### 2.4 Handler (处理器)

Handler 负责从数据源获取特定字段的数据。每个 Handler 继承自 `BaseHandler`，实现快速拒绝模式。

```python
from value_investment.pipeline.handlers.base_handler import BaseHandler

class BaseHandler(ABC):
    @property
    def can_handle(self) -> set[str]:
        """该 Handler 能处理的字段集合"""
        return self._supported_fields & (
            self._provider.supported_fields if self._provider else set()
        )

    def _can_handle_market(self, message: Message) -> bool:
        """快速判断：是否处理该市场"""
        return message.market == self.target_market

    def _can_handle_fields(self, message: Message) -> bool:
        """快速判断：是否有可处理的字段"""
        return bool(message.require & self.can_handle)

    async def handle(self, message: Message) -> None:
        # 快速拒绝：市场不匹配
        if not self._can_handle_market(message):
            return
        # 快速拒绝：无支持的字段
        if not self._can_handle_fields(message):
            return
        # 交给子类处理
        await self._handle_impl(message)

    @abstractmethod
    async def _handle_impl(self, message: Message) -> None:
        """子类实现具体处理逻辑"""
        pass
```

**Handler 类型**:

| Handler | 字段数量 | 数据来源 |
|---------|---------|---------|
| StatementHandler | ~26 | balance_sheet + income_statement + cash_flow |
| IndicatorHandler | ~17 | fina_indicator API |
| MarketHandler | ~6 | daily_basic API |

### 2.5 Calculator (计算器)

Calculator 负责计算派生字段。**所有 Calculator 必须使用 `@calculator` 装饰器注册**。

```python
from value_investment.pipeline.calculators import calculator
from value_investment.pipeline.fields import IFRSFields

@calculator  # ← 必须！否则不会被发现
class GrossProfitCalculator:
    name = IFRSFields.GROSS_PROFIT
    
    required_fields = {
        IFRSFields.TOTAL_REVENUE,
        IFRSFields.OPERATING_COST,
    }
    
    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        """从已有数据计算派生字段"""
        revenue = results.get(IFRSFields.TOTAL_REVENUE, {})
        cost = results.get(IFRSFields.OPERATING_COST, {})
        return {year: revenue.get(year, 0) - cost.get(year, 0) for year in revenue}
```

**已注册的 Calculator**:

| Calculator | 字段名 | 依赖字段 |
|-----------|--------|---------|
| GrossProfitCalculator | `gross_profit` | revenue, operating_cost |
| InventoryTurnoverCalculator | `inventory_turnover` | operating_cost, inventory |
| ImpliedGrowthCalculator | `implied_growth` | operating_cash_flow, capital_expenditure, market_cap |

---

## 3. 数据流

### 3.1 完整数据流

```
1. 用户调用 API
   ┌─────────────────────────────────────────────┐
   │ api = PipelineAPI()                        │
   │ result = await api.get_data("600519",     │
   │     ["roe", "roic", "gross_profit"],      │
   │     end="2024", years=10)                 │
   └─────────────────────────────────────────────┘
                       │
                       ▼
2. API 创建 Message
   ┌─────────────────────────────────────────────┐
   │ message.require = {"roe", "roic",          │
   │     "gross_profit"}                        │
   │ message.results = {}                       │
   └─────────────────────────────────────────────┘
                       │
                       ▼
3. MessageBus 多轮处理
   ┌─────────────────────────────────────────────┐
   │ Round 1: Handler 能直接获取的字段            │
   │   - AStockStatementHandler: total_revenue │
   │   - AStockIndicatorHandler: roe           │
   │   - message.require -= {total_revenue, roe}│
   │   - message.results[...] = {...}           │
   │                                           │
   │ Round 2: 检查是否有新字段可获取              │
   │   - message.require = {"gross_profit"}    │
   │   - 无法直接获取 (需要计算)                 │
   │   - 退出循环                               │
   └─────────────────────────────────────────────┘
                       │
                       ▼
4. Calculator 计算派生字段
   ┌─────────────────────────────────────────────┐
   │ _apply_calculators(message)                │
   │                                           │
   │ for field in {"gross_profit"}:            │
   │   calculator = CALCULATOR_MAP[field]      │
   │   if required_fields ⊆ results:          │
   │     calculated = calculator.calculate()    │
   │     message.results[field] = calculated   │
   │     message.require -= {field}            │
   └─────────────────────────────────────────────┘
                       │
                       ▼
5. 返回结果
   ┌─────────────────────────────────────────────┐
   │ return message.results                     │
   │ {                                          │
   │   "roe": {2024: 28.5, 2023: 27.1, ...},   │
   │   "roic": {2024: 22.3, 2023: 21.8, ...},  │
   │   "gross_profit": {2024: 902e9, ...},     │
   │ }                                          │
   └─────────────────────────────────────────────┘
```

### 3.2 多市场支持

| 市场 | 代码格式 | Handler | 数据源 |
|-----|---------|---------|--------|
| A 股 | 6 位数字 (0/3/6 开头) | AStockHandler | Tushare |
| 港股 | 5 位数字 | HKStockHandler | Akshare |
| 美股 | 字母代码 | USStockHandler | YFinance |

**市场自动检测**:
```python
def _detect_market(self, symbol: str) -> str:
    if len(symbol) == 5 and symbol.isdigit():
        return "港股"
    elif len(symbol) == 6 and symbol.isdigit() and symbol.startswith(("0", "3", "6")):
        return "A股"
    else:
        return "美股"
```

---

## 4. 字段系统

### 4.1 标准字段 (IFRSFields)

项目定义了 40 个标准财务字段：

```python
from value_investment.pipeline.fields import IFRSFields

# 资产负债表
total_assets, total_liabilities, total_equity
current_assets, current_liabilities
cash_and_equivalents, inventory
accounts_receivable, accounts_payable

# 利润表
total_revenue, net_profit
operating_profit, gross_profit, operating_cost

# 现金流量表
operating_cash_flow, investing_cash_flow
financing_cash_flow, capital_expenditure

# 指标
roe, roa, gross_margin, net_profit_margin
current_ratio, quick_ratio, debt_ratio
asset_turnover, inventory_turnover, receivable_turnover

# 市场数据
pe_ratio, pb_ratio, market_cap
basic_eps, diluted_eps, book_value_per_share
```

### 4.2 字段映射 (CORE_FIELD_MAPPING)

每个标准字段定义了 A 股/港股/美股的具体字段名：

```python
CORE_FIELD_MAPPING = {
    "total_revenue": {
        "A股": "营业总收入",
        "港股": "收益",
        "美股": "totalRevenue",
    },
    "roe": {
        "A股": "净资产收益率(%)",
        "港股": "股东权益回报率(%)",
        "美股": "returnOnEquity",
    },
    # ...
}
```

### 4.3 Calculator 字段

派生字段通过 Calculator 计算，需要声明依赖字段：

```python
class InventoryTurnoverCalculator:
    name = IFRSFields.INVENTORY_TURNOVER
    required_fields = {
        IFRSFields.OPERATING_COST,  # 营业成本
        IFRSFields.INVENTORY,       # 存货
    }
```

---

## 5. Handler 开发

### 5.1 创建新 Handler

继承 `BaseHandler` 实现快速拒绝模式：

```python
# src/value_investment/pipeline/handlers/my_handler.py
from value_investment.pipeline.handlers.base_handler import BaseHandler

# 定义支持的字段
MY_HANDLER_FIELDS: set[str] = {
    "total_revenue",
    "net_profit",
}

class MyStockStatementHandler(BaseHandler):
    """自定义股票数据处理器"""

    def __init__(self, provider=None):
        super().__init__(provider, "A股", MY_HANDLER_FIELDS)

    async def _handle_impl(self, message: Message) -> None:
        """处理消息"""
        to_handle = message.require & self.can_handle
        if not to_handle:
            return

        # 从数据源获取数据
        data = self._provider.fetch_financial_data(
            stock_code=message.symbol,
            fields=to_handle,
            end_year=int(message.end[:4]),
            years=message.years,
        )

        # 添加结果
        for field, values in data.items():
            if values:
                message.add_result(field, values)
```

### 5.2 Handler 示例 (AStockStatementHandler)

```python
from value_investment.pipeline.handlers.a_statement import AStockStatementHandler

# 字段定义 (来自 CORE_FIELD_MAPPING)
A_STOCK_STATEMENT_FIELDS: set[str] = {
    # 资产负债表
    "total_assets", "total_liabilities", "total_equity",
    "current_assets", "current_liabilities",
    "cash_and_equivalents", "inventory",
    "accounts_receivable", "accounts_payable",
    # 利润表
    "total_revenue", "net_profit", "operating_profit",
    # 现金流量表
    "operating_cash_flow", "investing_cash_flow",
    "financing_cash_flow",
}

class AStockStatementHandler(BaseHandler):
    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_STOCK_STATEMENT_FIELDS)

    async def _handle_impl(self, message: Message) -> None:
        to_handle = message.require & self.can_handle
        if not to_handle:
            return

        data = self._provider.fetch_financial_data(
            stock_code=message.symbol,
            fields=to_handle,
            end_year=int(message.end[:4]),
            years=message.years,
        )

        for field, values in data.items():
            if values:
                message.add_result(field, values)
```

### 5.3 注册 Handler

在 `Container.create()` 中注册:

```python
@classmethod
def create(cls) -> "Container":
    if cls._instance is None:
        container = cls()
        container.bus().register(container.my_handler())
        cls._instance = container
    return cls._instance
```

---

## 6. Calculator 开发

### 6.1 创建新 Calculator

**重要**: 所有 Calculator 必须使用 `@calculator` 装饰器，否则不会被发现。

```python
# src/value_investment/pipeline/calculators/xxx.py
from typing import Any
from value_investment.pipeline.calculators import calculator
from value_investment.pipeline.fields import IFRSFields

@calculator  # ← 必须！
class XxxCalculator:
    """XXX 计算器
    
    公式说明:
    - XXX = A / B
    - 其中 A = xxx, B = xxx
    """
    
    name = IFRSFields.XXX  # 字段名
    
    required_fields = {
        IFRSFields.FIELD_A,
        IFRSFields.FIELD_B,
    }
    
    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        """计算 XXX
        
        Args:
            results: {field: {year: value}}
        
        Returns:
            {year: xxx_value}
        """
        field_a = results.get(IFRSFields.FIELD_A, {})
        field_b = results.get(IFRSFields.FIELD_B, {})
        
        return {
            year: field_a.get(year, 0) / field_b.get(year, 1)
            for year in set(field_a.keys()) | set(field_b.keys())
        }
```

### 6.2 自动注册

**无需手动注册**！使用 `@calculator` 装饰器后，Calculator 会自动被发现并注册。

```python
# calculators/__init__.py 会自动发现并注册所有带 @calculator 的类
# 不需要手动添加到 ALL_CALCULATORS
```

### 6.3 验证依赖链

每次运行测试时，会自动验证所有 Calculator 的依赖字段是否可获取：

```bash
# 运行测试时自动验证
uv run python -m pytest tests/pipeline/test_validator.py

# 输出示例
============================================================
Pipeline Calculator Validation
============================================================

✅ gross_profit
    ✓ total_revenue                       → AStockStatementHandler
    ✓ operating_cost                      → AStockStatementHandler

✅ implied_growth
    ✓ operating_cash_flow                 → AStockStatementHandler
    ✓ capital_expenditure                 → AStockStatementHandler
    ✓ market_cap                          → AStockMarketHandler

============================================================
Total: 3 OK, 0 Missing
============================================================
```

### 6.4 计算器执行时机

Calculator 在 `PipelineAPI.get_data()` 中，数据获取完成后执行：

```python
async def get_data(self, symbol, fields, ...):
    # 1. 通过 MessageBus 获取原始数据
    await self._container.bus().process(message)
    
    # 2. 计算派生字段
    self._apply_calculators(message)
    
    # 3. 检查是否所有字段都已获取
    if message.require:
        raise ValueError(f"Missing fields: {message.require}")
    
    return message.results
```

---

## 7. 测试指南

### 7.1 测试 Calculator

```python
# tests/pipeline/test_xxx_calculator.py
import pytest
from value_investment.pipeline.calculators import calculator
from value_investment.pipeline.fields import IFRSFields

@calculator  # ← 必须
class XxxCalculator:
    name = IFRSFields.XXX
    required_fields = {IFRSFields.FIELD_A, IFRSFields.FIELD_B}
    
    def calculate(self, results):
        field_a = results.get(IFRSFields.FIELD_A, {})
        field_b = results.get(IFRSFields.FIELD_B, {})
        return {year: field_a.get(year, 0) / field_b.get(year, 1) for year in field_a}

class TestXxxCalculator:
    def test_required_fields(self):
        calc = XxxCalculator()
        assert IFRSFields.FIELD_A in calc.required_fields
        assert IFRSFields.FIELD_B in calc.required_fields
    
    def test_name(self):
        calc = XxxCalculator()
        assert calc.name == IFRSFields.XXX
    
    def test_calculate(self):
        calc = XxxCalculator()
        results = {
            IFRSFields.FIELD_A: {2024: 100, 2023: 80},
            IFRSFields.FIELD_B: {2024: 20, 2023: 20},
        }
        calculated = calc.calculate(results)
        
        assert calculated[2024] == 5.0
        assert calculated[2023] == 4.0
```

### 7.2 测试依赖链验证

```python
# tests/pipeline/test_validator.py
from value_investment.pipeline.calculators import ALL_CALCULATORS
from value_investment.pipeline.validator import assert_all_valid

def test_all_calculators_have_valid_dependencies():
    """所有 Calculator 的依赖字段都必须有 Handler 支持"""
    assert_all_valid(ALL_CALCULATORS)  # 失败会抛出 AssertionError
```

### 7.3 测试 Handler

```python
# tests/pipeline/test_my_handler.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from value_investment.pipeline.handlers.my_handler import MyStockHandler
from value_investment.pipeline.bus.message import Message

class TestMyHandler:
    @pytest.fixture
    def handler(self):
        provider = MagicMock()
        return MyStockHandler(provider)
    
    @pytest.mark.asyncio
    async def test_handle_basic(self, handler):
        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=5,
            require={IFRSFields.TOTAL_REVENUE},
        )
        
        await handler.handle(message)
        
        assert IFRSFields.TOTAL_REVENUE not in message.require
        assert IFRSFields.TOTAL_REVENUE in message.results
    
    @pytest.mark.asyncio
    async def test_handle_unsupported_field(self, handler):
        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=5,
            require={"unsupported_field"},
        )
        
        await handler.handle(message)
        
        # 不支持的字段不会被处理
        assert "unsupported_field" in message.require
```

### 7.3 端到端测试

```python
# tests/pipeline/test_e2e_xxx.py
import pytest
from value_investment.pipeline.api import PipelineAPI

class TestE2E:
    @pytest.mark.asyncio
    async def test_get_data_with_calculated_field(self):
        api = PipelineAPI()
        result = await api.get_data(
            "600519",
            ["roe", "roic", "gross_profit"],
            end="2024",
            years=5,
        )
        
        assert "roe" in result
        assert "roic" in result
        assert "gross_profit" in result
        
        # 验证数据结构
        for field, data in result.items():
            assert isinstance(data, dict)
            assert all(isinstance(k, int) for k in data.keys())
```

### 7.4 运行测试

```bash
# 运行所有测试
uv run python -m pytest tests/pipeline/ -v

# 运行特定测试
uv run python -m pytest tests/pipeline/test_xxx_calculator.py -v

# 运行端到端测试
uv run python -m pytest tests/pipeline/test_e2e_roic.py -v
```

---

## 8. 常见问题

### Q1: 新增字段需要修改哪些文件？

1. **字段定义**: `src/value_investment/pipeline/fields.py` → 添加 `IFRSFields.NEW_FIELD`
2. **字段映射**: `src/value_investment/data/mapper.py` → `CORE_FIELD_MAPPING["new_field"]`
3. **Handler 支持**: 在相应 Handler 的 `_supported_fields` 中添加（如 A_STOCK_STATEMENT_FIELDS）
4. **测试**: 添加单元测试和集成测试

### Q2: 如何添加新的派生字段计算器？

**步骤**:

1. **创建文件**: `src/value_investment/pipeline/calculators/xxx.py`

2. **实现 Calculator** (必须加 `@calculator`):
   ```python
   from value_investment.pipeline.calculators import calculator
   from value_investment.pipeline.fields import IFRSFields
   
   @calculator  # ← 必须！
   class XxxCalculator:
       name = IFRSFields.XXX
       required_fields = {IFRSFields.FIELD_A, IFRSFields.FIELD_B}
       
       def calculate(self, results):
           # 计算逻辑
           return {year: value for year, value in ...}
   ```

3. **写测试**: `tests/pipeline/test_xxx_calculator.py`

4. **运行测试** (自动验证依赖链):
   ```bash
   uv run python -m pytest tests/pipeline/test_xxx_calculator.py
   ```

**无需手动注册**！`@calculator` 装饰器会自动注册。

**验证依赖链**:
- 运行 `pytest tests/pipeline/test_validator.py` 自动验证
- 如果依赖字段没有 Handler 支持，会显示清晰的错误信息

### Q3: 如何添加新的市场支持？

1. **创建 Handler 组**: `handlers/hk_statement.py`, `handlers/hk_indicator.py`, `handlers/hk_market.py`
2. **创建/配置 Provider**: `data/akshare_provider.py` 等
3. **在 Container 中注册**: 在 `container.py` 的 `create()` 中添加
4. **在 `CORE_FIELD_MAPPING` 中添加市场字段映射**

### Q4: Handler 和 Calculator 的区别？

| 特性 | Handler | Calculator |
|-----|---------|------------|
| 数据来源 | 数据源 (API/数据库) | 已有数据 |
| 执行时机 | MessageBus 处理循环中 | API 层数据获取后 |
| 典型用途 | 获取原始财务数据 | 计算派生指标 |
| 示例 | 获取 ROE、营收、净利润 | 计算毛利、存货周转率 |

### Q5: 如何调试数据获取问题？

1. **查看 Handler 支持的字段**: 
   ```python
   handler.can_handle & message.require  # 查看交集
   ```

2. **检查市场匹配**: 
   ```python
   handler._can_handle_market(message)  # 快速拒绝检查
   ```

3. **检查字段映射**: 确认字段映射正确
   ```python
   from value_investment.data.mapper import DataMapper
   DataMapper.get_market_field("roe", "A股")  # 返回 A 股字段名
   ```

---

## 附录

### A. 文件结构

```
src/value_investment/pipeline/
├── __init__.py
├── api.py              # 高层 API
├── container.py        # 依赖注入容器 (注册 9 个 Handler)
├── fields.py           # 标准字段定义 (IFRSFields)
├── validator.py        # 依赖链验证工具
├── bus/
│   ├── __init__.py
│   ├── message.py      # Message 数据类
│   └── message_bus.py  # 消息总线
├── handlers/
│   ├── __init__.py
│   ├── base.py         # Handler Protocol (旧)
│   ├── base_handler.py # BaseHandler 基类 (快速拒绝模式)
│   ├── a_statement.py      # A 股财务报表 Handler
│   ├── a_indicator.py       # A 股财务指标 Handler
│   ├── a_market.py         # A 股市值数据 Handler
│   ├── hk_statement.py     # 港股财务报表 Handler
│   ├── hk_indicator.py      # 港股财务指标 Handler
│   ├── hk_market.py        # 港股市值数据 Handler
│   ├── us_statement.py     # 美股财务报表 Handler
│   ├── us_indicator.py     # 美股财务指标 Handler
│   └── us_market.py       # 美股市值数据 Handler
├── calculators/
│   ├── __init__.py     # 导出 @calculator 装饰器
│   ├── registry.py     # 装饰器实现 + 注册表
│   ├── gross_profit.py # @calculator
│   ├── implied_growth.py # @calculator
│   └── inventory_turnover.py # @calculator
└── data/
    ├── tushare_provider.py  # Tushare Provider
    ├── tushare_mapper.py    # Tushare 字段映射
    ├── provider.py         # DataProvider Protocol
    └── mapper.py           # 核心字段映射
```

**9 Handler 架构**:

```
Market ╲ Type │  Statement      Indicator     Market
─────────────┼──────────────────────────────────────
A股           │ AStatement      AIndicator     AMarket
港股          │ HKStatement     HKIndicator    HKMarket
美股          │ USStatement     USIndicator    USMarket
```

### B. 相关文档

- [market_indicator_differences.md](market_indicator_differences.md) - 三市场指标差异
- [ifrs_standard_fields.md](ifrs_standard_fields.md) - IFRS 标准字段
- [plans/README.md](plans/README.md) - 实施计划索引
- [CLAUDE.md](../CLAUDE.md) - 项目快速指南

### C. Handler 拆分历史

| 日期 | 变更 |
|------|------|
| 2026-03-19 | 拆分为 9 个 Handler（3 市场 × 3 数据类型），实现快速拒绝模式 |

### Q6: 忘记加 `@calculator` 装饰器会怎样？

**后果**: Calculator **不会被注册**，请求该字段时会报错 "Missing fields"。

**示例**:
```python
# ❌ 错误：忘记装饰器
class ROICCalculator:
    name = "roic"
    ...

# ✅ 正确
from value_investment.pipeline.calculators import calculator

@calculator
class ROICCalculator:
    name = "roic"
    ...
```

**验证**: 运行 `pytest tests/pipeline/test_validator.py` 会显示缺失的 Calculator。
