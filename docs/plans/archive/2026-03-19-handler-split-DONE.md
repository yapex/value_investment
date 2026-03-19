# Handler 拆分重构实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将单一 AStockHandler 拆分为 9 个 Handler（3 市场 × 3 数据类型），实现快速拒绝模式，提升 Handler 职责分离和可测试性。

**Architecture:** 按市场+数据类型拆分为 9 个 Handler，每个 Handler 专注单一职责：
- StatementHandler - 财务三表
- IndicatorHandler - 财务指标
- MarketHandler - 市值/PE/PB

每个 Handler 实现快速拒绝：
```python
def handle(self, message):
    if message.market != self.target_market:
        return
    if not (message.require & self.supported_fields):
        return
    # 真正处理...
```

**Tech Stack:** Python, pytest, asyncio

---

## 测试指南

**TDD Cycle:**
1. Write failing test
2. Run: `pytest tests/pipeline/ -v` → should FAIL
3. Implement
4. Run: `pytest tests/pipeline/ -v` → should PASS
5. Commit

**Testing Commands:**
- All tests: `pytest tests/pipeline/ -v`
- Single test: `pytest tests/pipeline/test_handler_split.py -v`
- Lint: `ruff check src/value_investment/pipeline/`

---

## Task 1: 创建 Handler 基类

**Files:**
- Create: `src/value_investment/pipeline/handlers/base_handler.py`
- Test: `tests/pipeline/test_base_handler.py`

**Step 1: Write failing test**

```python
# tests/pipeline/test_base_handler.py
import pytest
from value_investment.pipeline.handlers.base_handler import BaseHandler

class MockProvider:
    @property
    def supported_fields(self):
        return {"field_a", "field_b"}

class ConcreteHandler(BaseHandler):
    def __init__(self, provider=None):
        super().__init__(provider, "A股", {"field_a", "field_b", "field_c"})
    
    async def _fetch_data(self, message):
        return {}

class TestBaseHandler:
    def test_init(self):
        handler = ConcreteHandler(MockProvider())
        assert handler.target_market == "A股"
        assert handler.can_handle == {"field_a", "field_b"}

    def test_fast_reject_wrong_market(self):
        from value_investment.pipeline.bus.message import Message
        handler = ConcreteHandler(MockProvider())
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"field_a"})
        
        # 市场不匹配，应该能快速判断
        can_handle = handler._can_handle_market(message)
        assert can_handle == False

    def test_fast_reject_no_fields(self):
        from value_investment.pipeline.bus.message import Message
        handler = ConcreteHandler(MockProvider())
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"other_field"})
        
        can_handle = handler._can_handle_fields(message)
        assert can_handle == False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_base_handler.py -v`
Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

```python
# src/value_investment/pipeline/handlers/base_handler.py
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from value_investment.pipeline.bus.message import Message

class BaseHandler(ABC):
    """Handler 基类，实现快速拒绝模式"""
    
    def __init__(
        self,
        provider,
        target_market: str,
        supported_fields: set[str]
    ):
        self._provider = provider
        self.target_market = target_market
        self._supported_fields = supported_fields
    
    @property
    def can_handle(self) -> set[str]:
        """该 Handler 能处理的字段集合"""
        return self._supported_fields & (self._provider.supported_fields if self._provider else set())
    
    def _can_handle_market(self, message: "Message") -> bool:
        """快速判断：是否处理该市场"""
        return message.market == self.target_market
    
    def _can_handle_fields(self, message: "Message") -> bool:
        """快速判断：是否有可处理的字段"""
        return bool(message.require & self.can_handle)
    
    async def handle(self, message: "Message") -> None:
        """处理消息（模板方法）"""
        # 快速拒绝
        if not self._can_handle_market(message):
            return
        if not self._can_handle_fields(message):
            return
        
        # 交给子类处理
        await self._handle_impl(message)
    
    @abstractmethod
    async def _handle_impl(self, message: "Message") -> None:
        """子类实现具体处理逻辑"""
        pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_base_handler.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/pipeline/test_base_handler.py src/value_investment/pipeline/handlers/base_handler.py
git commit -m "feat: add BaseHandler with fast-reject pattern"
```

---

## Task 2: 创建 A 股 StatementHandler

**Files:**
- Create: `src/value_investment/pipeline/handlers/a_statement.py`
- Test: `tests/pipeline/test_a_statement.py`

**Step 1: Write failing test**

```python
# tests/pipeline/test_a_statement.py
import pytest
from unittest.mock import MagicMock, AsyncMock
from value_investment.pipeline.handlers.a_statement import AStockStatementHandler
from value_investment.pipeline.bus.message import Message

class TestAStockStatementHandler:
    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.supported_fields = {"total_revenue", "net_profit", "total_assets"}
        provider.fetch_financial_data = AsyncMock(return_value={
            "total_revenue": {2024: 100e9, 2023: 90e9}
        })
        return provider
    
    def test_market_filter(self, mock_provider):
        """快速拒绝：港股请求应该被忽略"""
        handler = AStockStatementHandler(mock_provider)
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"total_revenue"})
        
        # 市场不匹配，不处理
        assert handler._can_handle_market(message) == False
    
    def test_fields_filter(self, mock_provider):
        """快速拒绝：无支持字段应该被忽略"""
        handler = AStockStatementHandler(mock_provider)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"market_cap"})
        
        # 没有可处理的字段
        assert handler._can_handle_fields(message) == False
    
    @pytest.mark.asyncio
    async def test_fetch_financial_data(self, mock_provider):
        """正常流程：获取财务报表数据"""
        handler = AStockStatementHandler(mock_provider)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"total_revenue"})
        
        await handler.handle(message)
        
        # 应该调用 provider
        mock_provider.fetch_financial_data.assert_called_once()
        assert "total_revenue" not in message.require
        assert 2024 in message.results.get("total_revenue", {})
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_a_statement.py -v`
Expected: FAIL (module not found)

**Step 3: Write minimal implementation**

```python
# src/value_investment/pipeline/handlers/a_statement.py
from typing import TYPE_CHECKING, Any

from value_investment.pipeline.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.pipeline.bus.message import Message

# A 股财务报表字段
A_STOCK_STATEMENT_FIELDS = {
    # 资产负债表
    "total_assets", "total_liabilities", "total_equity",
    "current_assets", "current_liabilities",
    "cash_and_equivalents", "inventory",
    "accounts_receivable", "accounts_payable",
    "fixed_assets", "prepayment",
    "contract_assets", "contract_liab", "adv_receipts",
    # 利润表
    "total_revenue", "net_profit", "operating_profit",
    "gross_profit", "operating_cost",
    # 现金流量表
    "operating_cash_flow", "investing_cash_flow",
    "financing_cash_flow", "capital_expenditure",
}

class AStockStatementHandler(BaseHandler):
    """A 股财务三表 Handler"""
    
    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_STOCK_STATEMENT_FIELDS)
    
    async def _handle_impl(self, message: "Message") -> None:
        """处理 A 股财务报表请求"""
        if not self._provider:
            return
        
        # 获取需要处理的字段
        to_handle = message.require & self.can_handle
        if not to_handle:
            return
        
        # 调用 provider 获取数据
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

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_a_statement.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/pipeline/test_a_statement.py src/value_investment/pipeline/handlers/a_statement.py
git commit -m "feat: add AStockStatementHandler"
```

---

## Task 3: 创建 A 股 IndicatorHandler

**Files:**
- Create: `src/value_investment/pipeline/handlers/a_indicator.py`
- Test: `tests/pipeline/test_a_indicator.py`

**Step 1: Write failing test**

```python
# tests/pipeline/test_a_indicator.py
import pytest
from unittest.mock import MagicMock, AsyncMock
from value_investment.pipeline.handlers.a_indicator import AStockIndicatorHandler
from value_investment.pipeline.bus.message import Message

class TestAStockIndicatorHandler:
    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.supported_fields = {"roe", "roa", "gross_margin"}
        provider.fetch_indicators = AsyncMock(return_value={
            "roe": {2024: 25.5, 2023: 24.8}
        })
        return provider
    
    def test_market_filter(self, mock_provider):
        """快速拒绝：港股请求应该被忽略"""
        handler = AStockIndicatorHandler(mock_provider)
        message = Message(symbol="00700", market="港股", end="2024", years=5, require={"roe"})
        
        assert handler._can_handle_market(message) == False
    
    @pytest.mark.asyncio
    async def test_fetch_indicators(self, mock_provider):
        """正常流程：获取财务指标"""
        handler = AStockIndicatorHandler(mock_provider)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"roe", "roa"})
        
        await handler.handle(message)
        
        mock_provider.fetch_indicators.assert_called_once()
        assert "roe" not in message.require
        assert 2024 in message.results.get("roe", {})
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_a_indicator.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# src/value_investment/pipeline/handlers/a_indicator.py
from typing import TYPE_CHECKING

from value_investment.pipeline.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.pipeline.bus.message import Message

# A 股财务指标字段 (来自 fina_indicator API)
A_STOCK_INDICATOR_FIELDS = {
    "roe", "roa", "roic",
    "gross_margin", "net_profit_margin",
    "current_ratio", "quick_ratio", "cash_ratio",
    "debt_ratio", "equity_multiplier",
    "asset_turnover", "inventory_turnover", "receivable_turnover",
    "basic_eps", "diluted_eps", "book_value_per_share",
}

class AStockIndicatorHandler(BaseHandler):
    """A 股财务指标 Handler"""
    
    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_STOCK_INDICATOR_FIELDS)
    
    async def _handle_impl(self, message: "Message") -> None:
        """处理 A 股财务指标请求"""
        if not self._provider:
            return
        
        to_handle = message.require & self.can_handle
        if not to_handle:
            return
        
        data = self._provider.fetch_indicators(
            stock_code=message.symbol,
            fields=to_handle,
            end_year=int(message.end[:4]),
            years=message.years,
        )
        
        for field, values in data.items():
            if values:
                message.add_result(field, values)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_a_indicator.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/pipeline/test_a_indicator.py src/value_investment/pipeline/handlers/a_indicator.py
git commit -m "feat: add AStockIndicatorHandler"
```

---

## Task 4: 创建 A 股 MarketHandler

**Files:**
- Create: `src/value_investment/pipeline/handlers/a_market.py`
- Test: `tests/pipeline/test_a_market.py`

**Step 1: Write failing test**

```python
# tests/pipeline/test_a_market.py
import pytest
from unittest.mock import MagicMock, AsyncMock
from value_investment.pipeline.handlers.a_market import AStockMarketHandler
from value_investment.pipeline.bus.message import Message

class TestAStockMarketHandler:
    @pytest.fixture
    def mock_provider(self):
        provider = MagicMock()
        provider.supported_fields = {"market_cap", "pe_ratio", "pb_ratio"}
        provider.fetch_market_data = AsyncMock(return_value={
            "market_cap": 2.5e12,
            "pe_ratio": 28.5,
        })
        return provider
    
    @pytest.mark.asyncio
    async def test_fetch_market_data(self, mock_provider):
        """正常流程：获取市值数据"""
        handler = AStockMarketHandler(mock_provider)
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"market_cap", "pe_ratio"})
        
        await handler.handle(message)
        
        mock_provider.fetch_market_data.assert_called_once()
        assert "market_cap" not in message.require
        # 市场数据是单时间点，使用 end 年份
        assert 2024 in message.results.get("market_cap", {})
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_a_market.py -v`
Expected: FAIL

**Step 3: Write implementation**

```python
# src/value_investment/pipeline/handlers/a_market.py
from typing import TYPE_CHECKING

from value_investment.pipeline.handlers.base_handler import BaseHandler

if TYPE_CHECKING:
    from value_investment.pipeline.bus.message import Message

# A 股市场数据字段 (来自 daily_basic API)
A_STOCK_MARKET_FIELDS = {
    "market_cap", "pe_ratio", "pb_ratio",
    "total_shares", "circ_market_cap", "circ_shares",
}

class AStockMarketHandler(BaseHandler):
    """A 股市值数据 Handler"""
    
    def __init__(self, provider=None):
        super().__init__(provider, "A股", A_STOCK_MARKET_FIELDS)
    
    async def _handle_impl(self, message: "Message") -> None:
        """处理 A 股市值数据请求"""
        if not self._provider:
            return
        
        to_handle = message.require & self.can_handle
        if not to_handle:
            return
        
        data = self._provider.fetch_market_data(
            stock_code=message.symbol,
            fields=to_handle,
        )
        
        # 市场数据是单时间点，转换为 {year: value} 格式
        end_year = int(message.end[:4])
        for field, value in data.items():
            if value is not None:
                message.add_result(field, {end_year: value})
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/pipeline/test_a_market.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add tests/pipeline/test_a_market.py src/value_investment/pipeline/handlers/a_market.py
git commit -m "feat: add AStockMarketHandler"
```

---

## Task 5: 创建港股和美股 Handler (模板化)

**Files:**
- Create: `src/value_investment/pipeline/handlers/hk_statement.py`
- Create: `src/value_investment/pipeline/handlers/hk_indicator.py`
- Create: `src/value_investment/pipeline/handlers/hk_market.py`
- Create: `src/value_investment/pipeline/handlers/us_statement.py`
- Create: `src/value_investment/pipeline/handlers/us_indicator.py`
- Create: `src/value_investment/pipeline/handlers/us_market.py`
- Test: `tests/pipeline/test_hk_handlers.py`, `tests/pipeline/test_us_handlers.py`

由于港股和美股的实现与 A 股类似，使用相同的模式创建：

**Step 1: 创建 HK handlers (模板复制修改)**

```python
# src/value_investment/pipeline/handlers/hk_statement.py
from value_investment.pipeline.handlers.a_statement import AStockStatementHandler

class HKStockStatementHandler(AStockStatementHandler):
    def __init__(self, provider=None):
        # 使用港股字段，target_market 改为"港股"
        from value_investment.pipeline.handlers.a_statement import A_STOCK_STATEMENT_FIELDS
        super().__init__(provider)
        self.target_market = "港股"
```

类似创建 hk_indicator.py, hk_market.py, us_statement.py, us_indicator.py, us_market.py

**Step 2: Write basic tests for HK/US handlers**

```python
# tests/pipeline/test_hk_handlers.py
import pytest
from value_investment.pipeline.handlers.hk_statement import HKStockStatementHandler
from value_investment.pipeline.handlers.hk_indicator import HKStockIndicatorHandler
from value_investment.pipeline.handlers.hk_market import HKStockMarketHandler
from value_investment.pipeline.bus.message import Message

class TestHKHandlers:
    def test_statement_rejects_a_stock(self):
        handler = HKStockStatementHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"total_revenue"})
        assert handler._can_handle_market(message) == False
    
    def test_indicator_rejects_a_stock(self):
        handler = HKStockIndicatorHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"roe"})
        assert handler._can_handle_market(message) == False
    
    def test_market_rejects_a_stock(self):
        handler = HKStockMarketHandler()
        message = Message(symbol="600519", market="A股", end="2024", years=5, require={"market_cap"})
        assert handler._can_handle_market(message) == False
```

**Step 3: Run tests**

Run: `pytest tests/pipeline/test_hk_handlers.py tests/pipeline/test_us_handlers.py -v`

**Step 4: Commit**

```bash
git add src/value_investment/pipeline/handlers/hk_*.py src/value_investment/pipeline/handlers/us_*.py
git add tests/pipeline/test_hk_handlers.py tests/pipeline/test_us_handlers.py
git commit -m "feat: add HK and US handlers"
```

---

## Task 6: 更新 Container 注册 Handler

**Files:**
- Modify: `src/value_investment/pipeline/container.py`

**Step 1: Write failing test**

```python
# tests/pipeline/test_container_split.py
def test_container_registers_9_handlers():
    container = Container.create()
    # Container 应该注册 9 个 Handler
    handlers = [h for h in container.bus().handlers]
    handler_names = [type(h).__name__ for h in handlers]
    
    expected = [
        "AStockStatementHandler", "AStockIndicatorHandler", "AStockMarketHandler",
        "HKStockStatementHandler", "HKStockIndicatorHandler", "HKStockMarketHandler",
        "USStockStatementHandler", "USStockIndicatorHandler", "USStockMarketHandler",
    ]
    assert set(handler_names) == set(expected)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/pipeline/test_container_split.py -v`
Expected: FAIL

**Step 3: Update container**

```python
# src/value_investment/pipeline/container.py
from value_investment.pipeline.handlers.a_statement import AStockStatementHandler
from value_investment.pipeline.handlers.a_indicator import AStockIndicatorHandler
from value_investment.pipeline.handlers.a_market import AStockMarketHandler
from value_investment.pipeline.handlers.hk_statement import HKStockStatementHandler
from value_investment.pipeline.handlers.hk_indicator import HKStockIndicatorHandler
from value_investment.pipeline.handlers.hk_market import HKStockMarketHandler
from value_investment.pipeline.handlers.us_statement import USStockStatementHandler
from value_investment.pipeline.handlers.us_indicator import USStockIndicatorHandler
from value_investment.pipeline.handlers.us_market import USStockMarketHandler

# 在 create() 方法中注册所有 Handler
container.bus().register(AStockStatementHandler(container.tushare_provider()))
container.bus().register(AStockIndicatorHandler(container.tushare_provider()))
container.bus().register(AStockMarketHandler(container.tushare_provider()))
# HK handlers...
# US handlers...
```

**Step 4: Run tests**

Run: `pytest tests/pipeline/ -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/pipeline/container.py
git commit -m "feat: register 9 handlers in container"
```

---

## Task 7: 删除旧 Handler (可选)

**Files:**
- Delete: `src/value_investment/pipeline/handlers/a_stock.py` (旧 AStockHandler)
- Delete: `src/value_investment/pipeline/handlers/hk_stock.py`
- Delete: `src/value_investment/pipeline/handlers/us_stock.py`

**Step 1: 删除并运行测试确保无影响**

```bash
git rm src/value_investment/pipeline/handlers/a_stock.py
git rm src/value_investment/pipeline/handlers/hk_stock.py
git rm src/value_investment/pipeline/handlers/us_stock.py
pytest tests/pipeline/ -v
git commit -m "refactor: remove old handlers"
```

---

## Task 8: 端到端集成测试

**Files:**
- Create: `tests/pipeline/test_e2e_handler_split.py`

**Step 1: Write integration test**

```python
# tests/pipeline/test_e2e_handler_split.py
import pytest
from value_investment.pipeline.api import PipelineAPI

class TestE2EHandlerSplit:
    @pytest.mark.asyncio
    async def test_a_stock_fields_routed_correctly(self):
        """A股字段只被 A 股 Handler 处理"""
        api = PipelineAPI()
        # 应该能获取 A 股的 roe (indicator) 和 total_revenue (statement)
        # 使用 mock 验证路由正确
        ...
```

**Step 2: Run and commit**

Run: `pytest tests/pipeline/test_e2e_handler_split.py -v`

---

## 执行方式

**Plan complete and saved to `docs/plans/2026-03-19-handler-split.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
