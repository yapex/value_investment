# SOLID Principles Refactoring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor the codebase to comply with SOLID principles by splitting the monolithic `AkshareProvider` into market-specific providers, splitting the `IStockProvider` interface into smaller focused interfaces, and extracting duplicated `_find_column` logic into the base indicator class.

**Architecture:** 
- Split `IStockProvider` Protocol into three focused interfaces: `IMarketDataProvider` (prices/volumes), `ICompanyInfoProvider` (static info), and `IFinancialStatementProvider` (balance/income/cashflow sheets)
- Create market-specific provider classes (`AShareProvider`, `HKShareProvider`, `USShareProvider`) inheriting from a shared base, replacing the monolithic `AkshareProvider`
- Create a `ProviderFactory` to return the appropriate provider based on market configuration
- Move `_find_column` method from each indicator class to `BaseIndicator` for DRY compliance

**Tech Stack:** Python, Protocol (typing), dependency-injector, pandas, pytest

---

## Task 1: Split IStockProvider Interface (ISP)

**Files:**
- Modify: `src/value_investment/core/interfaces.py:1-50`
- Test: `tests/test_istock_provider.py`

**Step 1: Write failing tests for new interface structure**

```python
# tests/test_interface_isp.py
import pytest
from typing import Protocol

def test_imarket_data_provider_has_required_methods():
    """IMarketDataProvider should define get_historical_data"""
    from value_investment.core.interfaces import IMarketDataProvider
    required = ['get_historical_data']
    for method in required:
        assert hasattr(IMarketDataProvider, method)

def test_icompan y_info_provider_has_required_methods():
    """ICompanyInfoProvider should define get_stock_info"""
    from value_investment.core.interfaces import ICompanyInfoProvider
    required = ['get_stock_info']
    for method in required:
        assert hasattr(ICompanyInfoProvider, method)

def test_ifinancial_statement_provider_has_required_methods():
    """IFinancialStatementProvider should define balance/income/cashflow methods"""
    from value_investment.core.interfaces import IFinancialStatementProvider
    required = ['get_balance_sheet', 'get_income_statement', 'get_cash_flow_statement']
    for method in required:
        assert hasattr(IFinancialStatementProvider, method)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_interface_isp.py -v`
Expected: FAIL with "cannot import name 'IMarketDataProvider'"

**Step 3: Write minimal implementation**

```python
# src/value_investment/core/interfaces.py - add after existing imports

class IMarketDataProvider(Protocol):
    """Interface for market data (prices, volumes) - handles historical trading data"""

    def get_historical_data(
        self,
        stock_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
        adjust: str = ""
    ) -> "pd.DataFrame":
        """Get historical price data"""
        ...


class ICompanyInfoProvider(Protocol):
    """Interface for company information - static data like name, industry"""

    def get_stock_info(self, stock_code: str) -> "pd.DataFrame":
        """Get basic stock information"""
        ...


class IFinancialStatementProvider(Protocol):
    """Interface for financial statements - balance sheet, income, cash flow"""

    def get_balance_sheet(self, stock_code: str, end_year: int) -> "pd.DataFrame":
        """Get balance sheet data"""
        ...

    def get_income_statement(self, stock_code: str, end_year: int) -> "pd.DataFrame":
        """Get income statement data"""
        ...

    def get_cash_flow_statement(self, stock_code: str, end_year: int) -> "pd.DataFrame":
        """Get cash flow statement data"""
        ...


# Keep backward-compatible alias
IStockProvider = IFinancialStatementProvider  # For backward compatibility
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_interface_isp.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/core/interfaces.py tests/test_interface_isp.py
git commit -m "refactor(ISP): split IStockProvider into focused interfaces"
```

---

## Task 2: Create Market-Specific Provider Base Class

**Files:**
- Create: `src/value_investment/data/providers/base_provider.py`
- Modify: `src/value_investment/data/providers/akshare_provider.py`
- Test: `tests/test_base_provider.py`

**Step 1: Write failing tests**

```python
# tests/test_base_provider.py
import pytest
import pandas as pd

def test_base_provider_has_cache_and_market():
    """BaseProvider should have cache and market attributes"""
    from value_investment.data.providers.base_provider import BaseProvider
    assert hasattr(BaseProvider, '_cache')
    assert hasattr(BaseProvider, '_market')

def test_base_provider_abstract_methods():
    """BaseProvider should define abstract methods for market-specific implementations"""
    from value_investment.data.providers.base_provider import BaseProvider
    # Should have abstract methods for each data type
    import inspect
    methods = [m for m in dir(BaseProvider) if not m.startswith('_')]
    assert 'get_stock_info' in methods
    assert 'get_historical_data' in methods
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_base_provider.py -v`
Expected: FAIL with "No module named 'base_provider'"

**Step 3: Write minimal implementation**

```python
# src/value_investment/data/providers/base_provider.py
"""Base provider class with shared caching logic"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


def _get_ttl_until_next_midnight() -> int:
    """Get TTL in seconds until next midnight (for daily refresh data like stock info)"""
    now = datetime.now()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int((tomorrow - now).total_seconds())


def _get_ttl_until_june_next_year(end_year: int) -> int:
    """Get TTL in seconds until June 30th of the next year"""
    now = datetime.now()
    june_next_year = datetime(now.year + 1, 6, 30, 23, 59, 59)
    return int((june_next_year - now).total_seconds())


class BaseProvider(ABC):
    """Base class for market-specific providers with shared caching logic"""

    def __init__(self, cache: "SmartCache", market: str):
        """
        Initialize provider

        Args:
            cache: SmartCache instance
            market: Market type - "A" (A股), "HK" (港股), "US" (美股)
        """
        self._cache = cache
        self._market = market

    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format"""
        if not date_str:
            return date_str
        if "-" in date_str:
            return date_str
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    @abstractmethod
    def get_stock_info(self, symbol: str, force_refresh: bool = False) -> pd.DataFrame:
        """Get stock basic information - must be implemented by subclass"""
        pass

    @abstractmethod
    def get_historical_data(
        self,
        symbol: str,
        end_date: str,
        start_date: str | None = None,
        adjust: str = "hfq",
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get historical price data - must be implemented by subclass"""
        pass

    @abstractmethod
    def get_balance_sheet(
        self,
        symbol: str,
        end_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get balance sheet - must be implemented by subclass"""
        pass

    @abstractmethod
    def get_income_statement(
        self,
        symbol: str,
        end_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get income statement - must be implemented by subclass"""
        pass

    @abstractmethod
    def get_cash_flow_statement(
        self,
        symbol: str,
        end_year: int | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get cash flow statement - must be implemented by subclass"""
        pass
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_base_provider.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/data/providers/base_provider.py tests/test_base_provider.py
git commit -m "refactor(SRP): add BaseProvider abstract class for market-specific providers"
```

---

## Task 3: Create AShareProvider (A股)

**Files:**
- Create: `src/value_investment/data/providers/a_share_provider.py`
- Test: `tests/test_a_share_provider.py`

**Step 1: Write failing tests**

```python
# tests/test_a_share_provider.py
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

def test_a_share_provider_initialization():
    """AShareProvider should initialize with cache"""
    from value_investment.data.providers.a_share_provider import AShareProvider
    mock_cache = MagicMock()
    provider = AShareProvider(cache=mock_cache)
    assert provider._market == "A"
    assert provider._cache is mock_cache

def test_a_share_provider_get_stock_info():
    """AShareProvider.get_stock_info should fetch A股 info"""
    from value_investment.data.providers.a_share_provider import AShareProvider
    mock_cache = MagicMock()
    mock_cache.get.return_value = None
    provider = AShareProvider(cache=mock_cache)
    
    mock_data = pd.DataFrame({"item": ["股票代码"], "value": ["600519"]})
    with patch("akshare.stock_individual_info_em", return_value=mock_data):
        result = provider.get_stock_info("600519")
    
    assert "item" in result.columns
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_a_share_provider.py -v`
Expected: FAIL with "No module named 'a_share_provider'"

**Step 3: Write minimal implementation**

```python
# src/value_investment/data/providers/a_share_provider.py
"""A股 data provider"""
from datetime import datetime
from typing import TYPE_CHECKING

import akshare as ak
import pandas as pd

from value_investment.data.providers.base_provider import BaseProvider, _get_ttl_until_next_midnight, _get_ttl_until_june_next_year

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


class AShareProvider(BaseProvider):
    """Akshare data provider for A股 (Chinese A-shares)"""

    def get_stock_info(self, symbol: str, force_refresh: bool = False) -> pd.DataFrame:
        """Get A股 stock info"""
        cache_key = f"info_{symbol}"
        
        if force_refresh:
            self._cache.invalidate(cache_key)
        
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        data = ak.stock_individual_info_em(symbol=symbol)
        self._cache.set(cache_key, data, ttl=_get_ttl_until_next_midnight())
        return data

    def get_historical_data(
        self,
        symbol: str,
        end_date: str,
        start_date: str | None = None,
        adjust: str = "hfq",
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """Get A股 historical data"""
        end_date_normalized = self._normalize_date(end_date)
        start_date_normalized = self._normalize_date(start_date) if start_date else None
        
        cache_key = f"hist_{symbol}_{adjust}"
        
        def fetch_full_data() -> pd.DataFrame:
            tx_symbol = symbol
            if not symbol.startswith(("sh", "sz")):
                if symbol.startswith(("00", "30")):
                    tx_symbol = f"sz{symbol}"
                else:
                    tx_symbol = f"sh{symbol}"
            
            data = ak.stock_zh_a_hist_tx(
                symbol=tx_symbol,
                start_date="19700101",
                end_date=end_date,
                adjust=adjust,
            )
            data = data.rename(columns={
                "date": "日期", "open": "开盘", "close": "收盘",
                "high": "最高", "low": "最低", "amount": "成交量",
            })
            data["日期"] = pd.to_datetime(data["日期"]).dt.strftime("%Y-%m-%d")
            return data
        
        return self._cache.get_or_fetch_with_range(
            key=cache_key, date_column="日期", fetch_func=fetch_full_data,
            start_date=start_date_normalized, end_date=end_date_normalized,
            ttl=86400 * 365, force_refresh=force_refresh,
        )

    def get_balance_sheet(
        self, symbol: str, end_year: int | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        from datetime import datetime
        if end_year is None:
            end_year = datetime.now().year
        
        cache_key = f"balance_sheet_a_{symbol}"
        
        def fetch():
            full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
            return ak.stock_balance_sheet_by_yearly_em(symbol=full_symbol)
        
        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=_get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(df, end_year)

    def get_income_statement(
        self, symbol: str, end_year: int | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        from datetime import datetime
        if end_year is None:
            end_year = datetime.now().year
        
        cache_key = f"profit_sheet_a_{symbol}"
        
        def fetch():
            full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
            return ak.stock_profit_sheet_by_yearly_em(symbol=full_symbol)
        
        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=_get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(df, end_year)

    def get_cash_flow_statement(
        self, symbol: str, end_year: int | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        from datetime import datetime
        if end_year is None:
            end_year = datetime.now().year
        
        cache_key = f"cashflow_sheet_a_{symbol}"
        
        def fetch():
            full_symbol = f"SH{symbol}" if not symbol.startswith(("SH", "SZ")) else symbol
            return ak.stock_cash_flow_sheet_by_yearly_em(symbol=full_symbol)
        
        df = self._cache.get_or_fetch(
            cache_key, fetch, ttl=_get_ttl_until_june_next_year(datetime.now().year),
            force_refresh=force_refresh
        )
        return self._filter_by_year(df, end_year)

    def _filter_by_year(self, df: pd.DataFrame, end_year: int) -> pd.DataFrame:
        """Filter DataFrame by end_year"""
        if df.empty:
            return df
        
        year_col = None
        for col in ["REPORT", "year", "REPORT_DATE_NAME", "REPORT_DATE", "FISCAL_YEAR"]:
            if col in df.columns:
                year_col = col
                break
        
        if year_col is None:
            return df
        
        df = df.copy()
        try:
            if year_col == "REPORT_DATE_NAME":
                df["_year"] = pd.to_numeric(
                    df[year_col].astype(str).str.extract(r"(\d{4})")[0], errors="coerce"
                )
            elif df[year_col].dtype.kind in ['O', 'U']:
                df["_year"] = pd.to_datetime(df[year_col].astype(str), errors="coerce").dt.year
            else:
                df["_year"] = pd.to_numeric(df[year_col], errors="coerce")
            
            result = df[df["_year"] <= end_year].drop(columns=["_year"])
        except Exception:
            result = df
        
        return result
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_a_share_provider.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/data/providers/a_share_provider.py tests/test_a_share_provider.py
git commit -m "refactor(SRP): create AShareProvider for A股 data"
```

---

## Task 4: Create HKShareProvider and USShareProvider

**Files:**
- Create: `src/value_investment/data/providers/hk_share_provider.py`
- Create: `src/value_investment/data/providers/us_share_provider.py`
- Test: `tests/test_hk_share_provider.py`, `tests/test_us_share_provider.py`

**Step 1: Write failing tests**

```python
# tests/test_hk_share_provider.py
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

def test_hk_share_provider_initialization():
    """HKShareProvider should initialize with market='HK'"""
    from value_investment.data.providers.hk_share_provider import HKShareProvider
    mock_cache = MagicMock()
    provider = HKShareProvider(cache=mock_cache)
    assert provider._market == "HK"
```

```python
# tests/test_us_share_provider.py
def test_us_share_provider_initialization():
    """USShareProvider should initialize with market='US'"""
    from value_investment.data.providers.us_share_provider import USShareProvider
    mock_cache = MagicMock()
    provider = USShareProvider(cache=mock_cache)
    assert provider._market == "US"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_hk_share_provider.py tests/test_us_share_provider.py -v`
Expected: FAIL with "No module named 'hk_share_provider'"

**Step 3: Write implementations (similar pattern to AShareProvider)**

Create `hk_share_provider.py` and `us_share_provider.py` with market-specific akshare calls:
- HK: `stock_hk_company_profile_em`, `stock_hk_daily`, `stock_financial_hk_report_em`
- US: `stock_individual_basic_info_us_xq`, `stock_us_daily`, `stock_financial_us_report_em`

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_hk_share_provider.py tests/test_us_share_provider.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/data/providers/hk_share_provider.py src/value_investment/data/providers/us_share_provider.py tests/test_hk_share_provider.py tests/test_us_share_provider.py
git commit -m "refactor(SRP): create HKShareProvider and USShareProvider"
```

---

## Task 5: Create ProviderFactory (Facade Pattern)

**Files:**
- Create: `src/value_investment/data/providers/factory.py`
- Test: `tests/test_provider_factory.py`

**Step 1: Write failing tests**

```python
# tests/test_provider_factory.py
import pytest
from unittest.mock import MagicMock

def test_provider_factory_returns_ashare_for_market_a():
    """ProviderFactory should return AShareProvider for market='A'"""
    from value_investment.data.providers.factory import ProviderFactory
    mock_cache = MagicMock()
    provider = ProviderFactory.create_provider(mock_cache, market="A")
    assert provider.__class__.__name__ == "AShareProvider"

def test_provider_factory_returns_hkshare_for_market_hk():
    """ProviderFactory should return HKShareProvider for market='HK'"""
    from value_investment.data.providers.factory import ProviderFactory
    mock_cache = MagicMock()
    provider = ProviderFactory.create_provider(mock_cache, market="HK")
    assert provider.__class__.__name__ == "HKShareProvider"

def test_provider_factory_returns_us_share_for_market_us():
    """ProviderFactory should return USShareProvider for market='US'"""
    from value_investment.data.providers.factory import ProviderFactory
    mock_cache = MagicMock()
    provider = ProviderFactory.create_provider(mock_cache, market="US")
    assert provider.__class__.__name__ == "USShareProvider"
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_provider_factory.py -v`
Expected: FAIL with "No module named 'factory'"

**Step 3: Write implementation**

```python
# src/value_investment/data/providers/factory.py
"""Provider factory for creating market-specific providers"""
from typing import TYPE_CHECKING

from value_investment.data.providers.a_share_provider import AShareProvider
from value_investment.data.providers.hk_share_provider import HKShareProvider
from value_investment.data.providers.us_share_provider import USShareProvider

if TYPE_CHECKING:
    from value_investment.data.cache import SmartCache


class ProviderFactory:
    """Factory for creating market-specific stock data providers"""

    _PROVIDER_MAP = {
        "A": AShareProvider,
        "HK": HKShareProvider,
        "US": USShareProvider,
    }

    @classmethod
    def create_provider(cls, cache: "SmartCache", market: str = "A"):
        """
        Create a provider instance for the specified market

        Args:
            cache: SmartCache instance
            market: Market type - "A" (A股), "HK" (港股), "US" (美股)

        Returns:
            Provider instance for the specified market

        Raises:
            ValueError: If market is not supported
        """
        provider_class = cls._PROVIDER_MAP.get(market.upper())
        if provider_class is None:
            raise ValueError(f"Unsupported market: {market}. Supported: {list(cls._PROVIDER_MAP.keys())}")
        return provider_class(cache=cache)
```

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_provider_factory.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/data/providers/factory.py tests/test_provider_factory.py
git commit -m "refactor: add ProviderFactory for market-specific provider creation"
```

---

## Task 6: Update Container to Use ProviderFactory

**Files:**
- Modify: `src/value_investment/core/container.py`
- Test: `tests/test_container.py`

**Step 1: Write failing test**

```python
# tests/test_container.py - add to existing
def test_container_uses_factory():
    """Container should create providers via ProviderFactory"""
    from value_investment.core.container import Container
    container = Container()
    # Should work with ProviderFactory now
    from value_investment.data.providers.factory import ProviderFactory
    provider = ProviderFactory.create_provider(container.cache(), market="A")
    assert provider is not None
```

**Step 2: Run test**

Run: `pytest tests/test_container.py::test_container_uses_factory -v`
Expected: PASS (container already works, just verify integration)

**Step 3: Update container for factory pattern**

```python
# src/value_investment/core/container.py - update akshare_provider factory
from value_investment.data.providers.factory import ProviderFactory

# Replace:
# akshare_provider = providers.Factory(AkshareProvider, cache=cache, market=config.market)
# With:
akshare_provider = providers.Callable(
    ProviderFactory.create_provider,
    cache=cache,
    market=config.market,
)
```

**Step 4: Commit**

```bash
git add src/value_investment/core/container.py
git commit -m "refactor: update container to use ProviderFactory"
```

---

## Task 7: Extract _find_column to BaseIndicator (DRY)

**Files:**
- Modify: `src/value_investment/indicators/base.py`
- Modify: `src/value_investment/indicators/profitability.py`
- Modify: `src/value_investment/indicators/safety.py`
- Test: `tests/test_indicator_base_find_column.py`

**Step 1: Write failing test**

```python
# tests/test_indicator_base_find_column.py
import pytest
import pandas as pd

def test_base_indicator_has_find_column():
    """BaseIndicator should have _find_column method"""
    from value_investment.indicators.base import BaseIndicator
    assert hasattr(BaseIndicator, '_find_column')

def test_roe_indicator_uses_base_find_column():
    """ROEIndicator should use BaseIndicator._find_column"""
    from value_investment.indicators.base import BaseIndicator
    from value_investment.indicators.profitability import ROEIndicator
    
    # Check that ROEIndicator uses the inherited method
    assert ROEIndicator._find_column is BaseIndicator._find_column
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_indicator_base_find_column.py -v`
Expected: FAIL with "BaseIndicator does not have _find_column"

**Step 3: Add _find_column to BaseIndicator**

```python
# src/value_investment/indicators/base.py - add to BaseIndicator class

def _find_column(self, df: pd.DataFrame, candidates: list[str], strict: bool = False) -> str | None:
    """Find first matching column from candidates
    
    Args:
        df: DataFrame to search in
        candidates: List of column names to try (in order of priority)
        strict: If True, only exact matches; if False, also try fuzzy matching
        
    Returns:
        Column name if found, None otherwise
    """
    # First try exact match
    for col in candidates:
        if col in df.columns:
            return col
    
    # If not strict, try fuzzy match (case-insensitive contains)
    if not strict:
        for col in df.columns:
            for cand in candidates:
                if cand.lower() in col.lower():
                    return col
    
    return None
```

**Step 4: Update indicator classes to use inherited method**

```python
# src/value_investment/indicators/profitability.py - remove _find_column from ROEIndicator

class ROEIndicator(BaseIndicator):
    # ... keep calculate and get_required_fields, REMOVE _find_column method
    # The inherited _find_column from BaseIndicator will be used
    pass  # No local _find_column definition
```

Do the same for:
- ROAIndicator
- GrossMarginIndicator
- NetProfitMarginIndicator
- OperatingProfitMarginIndicator
- CashToDebtIndicator
- DebtRatioTotalIndicator

**Step 5: Run test to verify it passes**

Run: `pytest tests/test_indicator_base_find_column.py -v`
Expected: PASS

**Step 6: Run existing indicator tests to ensure nothing broke**

Run: `pytest tests/test_profitability_indicators.py tests/test_safety_indicators.py -v`
Expected: PASS (or fix any issues)

**Step 7: Commit**

```bash
git add src/value_investment/indicators/base.py src/value_investment/indicators/profitability.py src/value_investment/indicators/safety.py tests/test_indicator_base_find_column.py
git commit -m "refactor(DRY): extract _find_column to BaseIndicator"
```

---

## Task 8: Align Interface Method Names (LSP)

**Files:**
- Modify: `src/value_investment/core/interfaces.py`
- Modify: `src/value_investment/data/providers/a_share_provider.py` (and others)
- Test: `tests/test_lsp_compliance.py`

**Step 1: Write failing test**

```python
# tests/test_lsp_compliance.py
import pytest

def test_income_statement_method_exists():
    """Providers should have get_income_statement method per IStockProvider"""
    from value_investment.data.providers.a_share_provider import AShareProvider
    from value_investment.data.providers.factory import ProviderFactory
    
    # Check Protocol definition expects get_income_statement
    from value_investment.core.interfaces import IFinancialStatementProvider
    assert hasattr(IFinancialStatementProvider, 'get_income_statement')
```

**Step 2: Run test**

Run: `pytest tests/test_lsp_compliance.py -v`
Expected: FAIL - currently uses `get_profit_sheet` instead of `get_income_statement`

**Step 3: Rename method in providers**

In `a_share_provider.py`, `hk_share_provider.py`, `us_share_provider.py`:
Rename `get_profit_sheet` to `get_income_statement` to match interface

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_lsp_compliance.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/value_investment/data/providers/a_share_provider.py src/value_investment/data/providers/hk_share_provider.py src/value_investment/data/providers/us_share_provider.py tests/test_lsp_compliance.py
git commit -m "refactor(LSP): align method names with interface contract"
```

---

## Task 9: Run Full Test Suite

**Files:**
- Test: All existing tests

**Step 1: Run full test suite**

Run: `uv run python -m pytest tests/ -v --tb=short 2>&1 | head -100`

**Step 2: Fix any breaking changes**

Expected: Most tests should pass. Fix any issues related to:
- Import paths changed
- Provider class names changed
- Method names renamed

**Step 3: Commit**

```bash
git add -A
git commit -m "fix: resolve test failures from SOLID refactoring"
```

---

## Task 10: Update CLI and API Entry Points

**Files:**
- Modify: `src/value_investment/api.py`
- Modify: `src/value_investment/cli.py`

**Step 1: Verify CLI still works**

Run: `uv run python -m value_investment.cli --help`

**Step 2: If broken, update imports**

Update to use `ProviderFactory` or the new provider classes:
```python
# api.py - update provider initialization
from value_investment.data.providers.factory import ProviderFactory

# Replace AkshareProvider(...) with:
provider = ProviderFactory.create_provider(cache, market=market)
```

**Step 3: Commit**

```bash
git add src/value_investment/api.py src/value_investment/cli.py
git commit -m "refactor: update API and CLI to use new provider structure"
```

---

## Summary of Changes

| Task | SOLID Principle | Change |
|------|-----------------|--------|
| 1 | ISP | Split `IStockProvider` into `IMarketDataProvider`, `ICompanyInfoProvider`, `IFinancialStatementProvider` |
| 2-5 | SRP | Create `BaseProvider` → `AShareProvider`, `HKShareProvider`, `USShareProvider` + `ProviderFactory` |
| 6 | DIP | Update container to use factory pattern |
| 7 | DRY | Extract `_find_column` to `BaseIndicator` |
| 8 | LSP | Rename `get_profit_sheet` → `get_income_statement` to match interface |
| 9-10 | Integration | Run tests, fix issues, update CLI/API |
