# Pipeline 新架构指南

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
└─────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  AStockHandler  │  │  HKStockHandler │  │  USStockHandler │
│     (A股)       │  │     (港股)      │  │     (美股)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ TushareProvider │  │  AkshareProvider│  │  YFinanceProvider│
│   (数据源)      │  │    (数据源)     │  │    (数据源)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Calculator                                │
│              (派生字段计算: gross_profit, inventory_turnover)     │
└─────────────────────────────────────────────────────────────────┘
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
handler = container.a_stock_handler()
calculator = container.calculators()
```

**职责**: 统一管理所有组件的创建和依赖关系。

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

Handler 负责从数据源获取特定字段的数据。

```python
class BaseHandler(ABC):
    @abstractmethod
    async def handle(self, message: Message) -> None:
        """处理消息, 从 message.require 中获取能处理的字段"""
        pass
    
    @property
    @abstractmethod
    def supported_fields(self) -> set[str]:
        """返回该 Handler 支持的字段集合"""
        pass
```

### 2.5 Calculator (计算器)

Calculator 负责计算派生字段。

```python
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
   │   - AStockHandler: roe, roic               │
   │   - message.require -= {"roe", "roic"}     │
   │   - message.results["roe"] = {...}         │
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

```python
# src/value_investment/pipeline/handlers/my_handler.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from value_investment.pipeline.bus.message import Message

class BaseHandler(ABC):
    @abstractmethod
    async def handle(self, message: Message) -> None:
        """处理消息
        
        职责:
        1. 检查 message.require 中是否有自己能处理的字段
        2. 从数据源获取数据
        3. 调用 message.add_result(field, data) 添加结果
        """
        pass
    
    @property
    @abstractmethod
    def supported_fields(self) -> set[str]:
        """返回支持的字段集合"""
        pass
```

### 5.2 Handler 示例

```python
from value_investment.pipeline.handlers.base import BaseHandler
from value_investment.pipeline.bus.message import Message
from value_investment.pipeline.fields import IFRSFields
from value_investment.data.mapper import DataMapper

class MyStockHandler(BaseHandler):
    """自定义股票数据处理器"""
    
    def __init__(self, provider):
        self._provider = provider
    
    @property
    def supported_fields(self) -> set[str]:
        return {
            IFRSFields.TOTAL_REVENUE,
            IFRSFields.NET_PROFIT,
            IFRSFields.ROE,
        }
    
    async def handle(self, message: Message) -> None:
        # 获取该 handler 能处理的字段
        can_handle = message.require & self.supported_fields
        if not can_handle:
            return
        
        # 按数据类型分组获取数据
        balance_fields = can_handle & self._get_balance_fields()
        income_fields = can_handle & self._get_income_fields()
        
        # 获取数据并映射
        if balance_fields:
            data = await self._fetch_balance_sheet(message.symbol, message.market)
            mapped = DataMapper.map_balance_sheet(data)
            for field in balance_fields:
                if field in mapped.columns:
                    message.add_result(field, self._to_year_dict(mapped[field]))
        
        # ... 类似处理其他类型
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

```python
# src/value_investment/pipeline/calculators/xxx.py
from typing import Any
from value_investment.pipeline.fields import IFRSFields

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

### 6.2 注册 Calculator

在 `calculators/__init__.py` 中注册:

```python
from value_investment.pipeline.calculators.xxx import XxxCalculator

ALL_CALCULATORS = [
    GrossProfitCalculator(),
    InventoryTurnoverCalculator(),
    XxxCalculator(),  # 添加新计算器
]

CALCULATOR_MAP = {calc.name: calc for calc in ALL_CALCULATORS}
```

### 6.3 计算器执行时机

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
from value_investment.pipeline.calculators.xxx import XxxCalculator
from value_investment.pipeline.fields import IFRSFields

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
    
    def test_missing_data(self):
        calc = XxxCalculator()
        results = {
            IFRSFields.FIELD_A: {2024: 100},
            # FIELD_B 缺失
        }
        calculated = calc.calculate(results)
        
        # 缺失字段时使用默认值
        assert calculated[2024] == 100  # 100 / 1 (默认值)
```

### 7.2 测试 Handler

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
3. **Handler 支持**: 在相应 Handler 的 `supported_fields` 中添加
4. **测试**: 添加单元测试和集成测试

### Q2: 如何添加新的派生字段计算器？

1. **创建 Calculator**: `src/value_investment/pipeline/calculators/new_calc.py`
2. **定义字段**: 字段名添加到 `IFRSFields`
3. **定义映射**: 如果需要，在 `CORE_FIELD_MAPPING` 中添加
4. **注册**: 在 `calculators/__init__.py` 中注册
5. **测试**: 编写单元测试

### Q3: Handler 和 Calculator 的区别？

| 特性 | Handler | Calculator |
|-----|---------|------------|
| 数据来源 | 数据源 (API/数据库) | 已有数据 |
| 执行时机 | MessageBus 处理循环中 | API 层数据获取后 |
| 典型用途 | 获取原始财务数据 | 计算派生指标 |
| 示例 | 获取 ROE、营收、净利润 | 计算毛利、存货周转率 |

### Q4: 如何调试数据获取问题？

1. **查看详细日志**: MessageBus 和 API 都有 debug 输出
   ```python
   # stderr 会输出处理过程
   await api.get_data("600519", ["roe"])
   ```

2. **检查字段支持**: 确认 Handler 支持目标字段
   ```python
   handler.supported_fields & message.require
   ```

3. **检查数据映射**: 确认字段映射正确
   ```python
   from value_investment.data.mapper import DataMapper
   DataMapper.get_market_field("roe", "A股")  # 返回 A 股字段名
   ```

### Q5: 如何添加新的市场支持？

1. 创建新的 Handler: `handlers/hk_stock.py` 或 `handlers/us_stock.py`
2. 创建/配置 Provider: `data/tushare_provider.py` 等
3. 在 `Container.create()` 中注册 Handler
4. 在 `CORE_FIELD_MAPPING` 中添加市场字段映射
5. 添加市场检测逻辑 (如果需要)

---

## 附录

### A. 文件结构

```
src/value_investment/pipeline/
├── __init__.py
├── api.py              # 高层 API
├── container.py        # 依赖注入容器
├── fields.py           # 标准字段定义
├── bus/
│   ├── __init__.py
│   ├── message.py      # Message 数据类
│   └── message_bus.py  # 消息总线
├── handlers/
│   ├── __init__.py
│   ├── base.py         # Handler 基类
│   ├── a_stock.py      # A股处理器
│   ├── hk_stock.py     # 港股处理器
│   └── us_stock.py     # 美股处理器
├── calculators/
│   ├── __init__.py     # Calculator 注册
│   ├── gross_profit.py
│   └── inventory_turnover.py
└── data/
    ├── tushare_provider.py
    └── mapper.py       # 字段映射
```

### B. 相关文档

- [market_indicator_differences.md](market_indicator_differences.md) - 三市场指标差异
- [ifrs_standard_fields.md](ifrs_standard_fields.md) - IFRS 标准字段
- [CLAUDE.md](../CLAUDE.md) - 项目快速指南
