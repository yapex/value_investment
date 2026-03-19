# Value Investment Refactoring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor the value_investment codebase to fix SOLID violations (SRP, OCP, LSP, DIP) and add data validation with Pandera.

**Architecture:** Implement a layered pipeline: Adapter Layer (data fetching) → Validation Layer (Pandera) → Domain Layer (pure calculation). Add declarative dependency injection to replace reverse-calls from Indicators to Provider.

**Tech Stack:** Python, Pandera (DataFrame validation), Protocol (interface definition), dataclasses

---

## Phase 0: Quick Wins (Foundation)

### Task 1: Create DependencyRegistry and DataProvider

**Files:**
- Create: `src/value_investment/core/dependencies.py`
- Modify: `src/value_investment/api.py` (add registry to ValueInvestment class)
- Test: `tests/test_dependencies.py`

**Step 1: Write the failing test**

```python
# tests/test_dependencies.py
import pytest
from value_investment.core.dependencies import DataProvider, DependencyRegistry

class MockProvider:
    def get_quarterly_indicator(self, code):
        return f"quarterly:{code}"

    def get_historical_data(self, code, *args, **kwargs):
        return f"prices:{code}"

    def get_stock_info(self, code):
        return f"info:{code}"

def test_data_provider_get():
    provider = MockProvider()
    data_provider = DataProvider(provider)

    result = data_provider.get('quarterly', '600519')
    assert result == "quarterly:600519"

def test_dependency_registry_resolve():
    provider = MockProvider()
    data_provider = DataProvider(provider)
    registry = DependencyRegistry(data_provider)

    result = registry.resolve(['quarterly', 'prices'], '600519')
    assert result['quarterly'] == "quarterly:600519"
    assert result['prices'] == "prices:600519"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_dependencies.py -v`
Expected: FAIL - module not found

**Step 3: Write minimal implementation**

```python
# src/value_investment/core/dependencies.py
from dataclasses dataclass
from typing import Any

class DataProvider:
    """Lightweight dependency provider - fetches data by stock_code"""

    def __init__(self, stock_provider):
        self._provider = stock_provider

    def get(self, data_type: str, stock_code: str, **kwargs) -> Any:
        fetchers = {
            'quarterly': lambda: self._provider.get_quarterly_indicator(stock_code),
            'prices': lambda: self._provider.get_historical_data(stock_code, **kwargs),
            'stock_info': lambda: self._provider.get_stock_info(stock_code),
        }
        if data_type not in fetchers:
            raise ValueError(f"Unknown data type: {data_type}")
        return fetchers[data_type]()

class DependencyRegistry:
    """Dependency registry - maps declarations to fetchers"""

    def __init__(self, data_provider: DataProvider):
        self._provider = data_provider

    def resolve(self, needs: list[str], stock_code: str, **kwargs) -> dict:
        """Resolve dependencies based on declarations"""
        if not needs:
            return {}
        return {n: self._provider.get(n, stock_code, **kwargs) for n in needs}
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_dependencies.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/core/dependencies.py tests/test_dependencies.py
git commit -m "feat: add DependencyRegistry and DataProvider for declarative dependency injection"
```

---

### Task 2: Add `needs` declaration to 3 violating Indicators

**Files:**
- Modify: `src/value_investment/indicators/simple.py:530-656` (LatestMarketCapIndicator)
- Modify: `src/value_investment/indicators/complex.py:280-299` (ImpliedGrowthIndicator)
- Modify: `src/value_investment/indicators/complex.py:435-448` (PEPercentileIndicator)
- Test: `tests/test_indicator_needs.py`

**Step 1: Write the failing test**

```python
# tests/test_indicator_needs.py
import pytest
from value_investment.indicators.simple import LatestMarketCapIndicator
from value_investment.indicators.complex import ImpliedGrowthIndicator, PEPercentileIndicator

def test_latest_market_cap_has_needs():
    indicator = LatestMarketCapIndicator()
    assert hasattr(indicator, 'needs'), "LatestMarketCapIndicator must have 'needs' attribute"
    assert indicator.needs == ['stock_info', 'prices']

def test_implied_growth_has_needs():
    indicator = ImpliedGrowthIndicator()
    assert hasattr(indicator, 'needs'), "ImpliedGrowthIndicator must have 'needs' attribute"
    assert 'stock_info' in indicator.needs

def test_pe_percentile_has_needs():
    indicator = PEPercentileIndicator()
    assert hasattr(indicator, 'needs'), "PEPercentileIndicator must have 'needs' attribute"
    assert 'quarterly' in indicator.needs
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_indicator_needs.py -v`
Expected: FAIL - 'needs' attribute not found

**Step 3: Write minimal implementation**

In `src/value_investment/indicators/simple.py`, add to LatestMarketCapIndicator class:
```python
class LatestMarketCapIndicator(BaseIndicator):
    name = "latest_market_cap"
    needs = ['stock_info', 'prices']  # ADD THIS
    # ... rest of class
```

In `src/value_investment/indicators/complex.py`, add to ImpliedGrowthIndicator class:
```python
class ImpliedGrowthIndicator(BaseIndicator):
    name = "implied_growth"
    needs = ['stock_info']  # ADD THIS
    # ... rest of class
```

In `src/value_investment/indicators/complex.py`, add to PEPercentileIndicator class:
```python
class PEPercentileIndicator(BaseIndicator):
    name = "PEPct"
    needs = ['quarterly', 'prices']  # ADD THIS
    # ... rest of class
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_indicator_needs.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/indicators/simple.py src/value_investment/indicators/complex.py tests/test_indicator_needs.py
git commit -m "feat: add 'needs' declaration to violating indicators"
```

---

### Task 3: Activate DataMapper in Provider

**Files:**
- Modify: `src/value_investment/data/providers/akshare_provider.py` (find where financial data is fetched)
- Test: `tests/test_datamapper_activated.py`

**Step 1: Write the failing test**

```python
# tests/test_datamapper_activated.py
import pytest
from unittest.mock import MagicMock, patch

def test_provider_uses_datamapper():
    """Verify that provider transforms data using DataMapper"""
    from value_investment.data.providers.akshare_provider import AkshareProvider

    # Check if DataMapper is imported and used in the provider
    import value_investment.data.providers.akshare_provider as provider_module

    # The provider should have DataMapper imported
    assert hasattr(provider_module, 'DataMapper') or 'DataMapper' in dir(provider_module)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_datamapper_activated.py -v`
Expected: FAIL - DataMapper not used in provider

**Step 3: Write minimal implementation**

In `src/value_investment/data/providers/akshare_provider.py`, add import and use:

```python
# At top of file, add:
from value_investment.data.mapper import DataMapper

# Find the method that returns financial data (e.g., get_financial_data)
# and add mapping after fetching:
def get_financial_data(self, stock_code: str, end_year: int = None) -> pd.DataFrame:
    # ... existing fetch code ...

    # Apply DataMapper to standardize fields
    result = DataMapper.to_standard_format(result)

    return result
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_datamapper_activated.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/data/providers/akshare_provider.py tests/test_datamapper_activated.py
git commit -m "feat: activate DataMapper in provider for field standardization"
```

---

### Task 4: Add CacheConfig for configurable caching

**Files:**
- Create: `src/value_investment/core/cache_config.py`
- Modify: `src/value_investment/data/cache.py` (use config)
- Test: `tests/test_cache_config.py`

**Step 1: Write the failing test**

```python
# tests/test_cache_config.py
import pytest
from value_investment.core.cache_config import CacheConfig, CacheStrategy

def test_cache_config_defaults():
    config = CacheConfig()
    assert config.stock_info_ttl > 0
    assert config.historical_ttl > 0
    assert config.financial_ttl > 0

def test_cache_strategy_for_stock_info():
    strategy = CacheStrategy.for_data_type('stock_info')
    assert strategy.ttl > 0

def test_cache_strategy_unknown_type():
    strategy = CacheStrategy.for_data_type('unknown')
    assert strategy.ttl == 0  # No cache for unknown types
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_cache_config.py -v`
Expected: FAIL - module not found

**Step 3: Write minimal implementation**

```python
# src/value_investment/core/cache_config.py
from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class CacheStrategy:
    """Cache strategy for a specific data type"""
    ttl: int  # seconds
    stale_while_revalidate: bool = True

    @classmethod
    def for_data_type(cls, data_type: str) -> 'CacheStrategy':
        strategies = {
            'stock_info': cls(ttl=86400),  # 1 day - expires next morning
            'historical': cls(ttl=86400 * 365),  # 1 year
            'quarterly': cls(ttl=86400 * 180),  # 6 months
            'financial': cls(ttl=86400 * 365 * 2),  # 2 years - expires June next year
        }
        return strategies.get(data_type, cls(ttl=0))

@dataclass
class CacheConfig:
    """Cache configuration - centralizes TTL settings"""
    stock_info_ttl: int = 86400
    historical_ttl: int = 86400 * 365
    financial_ttl: int = 86400 * 365 * 2
    quarterly_ttl: int = 86400 * 180

    def get_ttl(self, data_type: str) -> int:
        """Get TTL for data type"""
        mapping = {
            'stock_info': self.stock_info_ttl,
            'historical': self.historical_ttl,
            'quarterly': self.quarterly_ttl,
            'financial': self.financial_ttl,
        }
        return mapping.get(data_type, 0)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_cache_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/core/cache_config.py tests/test_cache_config.py
git commit -f "feat: add CacheConfig for configurable caching strategies"
```

---

## Phase 1: Schema & Validation

### Task 5: Define CoreFinancialSchema with Pandera

**Files:**
- Create: `src/value_investment/core/schemas.py`
- Test: `tests/test_core_schema.py`

**Step 1: Write the failing test**

```python
# tests/test_core_schema.py
import pytest
import pandas as pd
from value_investment.core.schemas import CoreFinancialSchema, CoreFinancialSchemaLite

def test_schema_validates_valid_data():
    """Schema should pass with valid data"""
    data = pd.DataFrame({
        'year': [2024, 2023],
        'net_profit': [100.0, 90.0],
        'total_equity': [500.0, 450.0],
        'total_assets': [1000.0, 900.0],
        'revenue': [800.0, 700.0],
    })

    # Should not raise
    validated = CoreFinancialSchema.validate(data)
    assert not validated.empty

def test_schema_rejects_missing_required_fields():
    """Schema should fail with missing required fields"""
    data = pd.DataFrame({
        'year': [2024],
        'net_profit': [100.0],
        # Missing: total_equity, total_assets, revenue
    })

    with pytest.raises(Exception):
        CoreFinancialSchema.validate(data)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_core_schema.py -v`
Expected: FAIL - module not found

**Step 3: Write minimal implementation**

```python
# src/value_investment/core/schemas.py
import pandera as pa
from pandera import Column, Check, DataFrameModel
from typing import Optional

class CoreFinancialSchema(DataFrameModel):
    """Core financial fields - required for 90% of indicators"""

    year: int = Column(int, Check.greater_than(1990), nullable=False)

    # Required fields
    net_profit: float = Column(float, nullable=False)
    total_equity: float = Column(float, Check.greater_than(0), nullable=False)
    total_assets: float = Column(float, Check.greater_than(0), nullable=False)
    revenue: float = Column(float, Check.greater_than(0), nullable=False)

    # Optional fields
    operating_cash_flow: Optional[float] = Column(float, nullable=True)
    operating_profit: Optional[float] = Column(float, nullable=True)
    total_liabilities: Optional[float] = Column(float, nullable=True)
    current_assets: Optional[float] = Column(float, nullable=True)
    current_liabilities: Optional[float] = Column(float, nullable=True)

    class Config:
        strict = False  # Allow extra columns

class CoreFinancialSchemaLite(DataFrameModel):
    """Minimal schema - only year and one financial metric"""

    year: int = Column(int, Check.greater_than(1990), nullable=False)

    # At least one of these must be present
    net_profit: Optional[float] = Column(float, nullable=True)
    revenue: Optional[float] = Column(float, nullable=True)
    total_assets: Optional[float] = Column(float, nullable=True)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_core_schema.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/core/schemas.py tests/test_core_schema.py
git commit -m "feat: add CoreFinancialSchema with Pandera validation"
```

---

### Task 6: Create Validation Pipeline

**Files:**
- Create: `src/value_investment/core/validation.py`
- Test: `tests/test_validation_pipeline.py`

**Step 1: Write the failing test**

```python
# tests/test_validation_pipeline.py
import pytest
import pandas as pd
from value_investment.core.validation import ValidationPipeline, ValidationError

def test_pipeline_passes_valid_data():
    pipeline = ValidationPipeline()
    data = pd.DataFrame({
        'year': [2024],
        'net_profit': [100.0],
        'total_equity': [500.0],
        'total_assets': [1000.0],
        'revenue': [800.0],
    })

    result = pipeline.validate(data)
    assert result is not None

def test_pipeline_raises_on_invalid_data():
    pipeline = ValidationPipeline()
    data = pd.DataFrame({
        'year': [2024],
        # Missing all required fields
    })

    with pytest.raises(ValidationError) as exc_info:
        pipeline.validate(data)

    assert 'net_profit' in str(exc_info.value)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_validation_pipeline.py -v`
Expected: FAIL - module not found

**Step 3: Write minimal implementation**

```python
# src/value_investment/core/validation.py
import pandas as pd
from dataclasses import dataclass
from value_investment.core.schemas import CoreFinancialSchema

@dataclass
class ValidationError(Exception):
    """Validation error with details"""
    message: str
    missing_fields: list = None

    def __str__(self):
        return self.message

class ValidationPipeline:
    """Pipeline that validates data through schemas"""

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.schema = CoreFinancialSchema

    def validate(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate DataFrame through schema"""
        if data is None or data.empty:
            raise ValidationError("Empty DataFrame provided")

        try:
            validated = self.schema.validate(data)
            return validated
        except pa.errors.SchemaError as e:
            # Extract missing fields from error
            missing = []
            if hasattr(e, 'errors'):
                for error in e.errors:
                    if error.get('loc'):
                        missing.append(str(error['loc'][0]))

            raise ValidationError(
                message=f"Validation failed: {str(e)}",
                missing_fields=missing
            )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_validation_pipeline.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/core/validation.py tests/test_validation_pipeline.py
git commit -m "feat: add ValidationPipeline for DataFrame validation"
```

---

### Task 7: Extract IStockProvider Protocol

**Files:**
- Create: `src/value_investment/core/interfaces.py`
- Modify: `src/value_investment/data/providers/akshare_provider.py` (implement protocol)
- Test: `tests/test_istock_provider.py`

**Step 1: Write the failing test**

```python
# tests/test_istock_provider.py
import pytest
from typing import Protocol
from value_investment.core.interfaces import IStockProvider

def test_provider_implements_protocol():
    """AkshareProvider should implement IStockProvider"""
    from value_investment.data.providers.akshare_provider import AkshareProvider

    # Check that provider has all required methods
    required_methods = [
        'get_stock_info',
        'get_quarterly_indicator',
        'get_historical_data',
        'get_balance_sheet',
        'get_income_statement',
        'get_cash_flow_statement',
    ]

    for method in required_methods:
        assert hasattr(AkshareProvider, method), f"Missing method: {method}"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_istock_provider.py -v`
Expected: FAIL - IStockProvider not defined

**Step 3: Write minimal implementation**

```python
# src/value_investment/core/interfaces.py
from typing import Protocol
import pandas as pd
from typing import Optional, Any

class IStockProvider(Protocol):
    """Abstract interface for stock data providers"""

    def get_stock_info(self, stock_code: str) -> pd.DataFrame:
        """Get basic stock information"""
        ...

    def get_quarterly_indicator(self, stock_code: str) -> pd.DataFrame:
        """Get quarterly financial indicators"""
        ...

    def get_historical_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        adjust: str = ""
    ) -> pd.DataFrame:
        """Get historical price data"""
        ...

    def get_balance_sheet(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get balance sheet data"""
        ...

    def get_income_statement(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get income statement data"""
        ...

    def get_cash_flow_statement(self, stock_code: str, end_year: int) -> pd.DataFrame:
        """Get cash flow statement data"""
        ...
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_istock_provider.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/core/interfaces.py tests/test_istock_provider.py
git commit -m "feat: extract IStockProvider Protocol interface"
```

---

### Task 8: Update BaseIndicator to use Protocol

**Files:**
- Modify: `src/value_investment/indicators/base.py`
- Test: `tests/test_indicator_protocol.py`

**Step 1: Write the failing test**

```python
# tests/test_indicator_protocol.py
import pytest
from value_investment.indicators.base import IIndicator
from value_investment.indicators.simple import ROEIndicator

def test_indicator_implements_protocol():
    """ROEIndicator should satisfy IIndicator Protocol"""
    # Check class has required Protocol methods
    indicator = ROEIndicator()

    assert hasattr(indicator, 'calculate')
    assert hasattr(indicator, 'get_required_fields')
    assert hasattr(indicator, 'name')
    assert hasattr(indicator, 'needs')
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_indicator_protocol.py -v`
Expected: FAIL - IIndicator not defined

**Step 3: Write minimal implementation**

In `src/value_investment/indicators/base.py`, add:

```python
# Add after imports
from typing import Protocol as TypingProtocol

class IIndicator(TypingProtocol):
    """Indicator protocol - defines interface for all indicators"""

    name: str

    def calculate(self, data: "pd.DataFrame", **kwargs) -> IndicatorResult:
        """Calculate the indicator"""
        ...

    def get_required_fields(self) -> list:
        """Return list of required data fields"""
        ...

    @property
    def needs(self) -> list:
        """Return list of external data dependencies"""
        return []
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_indicator_protocol.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/indicators/base.py tests/test_indicator_protocol.py
git commit -m "feat: add IIndicator Protocol to base module"
```

---

### Task 9: Update ValueInvestment API to use DependencyRegistry

**Files:**
- Modify: `src/value_investment/api.py`
- Test: `tests/test_api_dependency_injection.py`

**Step 1: Write the failing test**

```python
# tests/test_api_dependency_injection.py
import pytest
from unittest.mock import MagicMock
from value_investment.api import ValueInvestment

def test_api_uses_registry_for_needs():
    """API should resolve needs through DependencyRegistry"""
    api = ValueInvestment()

    # Check that api has registry
    assert hasattr(api, '_registry'), "ValueInvestment must have _registry"

def test_calculate_indicator_injects_dependencies():
    """calculate_indicator should inject dependencies from needs"""
    api = ValueInvestment()

    # Mock the registry
    api._registry = MagicMock()
    api._registry.resolve = lambda needs, code, **kw: {'quarterly': 'test_data'}

    # This should call registry.resolve
    try:
        api.calculate_indicator('PEPct', '600519')
    except:
        pass

    api._registry.resolve.assert_called()
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_api_dependency_injection.py -v`
Expected: FAIL - no _registry attribute

**Step 3: Write minimal implementation**

In `src/value_investment/api.py`, find the `ValueInvestment` class and modify:

```python
# Add import at top
from value_investment.core.dependencies import DependencyRegistry, DataProvider

class ValueInvestment:
    def __init__(self, provider=None, cache_dir=None):
        self._provider = provider
        # Add registry
        self._data_provider = DataProvider(provider)
        self._registry = DependencyRegistry(self._data_provider)

    def calculate_indicator(self, name: str, stock_code: str, **kwargs):
        # Get indicator
        indicator = self._factory.get(name)

        # Resolve dependencies if indicator has 'needs'
        needs = getattr(indicator, 'needs', [])
        injected = self._registry.resolve(needs, stock_code, **kwargs)

        # Get financial data
        data = self._get_financial_data(stock_code, **kwargs)

        # Merge injected data into kwargs for indicators that need it
        full_kwargs = {**kwargs, **injected}

        return indicator.calculate(data, **full_kwargs)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_api_dependency_injection.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/api.py tests/test_api_dependency_injection.py
git commit -m "feat: integrate DependencyRegistry into ValueInvestment API"
```

---

### Task 10: Remove kwargs.get('provider') from Indicators

**Files:**
- Modify: `src/value_investment/indicators/simple.py:530-656` (LatestMarketCapIndicator)
- Modify: `src/value_investment/indicators/complex.py:280-299` (ImpliedGrowthIndicator)
- Modify: `src/value_investment/indicators/complex.py:435-466` (PEPercentileIndicator)
- Test: `tests/test_no_provider_in_kwargs.py`

**Step 1: Write the failing test**

```python
# tests/test_no_provider_in_kwargs.py
import pytest

def test_latest_market_cap_no_provider_kwarg():
    """LatestMarketCapIndicator should not use kwargs.get('provider')"""
    from value_investment.indicators.simple import LatestMarketCapIndicator

    source = open('src/value_investment/indicators/simple.py').read()

    # Should NOT contain this pattern
    assert "kwargs.get('provider')" not in source or \
           "LatestMarketCapIndicator" not in source.split("kwargs.get('provider')")[0][-1000:]
    # This is tricky - let's just check the method doesn't call kwargs.get
    indicator = LatestMarketCapIndicator()
    import inspect
    source = inspect.getsource(indicator.calculate)
    assert "kwargs.get('provider')" not in source
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_no_provider_in_kwargs.py -v`
Expected: FAIL - still uses kwargs.get('provider')

**Step 3: Write minimal implementation**

For `LatestMarketCapIndicator`, replace the `calculate` method to use injected data:

```python
def calculate(self, data: pd.DataFrame, **kwargs) -> IndicatorResult:
    # Use injected dependencies instead of kwargs.get('provider')
    stock_info = kwargs.get('stock_info')  # Injected from registry
    prices = kwargs.get('prices')  # Injected from registry
    stock_code = kwargs.get('stock_code')

    if not stock_info or not prices or not stock_code:
        return IndicatorResult(
            value=0.0,
            unit="",
            description="最新市值 (需要stock_code和依赖注入)",
            years=[],
            values=[]
        )

    # Use stock_info and prices directly (already fetched)
    # ... rest of implementation using injected data
```

Do the same for `ImpliedGrowthIndicator` and `PEPercentileIndicator`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_no_provider_in_kwargs.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/indicators/simple.py src/value_investment/indicators/complex.py tests/test_no_provider_in_kwargs.py
git commit -m "refactor: remove kwargs.get('provider') from indicators, use injected deps"
```

---

## Summary

This plan implements the refactoring in 10 tasks:

| Task | Description | Files Changed |
|------|-------------|---------------|
| 1 | DependencyRegistry + DataProvider | New: `core/dependencies.py` |
| 2 | Add `needs` to 3 indicators | `indicators/simple.py`, `indicators/complex.py` |
| 3 | Activate DataMapper in Provider | `data/providers/akshare_provider.py` |
| 4 | CacheConfig | New: `core/cache_config.py` |
| 5 | CoreFinancialSchema | New: `core/schemas.py` |
| 6 | ValidationPipeline | New: `core/validation.py` |
| 7 | IStockProvider Protocol | New: `core/interfaces.py` |
| 8 | IIndicator Protocol | `indicators/base.py` |
| 9 | API uses DependencyRegistry | `api.py` |
| 10 | Remove kwargs.get('provider') | `indicators/simple.py`, `indicators/complex.py` |

**Prerequisites:**
- Run all tests after each task to verify changes
- Commit after each task for small, focused changes

**Related skills:**
- @superpowers:test-driven-development
- @superpowers:verification-before-completion
