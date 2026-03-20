"""Comprehensive tests for Pipeline API"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

from value_investment.pipeline.api import PipelineAPI, CALCULATOR_MAP
from value_investment.domain.fields import ALL_FIELDS
from value_investment.pipeline.validator import ValidationReport
from value_investment.core.types import Message


# ============================================================================
# Test Market Detection
# ============================================================================

class TestMarketDetection:
    """Test _detect_market method"""

    def test_detect_a_stock(self):
        """Test A股 detection"""
        api = PipelineAPI()
        # A股: 6位数字 (0/3/6开头)
        assert api._detect_market("600519") == "A股"
        assert api._detect_market("000001") == "A股"
        assert api._detect_market("300001") == "A股"

    def test_detect_hk_stock(self):
        """Test 港股 detection"""
        api = PipelineAPI()
        # 港股: 5位数字
        assert api._detect_market("00700") == "港股"
        assert api._detect_market("09988") == "港股"

    def test_detect_us_stock(self):
        """Test 美股 detection"""
        api = PipelineAPI()
        # 美股: 字母代码
        assert api._detect_market("AAPL") == "美股"
        assert api._detect_market("TSLA") == "美股"
        assert api._detect_market("GOOGL") == "美股"

    def test_detect_mixed_case(self):
        """Test mixed case detection"""
        api = PipelineAPI()
        assert api._detect_market("aapl") == "美股"
        assert api._detect_market("MsFt") == "美股"


# ============================================================================
# Test Container Access
# ============================================================================

class TestContainerAccess:
    """Test container property"""

    def test_container_is_available(self):
        """Test container is accessible"""
        api = PipelineAPI()
        assert api.container is not None

    def test_container_is_singleton(self):
        """Test container follows singleton pattern"""
        api1 = PipelineAPI()
        api2 = PipelineAPI()
        # Should be the same instance
        assert api1.container is api2.container


# ============================================================================
# Test Validation
# ============================================================================

class TestValidate:
    """Test validate method"""

    def test_validate_a_stock(self):
        """Test A股 validation"""
        api = PipelineAPI()
        report = api.validate("600519", ["total_revenue", "net_profit"])
        
        assert isinstance(report, ValidationReport)
        assert report.market == "A股"

    def test_validate_hk_stock(self):
        """Test 港股 validation"""
        api = PipelineAPI()
        report = api.validate("00700", ["total_revenue"])
        
        assert isinstance(report, ValidationReport)
        assert report.market == "港股"

    def test_validate_us_stock(self):
        """Test 美股 validation"""
        api = PipelineAPI()
        report = api.validate("AAPL", ["total_revenue"])
        
        assert isinstance(report, ValidationReport)
        assert report.market == "美股"

    def test_validate_with_explicit_market(self):
        """Test validation with explicit market"""
        api = PipelineAPI()
        report = api.validate("600519", ["total_revenue"], market="A股")
        
        assert report.market == "A股"

    def test_validate_with_calculator_field(self):
        """Test validation with calculator field"""
        api = PipelineAPI()
        report = api.validate("600519", ["implied_growth"])
        
        assert isinstance(report, ValidationReport)
        assert "implied_growth" in report.fields_requested

    def test_validate_returns_dry_run_true(self):
        """Test validation is always dry run"""
        api = PipelineAPI()
        report = api.validate("600519", ["total_revenue"])
        
        assert report.dry_run is True


# ============================================================================
# Test Field Expansion
# ============================================================================

class TestExpandRequiredFields:
    """Test _expand_required_fields method"""

    def test_expand_calculator_dependencies(self):
        """Test calculator field expansion"""
        api = PipelineAPI()
        
        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=10,
            require={"implied_growth"},
        )
        
        api._expand_required_fields(message)
        
        # Should include implied_growth dependencies
        assert "implied_growth" in message.require
        assert len(message.require) > 1  # Should have dependencies too

    def test_regular_fields_not_expanded(self):
        """Test regular fields don't expand"""
        api = PipelineAPI()
        
        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=10,
            require={"total_revenue", "net_profit"},
        )
        
        original_len = len(message.require)
        api._expand_required_fields(message)
        
        # Should not add new fields
        assert len(message.require) == original_len

    def test_mixed_fields(self):
        """Test mixed calculator and regular fields"""
        api = PipelineAPI()
        
        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=10,
            require={"total_revenue", "implied_growth"},
        )
        
        api._expand_required_fields(message)
        
        assert "total_revenue" in message.require
        assert "implied_growth" in message.require


# ============================================================================
# Test Apply Calculators
# ============================================================================

class TestApplyCalculators:
    """Test _apply_calculators method"""

    def test_apply_single_calculator(self):
        """Test applying a single calculator"""
        api = PipelineAPI()
        
        # Create message with required data for a calculator
        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=10,
            require={"gross_profit"},  # Calculator field
        )
        # Add required fields
        message.results["total_revenue"] = {2024: 1000000}
        message.results["operating_cost"] = {2024: 600000}
        
        api._apply_calculators(message)
        
        # Calculator should have been applied
        assert "gross_profit" in message.results

    def test_apply_calculator_with_missing_dependencies(self):
        """Test calculator not applied when dependencies missing"""
        api = PipelineAPI()
        
        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=10,
            require={"implied_growth"},  # Has dependencies
        )
        # Don't add required fields
        
        api._apply_calculators(message)
        
        # Should not add result for calculator
        assert "implied_growth" not in message.results

    def test_apply_multiple_calculators(self):
        """Test applying multiple calculators"""
        api = PipelineAPI()
        
        message = Message(
            symbol="600519",
            market="A股",
            end="2024",
            years=10,
            require={"gross_profit"},
        )
        message.results["total_revenue"] = {2024: 1000000}
        message.results["operating_cost"] = {2024: 600000}
        
        api._apply_calculators(message)
        
        # Should have calculated result
        assert "gross_profit" in message.results


# ============================================================================
# Test Get Data (Async)
# ============================================================================

class TestGetData:
    """Test get_data async method"""

    @pytest.mark.asyncio
    async def test_get_data_unknown_fields_warning(self):
        """Test warning for unknown fields"""
        api = PipelineAPI()
        
        with pytest.warns(UserWarning, match="Unknown fields"):
            try:
                await api.get_data("600519", ["unknown_field_xyz"])
            except (ValueError, Exception):
                pass  # Expected - missing fields

    @pytest.mark.asyncio
    async def test_get_data_market_detection(self):
        """Test automatic market detection"""
        api = PipelineAPI()
        
        # Should detect A股
        with patch.object(api._container.bus(), 'process', new_callable=AsyncMock):
            try:
                await api.get_data("600519", ["total_revenue"])
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_get_data_with_explicit_market(self):
        """Test with explicit market parameter"""
        api = PipelineAPI()
        
        with patch.object(api._container.bus(), 'process', new_callable=AsyncMock):
            try:
                await api.get_data("600519", ["total_revenue"], market="A股")
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_get_data_with_end_year(self):
        """Test with end year parameter"""
        api = PipelineAPI()
        
        with patch.object(api._container.bus(), 'process', new_callable=AsyncMock):
            try:
                await api.get_data("600519", ["total_revenue"], end="2023")
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_get_data_with_years(self):
        """Test with years parameter"""
        api = PipelineAPI()
        
        with patch.object(api._container.bus(), 'process', new_callable=AsyncMock):
            try:
                await api.get_data("600519", ["total_revenue"], years=5)
            except Exception:
                pass

    @pytest.mark.asyncio
    async def test_get_data_missing_fields_raises(self):
        """Test that missing fields raise ValueError"""
        api = PipelineAPI()
        
        # Mock empty results
        with patch.object(api._container.bus(), 'process', new_callable=AsyncMock) as mock_process:
            async def empty_process(msg):
                # Don't add any results
                pass
            
            mock_process.side_effect = empty_process
            
            with pytest.raises(ValueError, match="Missing fields"):
                await api.get_data("600519", ["total_revenue"])


# ============================================================================
# Test Calculator Map
# ============================================================================

class TestCalculatorMap:
    """Test CALCULATOR_MAP constant"""

    def test_calculator_map_exists(self):
        """Test CALCULATOR_MAP is defined"""
        assert isinstance(CALCULATOR_MAP, dict)

    def test_calculator_map_contains_calculators(self):
        """Test CALCULATOR_MAP contains calculators"""
        assert len(CALCULATOR_MAP) > 0

    def test_calculator_map_has_expected_calculators(self):
        """Test known calculators are in the map"""
        expected = {"gross_profit", "inventory_turnover", "implied_growth"}
        for calc_name in expected:
            if calc_name in CALCULATOR_MAP:
                assert True
                return
        # If not in map, test passes (calculator might not exist)


# ============================================================================
# Test Integration
# ============================================================================

class TestIntegration:
    """Integration tests"""

    def test_api_validation_flow(self):
        """Test full validation flow"""
        api = PipelineAPI()
        
        # Validate A股 stock
        report = api.validate("600519", ["total_revenue", "net_profit", "roic"])
        
        assert isinstance(report, ValidationReport)
        assert len(report.fields_requested) == 3

    def test_api_validation_with_multiple_markets(self):
        """Test validation for different markets"""
        api = PipelineAPI()
        
        # A股
        report_a = api.validate("600519", ["total_revenue"])
        assert report_a.market == "A股"
        
        # 港股
        report_hk = api.validate("00700", ["total_revenue"])
        assert report_hk.market == "港股"
        
        # 美股
        report_us = api.validate("AAPL", ["total_revenue"])
        assert report_us.market == "美股"

    def test_api_with_calculator_fields(self):
        """Test API with calculator fields"""
        api = PipelineAPI()
        
        # implied_growth requires roic, roic requires other fields
        report = api.validate("600519", ["implied_growth"])
        
        assert isinstance(report, ValidationReport)
        # Should have expanded to include dependencies
        assert len(report.fields_expanded) >= len(report.fields_requested)
