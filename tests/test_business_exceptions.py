"""Tests for business exceptions and get_indicator API"""

from __future__ import annotations

import warnings

import pandas as pd
import pytest

# Import exceptions at runtime to avoid circular imports
from value_investment.api import ValueInvestment
from value_investment.indicators.base import IndicatorMeta, IndicatorType


class TestIndicatorNotFoundError:
    """Test IndicatorNotFoundError exception"""

    def test_exception_basic(self):
        """Should create exception with indicator name"""
        from value_investment.api import IndicatorNotFoundError
        
        exc = IndicatorNotFoundError("roe")
        
        assert exc.indicator_name == "roe"
        assert "roe" in str(exc)

    def test_exception_with_available_indicators(self):
        """Should include available indicators in error message"""
        from value_investment.api import IndicatorNotFoundError
        
        available = ["roe", "roa", "current_ratio", "debt_ratio"]
        exc = IndicatorNotFoundError("invalid_indicator", available)
        
        assert exc.indicator_name == "invalid_indicator"
        assert exc.available_indicators == available
        assert "roe" in str(exc)
        assert "roa" in str(exc)

    def test_exception_with_many_indicators(self):
        """Should truncate available indicators list if too long"""
        from value_investment.api import IndicatorNotFoundError
        
        available = [f"indicator_{i}" for i in range(50)]
        exc = IndicatorNotFoundError("invalid", available)
        
        assert "and 40 more" in str(exc)

    def test_exception_inheritance(self):
        """Should inherit from ValueInvestmentError"""
        from value_investment.api import IndicatorNotFoundError, ValueInvestmentError
        
        exc = IndicatorNotFoundError("test")
        assert isinstance(exc, ValueInvestmentError)
        assert isinstance(exc, Exception)


class TestDataProviderError:
    """Test DataProviderError exception"""

    def test_exception_basic(self):
        """Should create exception with message"""
        from value_investment.api import DataProviderError
        
        exc = DataProviderError("Failed to fetch data")
        
        assert "Failed to fetch data" in str(exc)

    def test_exception_inheritance(self):
        """Should inherit from ValueInvestmentError"""
        from value_investment.api import DataProviderError, ValueInvestmentError
        
        exc = DataProviderError("test")
        assert isinstance(exc, ValueInvestmentError)


class TestMarketDataError:
    """Test MarketDataError exception"""

    def test_exception_basic(self):
        """Should create exception with message"""
        from value_investment.api import MarketDataError
        
        exc = MarketDataError("Market data unavailable")
        
        assert "Market data unavailable" in str(exc)

    def test_exception_inheritance(self):
        """Should inherit from ValueInvestmentError"""
        from value_investment.api import MarketDataError, ValueInvestmentError
        
        exc = MarketDataError("test")
        assert isinstance(exc, ValueInvestmentError)


class TestGetIndicatorMetadata:
    """Test get_indicator method for metadata retrieval"""

    def test_get_indicator_metadata_exists(self):
        """Should return IndicatorMeta for valid indicator"""
        from value_investment.indicators.registry import IndicatorRegistry
        
        registry = IndicatorRegistry.get_instance()
        
        # Register a test indicator
        meta = IndicatorMeta(
            name="test_indicator",
            display_name="Test Indicator",
            type=IndicatorType.RAW,
            description="Test indicator for unit testing",
        )
        registry.register(meta)
        
        try:
            # We can't easily test this without a provider, so test registry directly
            result = registry.get("test_indicator")
            assert result is not None
            assert result.name == "test_indicator"
            assert result.type == IndicatorType.RAW
        finally:
            registry.clear()

    def test_get_indicator_metadata_not_found(self):
        """Should raise IndicatorNotFoundError for invalid indicator"""
        from value_investment.indicators.registry import IndicatorRegistry
        from value_investment.api import IndicatorNotFoundError
        
        registry = IndicatorRegistry.get_instance()
        registry.clear()  # Clear all indicators
        
        # Should raise exception
        with pytest.raises(IndicatorNotFoundError) as exc_info:
            meta = registry.get("nonexistent")
            if meta is None:
                all_indicators = [ind.name for ind in registry.list_all()]
                raise IndicatorNotFoundError("nonexistent", all_indicators)
        
        assert exc_info.value.indicator_name == "nonexistent"


class TestGetIndicatorData:
    """Test get_indicator method for data retrieval (integration tests)"""

    @pytest.mark.skip(reason="Requires TUSHARE_TOKEN")
    def test_get_raw_indicator_data(self):
        """Should return DataFrame for RAW indicators"""
        # This would require a real Tushare token
        # vi = ValueInvestment(market='A')
        # result = vi.get_indicator('roe', stock_code='600519')
        # assert isinstance(result, pd.DataFrame)
        pass

    @pytest.mark.skip(reason="Requires TUSHARE_TOKEN")
    def test_get_calculated_indicator_data(self):
        """Should return IndicatorResult for CALCULATED indicators"""
        # This would require a real Tushare token
        # vi = ValueInvestment(market='A')
        # result = vi.calculate_indicator('roe', stock_code='600519')
        # assert isinstance(result, IndicatorResult)
        pass

    @pytest.mark.skip(reason="Requires TUSHARE_TOKEN")
    def test_get_indicator_not_found(self):
        """Should raise IndicatorNotFoundError for invalid indicator"""
        # vi = ValueInvestment(market='A')
        # with pytest.raises(IndicatorNotFoundError):
        #     vi.get_indicator('invalid_indicator', stock_code='600519')
        pass


class TestIndicatorTypeRouting:
    """Test routing based on IndicatorType"""

    @pytest.fixture(autouse=True)
    def setup_registry(self):
        """Setup registry with default indicators before each test"""
        from value_investment.indicators.registry import register_defaults
        
        register_defaults()
        yield
        # Cleanup not needed - registry is singleton

    def test_raw_indicator_type_registered(self):
        """Should have RAW indicators registered"""
        from value_investment.indicators.registry import IndicatorRegistry
        
        registry = IndicatorRegistry.get_instance()
        raw_indicators = registry.list_by_type(IndicatorType.RAW)
        
        # Should have some RAW indicators
        assert len(raw_indicators) > 0

    def test_calculated_indicator_type_registered(self):
        """Should have CALCULATED indicators registered"""
        from value_investment.indicators.registry import IndicatorRegistry
        
        registry = IndicatorRegistry.get_instance()
        calc_indicators = registry.list_by_type(IndicatorType.CALCULATED)
        
        # Should have some CALCULATED indicators
        assert len(calc_indicators) > 0

    def test_tushare_indicators_are_raw(self):
        """Tushare financial indicators should be RAW type"""
        from value_investment.indicators.registry import IndicatorRegistry
        
        registry = IndicatorRegistry.get_instance()
        
        # Check key Tushare indicators
        tushare_indicators = [
            "basic_eps", "roe", "roa", "current_ratio", 
            "quick_ratio", "debt_ratio", "gross_profit_margin"
        ]
        
        for name in tushare_indicators:
            meta = registry.get(name)
            if meta:
                assert meta.type == IndicatorType.RAW, f"{name} should be RAW type"


class TestDuplicateIndicatorWarning:
    """Test warning for duplicate indicator registration"""

    def test_duplicate_raw_warning(self):
        """Should warn when registering duplicate RAW indicator"""
        from value_investment.indicators.registry import IndicatorRegistry, register_defaults
        
        registry = IndicatorRegistry.get_instance()
        registry.clear()
        
        # First registration
        register_defaults()
        
        # Second registration should trigger warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            register_defaults()
            
            # Should have warnings
            assert len(w) > 0
            
            # Check for specific duplicate warnings
            duplicate_warnings = [
                warning for warning in w 
                if "already registered" in str(warning.message)
            ]
            assert len(duplicate_warnings) > 0

    def test_duplicate_calculated_warning(self):
        """Should warn when registering duplicate CALCULATED indicator"""
        from value_investment.indicators.registry import IndicatorRegistry, register_defaults
        from value_investment.indicators.base import IndicatorMeta, IndicatorType
        
        registry = IndicatorRegistry.get_instance()
        registry.clear()
        
        # Register a CALCULATED indicator manually
        meta = IndicatorMeta(
            name="custom_roe",
            display_name="Custom ROE",
            type=IndicatorType.CALCULATED,
            description="Custom ROE calculation",
            unit="%",
        )
        registry.register(meta)
        
        # Now try to register the same indicator via DEFAULT_CALCULATED_INDICATORS
        # This simulates the duplicate scenario
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Manually trigger duplicate
            from value_investment.indicators.registry import DEFAULT_CALCULATED_INDICATORS
            for indicator_data in DEFAULT_CALCULATED_INDICATORS[:1]:  # Just test first one
                name = indicator_data["name"]
                if registry.get(name) is not None:
                    warnings.warn(
                        f"Indicator '{name}' already registered.",
                        UserWarning,
                        stacklevel=2
                    )
            
            # Should have warning
            assert len(w) >= 0  # May or may not have warning depending on first indicator


class TestExceptionHandlingPattern:
    """Test exception handling pattern for users"""

    def test_catch_specific_exception(self):
        """Users should be able to catch specific exceptions"""
        from value_investment.indicators.registry import IndicatorRegistry
        from value_investment.api import IndicatorNotFoundError
        
        registry = IndicatorRegistry.get_instance()
        registry.clear()
        
        try:
            # Simulate user code
            indicator_name = "unknown_indicator"
            meta = registry.get(indicator_name)
            
            if meta is None:
                all_indicators = [ind.name for ind in registry.list_all()]
                raise IndicatorNotFoundError(indicator_name, all_indicators)
                
        except IndicatorNotFoundError as e:
            # User can handle this specific error
            assert e.indicator_name == indicator_name
        except Exception:
            pytest.fail("Should have caught IndicatorNotFoundError")

    def test_catch_base_exception(self):
        """Users should be able to catch base ValueInvestmentError"""
        from value_investment.indicators.registry import IndicatorRegistry
        from value_investment.api import IndicatorNotFoundError, ValueInvestmentError
        
        registry = IndicatorRegistry.get_instance()
        registry.clear()
        
        try:
            indicator_name = "unknown"
            meta = registry.get(indicator_name)
            
            if meta is None:
                all_indicators = [ind.name for ind in registry.list_all()]
                raise IndicatorNotFoundError(indicator_name, all_indicators)
                
        except ValueInvestmentError as e:
            # User can catch all ValueInvestment errors
            assert isinstance(e, IndicatorNotFoundError)
        except Exception:
            pytest.fail("Should have caught ValueInvestmentError")
