# ROIC Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现基于消息总线的 ROIC 指标计算流程，走通从用户请求到返回结果的完整链路。

**Architecture:**
- 消息总线架构：消息发送者（ROIC Calculator）→ 消息总线 → 消息处理者（数据源）
- 两个篮子：需求篮子（需要什么字段）+ 结果篮子（已获取的字段）
- 多轮执行：处理者按顺序执行，直到需求篮子为空或无新进展
- 处理者内部解决缓存问题

**Tech Stack:**
- Python async/await
- dependency-injector 框架
- TDD 驱动开发
- SmartCache 复用（现有代码）

---

## 阶段 1: 搭建骨架

### Task 1: 创建 pipeline 目录结构和基础文件

**Files:**
- Create: `src/value_investment/pipeline/__init__.py`
- Create: `src/value_investment/pipeline/bus/__init__.py`
- Create: `src/value_investment/pipeline/bus/message.py`
- Create: `src/value_investment/pipeline/bus/message_bus.py`
- Create: `src/value_investment/pipeline/bus/handler.py`
- Create: `src/value_investment/pipeline/fields/__init__.py`
- Create: `src/value_investment/pipeline/fields/registry.py`
- Create: `src/value_investment/pipeline/handlers/__init__.py`
- Create: `src/value_investment/pipeline/handlers/base.py`
- Create: `src/value_investment/pipeline/calculators/__init__.py`
- Create: `src/value_investment/pipeline/calculators/roic.py`
- Create: `src/value_investment/pipeline/container.py`
- Create: `src/value_investment/pipeline/api.py`

**Step 1: Write the failing test**

```python
# tests/pipeline/test_message.py
import pytest
from value_investment.pipeline.bus.message import Message

def test_message_creation():
    msg = Message(
        symbol="600519",
        market="A股",
        end="2024",
        years=10,
        require={"ebit", "total_assets", "cash", "current_liabilities"},
    )
    assert msg.symbol == "600519"
    assert msg.market == "A股"
    assert "ebit" in msg.require
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_message.py::test_message_creation -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'value_investment.pipeline'"

**Step 3: Write minimal implementation**

```python
# src/value_investment/pipeline/__init__.py
"""Pipeline module for message bus based financial data processing"""
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_message.py::test_message_creation -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/pipeline/ tests/pipeline/
git commit -m "feat: create pipeline module structure"
```

---

### Task 2: 实现 Message 类（需求篮子 + 结果篮子）

**Files:**
- Modify: `src/value_investment/pipeline/bus/message.py`
- Test: `tests/pipeline/test_message.py`

**Step 1: Write the failing test**

```python
def test_message_two_baskets():
    msg = Message(
        symbol="600519",
        market="A股",
        end="2024",
        years=10,
        require={"ebit", "total_assets"},
    )
    # 需求篮子
    assert "ebit" in msg.require
    assert "total_assets" in msg.require
    # 结果篮子初始为空
    assert msg.results == {}
    # 放入结果
    msg.add_result("ebit", {2024: 100.0})
    assert "ebit" in msg.results
    assert msg.results["ebit"][2024] == 100.0
    # 从需求篮子移除
    assert "ebit" not in msg.require
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_message.py::test_message_two_baskets -v`
Expected: FAIL with AttributeError or similar

**Step 3: Write minimal implementation**

```python
# src/value_investment/pipeline/bus/message.py
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Message:
    symbol: str
    market: str
    end: str
    years: int
    require: set[str] = field(default_factory=set)
    results: dict[str, dict[int, Any]] = field(default_factory=dict)
    force_refresh: bool = False
    
    def add_result(self, field: str, data: dict[int, Any]) -> None:
        """Add result to results basket"""
        self.results[field] = data
        self.require.discard(field)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_message.py::test_message_two_baskets -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/pipeline/bus/message.py tests/pipeline/test_message.py
git commit -m "feat: implement Message class with two baskets"
```

---

### Task 3: 实现 Handler 基类

**Files:**
- Modify: `src/value_investment/pipeline/handlers/base.py`
- Test: `tests/pipeline/test_handler.py`

**Step 1: Write the failing test**

```python
from value_investment.pipeline.handlers.base import Handler

def test_handler_interface():
    class TestHandler(Handler):
        @property
        def can_handle(self) -> set[str]:
            return {"ebit", "total_assets"}
        
        async def handle(self, message):
            pass
    
    handler = TestHandler()
    assert "ebit" in handler.can_handle
    assert handler.can_handle == {"ebit", "total_assets"}
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_handler.py::test_handler_interface -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/value_investment/pipeline/handlers/base.py
from abc import ABC, abstractmethod
from typing import Any

class Handler(ABC):
    """Handler base class for message processing"""
    
    @property
    @abstractmethod
    def can_handle(self) -> set[str]:
        """Fields this handler can provide"""
        pass
    
    @abstractmethod
    async def handle(self, message) -> None:
        """Handle the message"""
        pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_handler.py::test_handler_interface -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/pipeline/handlers/base.py tests/pipeline/test_handler.py
git commit -m "feat: implement Handler base class"
```

---

### Task 4: 实现 MessageBus（多轮执行逻辑）

**Files:**
- Modify: `src/value_investment/pipeline/bus/message_bus.py`
- Test: `tests/pipeline/test_message_bus.py`

**Step 1: Write the failing test**

```python
from value_investment.pipeline.bus.message_bus import MessageBus
from value_investment.pipeline.handlers.base import Handler

class MockHandler(Handler):
    def __init__(self, can_handle_fields: set[str]):
        self._can_handle = can_handle_fields
    
    @property
    def can_handle(self) -> set[str]:
        return self._can_handle
    
    async def handle(self, message):
        if "ebit" in message.require:
            message.add_result("ebit", {2024: 100.0})

def test_message_bus_single_round():
    bus = MessageBus()
    handler = MockHandler({"ebit"})
    bus.register(handler)
    
    from value_investment.pipeline.bus.message import Message
    msg = Message(
        symbol="600519",
        market="A股",
        end="2024",
        years=10,
        require={"ebit"},
    )
    
    import asyncio
    result = asyncio.run(bus.process(msg))
    
    assert "ebit" in result.results
    assert "ebit" not in result.require
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_message_bus.py::test_message_bus_single_round -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/value_investment/pipeline/bus/message_bus.py
from typing import Any

class MessageBus:
    def __init__(self):
        self.handlers: list = []
    
    def register(self, handler) -> None:
        self.handlers.append(handler)
    
    async def process(self, message) -> Any:
        while message.require:
            before = len(message.require)
            for handler in self.handlers:
                await handler.handle(message)
            after = len(message.require)
            # No progress, exit loop
            if before == after:
                break
        return message
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_message_bus.py::test_message_bus_single_round -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/pipeline/bus/message_bus.py tests/pipeline/test_message_bus.py
git commit -m "feat: implement MessageBus with multi-round execution"
```

---

### Task 5: 实现 ROIC Calculator（消息发送者）

**Files:**
- Modify: `src/value_investment/pipeline/calculators/roic.py`
- Test: `tests/pipeline/test_roic_calculator.py`

**Step 1: Write the failing test**

```python
from value_investment.pipeline.calculators.roic import ROICCalculator

def test_roic_required_fields():
    calc = ROICCalculator()
    assert "ebit" in calc.required_fields
    assert "total_assets" in calc.required_fields
    assert "cash" in calc.required_fields
    assert "current_liabilities" in calc.required_fields
    assert "roic" not in calc.required_fields  # 这是输出，不是输入

def test_roic_calculate():
    calc = ROICCalculator()
    results = {
        "ebit": {2024: 100.0, 2023: 90.0},
        "total_assets": {2024: 1000.0, 2023: 900.0},
        "cash": {2024: 200.0, 2023: 180.0},
        "current_liabilities": {2024: 300.0, 2023: 280.0},
    }
    roic = calc.calculate(results)
    # ROIC = EBIT / (Total Assets - Cash - Current Liabilities)
    # = 100 / (1000 - 200 - 300) = 100 / 500 = 0.2 = 20%
    assert abs(roic[2024] - 0.2) < 0.001
    assert abs(roic[2023] - 0.18) < 0.001
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_roic_calculator.py -v`
Expected: FAIL (ModuleNotFoundError)

**Step 3: Write minimal implementation**

```python
# src/value_investment/pipeline/calculators/roic.py
"""ROIC Calculator"""
from typing import Any

class ROICCalculator:
    """ROIC (Return on Invested Capital) Calculator
    
    ROIC = EBIT / (Total Assets - Cash - Current Liabilities)
    = EBIT / Working Capital
    """
    
    name = "roic"
    
    @property
    def required_fields(self) -> set[str]:
        return {"ebit", "total_assets", "cash", "current_liabilities"}
    
    def calculate(self, results: dict[str, dict[int, Any]]) -> dict[int, float]:
        """Calculate ROIC from results
        
        Args:
            results: {field: {year: value}}
            
        Returns:
            {year: roic_value}
        """
        ebit = results.get("ebit", {})
        total_assets = results.get("total_assets", {})
        cash = results.get("cash", {})
        current_liabilities = results.get("current_liabilities", {})
        
        roic = {}
        for year in ebit:
            invested_capital = (
                total_assets.get(year, 0) 
                - cash.get(year, 0) 
                - current_liabilities.get(year, 0)
            )
            if invested_capital != 0:
                roic[year] = ebit[year] / invested_capital
            else:
                roic[year] = 0.0
        
        return roic
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_roic_calculator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/pipeline/calculators/roic.py tests/pipeline/test_roic_calculator.py
git commit -m "feat: implement ROIC Calculator"
```

---

## 阶段 2: 实现数据处理者

### Task 6: 实现 A股数据处理者（从现有 mapper 读取字段映射）

**Files:**
- Create: `src/value_investment/pipeline/handlers/a_stock.py`
- Test: `tests/pipeline/test_a_stock_handler.py`

**Step 1: Write the failing test**

```python
from value_investment.pipeline.handlers.a_stock import AStockHandler
from value_investment.pipeline.bus.message import Message

class MockCache:
    def __init__(self):
        self.data = {}
    
    def get(self, key):
        return self.data.get(key)
    
    def set(self, key, value):
        self.data[key] = value

async def test_a_stock_handler_provides_fields():
    handler = AStockHandler(cache=MockCache())
    
    # Handler 能处理 A 股的哪些字段
    assert "net_profit" in handler.can_handle
    assert "total_assets" in handler.can_handle
    assert "ebit" in handler.can_handle
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_a_stock_handler.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/value_investment/pipeline/handlers/a_stock.py
"""A 股数据处理者"""
from value_investment.pipeline.handlers.base import Handler

class AStockHandler(Handler):
    """Handler for A股 (A-shares) financial data"""
    
    def __init__(self, cache=None):
        self.cache = cache
        # 从 CORE_FIELD_MAPPING 提取 A 股字段
        from value_investment.data.mapper import CORE_FIELD_MAPPING
        self._can_handle = set()
        for field, market_map in CORE_FIELD_MAPPING.items():
            if "A股" in market_map:
                self._can_handle.add(field)
    
    @property
    def can_handle(self) -> set[str]:
        return self._can_handle
    
    async def handle(self, message) -> None:
        # 简单实现：跳过，等待 Task 8 真实数据获取
        pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_a_stock_handler.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/pipeline/handlers/a_stock.py tests/pipeline/test_a_stock_handler.py
git commit -m "feat: implement AStockHandler with field mapping"
```

---

### Task 7: 实现依赖注入容器

**Files:**
- Modify: `src/value_investment/pipeline/container.py`
- Test: `tests/pipeline/test_container.py`

**Step 1: Write the failing test**

```python
from value_investment.pipeline.container import Container

def test_container_creation():
    container = Container()
    assert container.bus is not None
    assert len(container.bus.handlers) > 0

def test_container_provides_handlers():
    container = Container()
    # 应该有多个 handler 注册
    assert len(container.bus.handlers) >= 2
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_container.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/value_investment/pipeline/container.py
"""Dependency Injection Container"""
from dependency_injector import containers, providers

from value_investment.pipeline.bus.message_bus import MessageBus
from value_investment.pipeline.handlers.a_stock import AStockHandler
from value_investment.pipeline.handlers.hk_stock import HKStockHandler
from value_investment.pipeline.handlers.us_stock import USStockHandler

class Container(containers.DeclarativeContainer):
    """DI Container for Pipeline"""
    
    # SmartCache 复用现有实现
    cache = providers.Singleton(
        lambda: __import__("value_investment.data.cache", fromlist=["SmartCache"]).SmartCache()
    )
    
    # 消息总线
    bus = providers.Singleton(MessageBus)
    
    # Handlers
    a_stock_handler = providers.Singleton(AStockHandler)
    hk_stock_handler = providers.Singleton(HKStockHandler)
    us_stock_handler = providers.Singleton(USStockHandler)
    
    # 组装
    def __init__(self):
        super().__init__()
        # 注册 handlers 到 bus
        self.bus().register(self.a_stock_handler())
        self.bus().register(self.hk_stock_handler())
        self.bus().register(self.us_stock_handler())
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_container.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/pipeline/container.py tests/pipeline/test_container.py
git commit -m "feat: implement DI Container"
```

---

### Task 8: 实现 A股数据处理者的真实数据获取

**Files:**
- Modify: `src/value_investment/pipeline/handlers/a_stock.py`
- Test: `tests/pipeline/test_a_stock_data_fetch.py`

**Step 1: Write the failing test**

```python
# 这个测试会调用真实数据源，需要 mock
import pytest
from unittest.mock import patch, AsyncMock

async def test_a_stock_handler_fetches_data():
    handler = AStockHandler()
    
    msg = Message(
        symbol="600519",
        market="A股",
        end="2024",
        years=10,
        require={"ebit", "net_profit"},
    )
    
    # Mock 数据源
    with patch.object(handler, 'fetch_from_source', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = {
            "ebit": {2024: 100.0, 2023: 90.0},
            "net_profit": {2024: 80.0, 2023: 70.0},
        }
        await handler.handle(msg)
    
    assert "ebit" in msg.results
    assert "net_profit" in msg.results
    assert "ebit" not in msg.require
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_a_stock_data_fetch.py -v`
Expected: FAIL

**Step 3: Write实现**

```python
# src/value_investment/pipeline/handlers/a_stock.py
async def handle(self, message) -> None:
    if message.market != "A股":
        return
    
    # 找出我能处理且在需求篮子里的字段
    to_handle = self.can_handle & message.require
    if not to_handle:
        return
    
    # 从数据源获取（这里先留空，后续完善）
    data = await self.fetch_from_source(message.symbol, to_handle, message.end, message.years)
    
    for field, values in data.items():
        message.add_result(field, values)

async def fetch_from_source(self, symbol, fields, end, years):
    # TODO: 实现真实数据获取
    # 可以复用现有的 data provider
    return {}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_a_stock_data_fetch.py -v`
Expected: PASS (with mock)

**Step 5: Commit**

```bash
git add src/value_investment/pipeline/handlers/a_stock.py
git commit -m "feat: implement AStockHandler data fetching"
```

---

### Task 9: 实现 Pipeline API

**Files:**
- Modify: `src/value_investment/pipeline/api.py`
- Test: `tests/pipeline/test_api.py`

**Step 1: Write the failing test**

```python
from value_investment.pipeline.api import PipelineAPI

async def test_pipeline_api_get_roic():
    api = PipelineAPI()
    
    # Mock 数据
    with patch.object(api.container.bus, 'process', new_callable=AsyncMock) as mock_process:
        mock_msg = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=10,
            require={"ebit", "total_assets", "cash", "current_liabilities"},
        )
        mock_msg.add_result("ebit", {2024: 100.0})
        mock_msg.add_result("total_assets", {2024: 1000.0})
        mock_msg.add_result("cash", {2024: 200.0})
        mock_msg.add_result("current_liabilities", {2024: 300.0})
        mock_process.return_value = mock_msg
        
        result = await api.get_indicator("600519", "roic", end="2024", years=10)
        
        assert 2024 in result
        assert abs(result[2024] - 0.2) < 0.001
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_api.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

```python
# src/value_investment/pipeline/api.py
"""Pipeline API"""
from typing import Any

from value_investment.pipeline.bus.message import Message
from value_investment.pipeline.container import Container

class PipelineAPI:
    """High-level API for financial data pipeline"""
    
    def __init__(self):
        self.container = Container()
    
    async def get_indicator(
        self,
        symbol: str,
        indicator: str,
        end: str = "2024",
        years: int = 10,
        market: str | None = None,
    ) -> dict[int, float]:
        """Get financial indicator
        
        Args:
            symbol: Stock code
            indicator: Indicator name (e.g., "roic", "roe")
            end: End year
            years: Number of years
            market: Market (auto-detected if None)
            
        Returns:
            {year: indicator_value}
        """
        # 自动检测市场
        if market is None:
            market = self._detect_market(symbol)
        
        # 获取计算器
        calculator = self._get_calculator(indicator)
        
        # 创建消息
        message = Message(
            symbol=symbol,
            market=market,
            end=end,
            years=years,
            require=calculator.required_fields.copy(),
        )
        
        # 通过消息总线获取数据
        await self.container.bus.process(message)
        
        # 检查是否所有字段都获取到了
        if message.require:
            missing = message.require
            raise ValueError(f"Missing fields: {missing}")
        
        # 计算指标
        return calculator.calculate(message.results)
    
    def _detect_market(self, symbol: str) -> str:
        """Detect market from symbol"""
        if symbol.startswith(("0", "3")):
            return "A股"
        elif symbol.startswith("6"):
            return "A股"
        elif len(symbol) == 5:
            return "港股"
        else:
            return "美股"
    
    def _get_calculator(self, name: str):
        """Get calculator by name"""
        from value_investment.pipeline.calculators.roic import ROICCalculator
        
        calculators = {
            "roic": ROICCalculator,
        }
        
        if name not in calculators:
            raise ValueError(f"Unknown indicator: {name}")
        
        return calculators[name]()
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_api.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/pipeline/api.py tests/pipeline/test_api.py
git commit -m "feat: implement Pipeline API"
```

---

## 阶段 3: 集成测试

### Task 10: 端到端测试（完整流程）

**Files:**
- Test: `tests/pipeline/test_e2e_roic.py`

**Step 1: Write the failing test**

```python
@pytest.mark.asyncio
async def test_e2e_roic_full_flow():
    """端到端测试：获取贵州茅台 ROIC"""
    api = PipelineAPI()
    
    # 这个测试会真正调用数据源
    result = await api.get_indicator(
        symbol="600519",
        indicator="roic",
        end="2024",
        years=10,
    )
    
    assert isinstance(result, dict)
    assert len(result) > 0
    assert 2024 in result
    # ROIC 应该在合理范围内
    for year, value in result.items():
        assert 0 <= value <= 1  # 0% - 100%
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_e2e_roic.py -v`
Expected: FAIL (因为数据获取还没实现)

**Step 3: 实现真实数据获取逻辑**

完善 AStockHandler.fetch_from_source 方法，复用现有的数据获取逻辑。

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_e2e_roic.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/pipeline/test_e2e_roic.py
git commit -m "test: add E2E test for ROIC"
```

---

## 任务清单汇总

| Task | 描述 |
|-----|------|
| 1 | 创建 pipeline 目录结构 |
| 2 | 实现 Message 类 |
| 3 | 实现 Handler 基类 |
| 4 | 实现 MessageBus |
| 5 | 实现 ROIC Calculator |
| 6 | 实现 A股 Handler |
| 7 | 实现 DI Container |
| 8 | 实现数据获取 |
| 9 | 实现 Pipeline API |
| 10 | E2E 端到端测试 |
