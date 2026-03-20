"""Comprehensive tests for HK Share Handlers"""
import pytest
from unittest.mock import MagicMock, AsyncMock
import pandas as pd

from value_investment.handlers.hk_share import (
    HKShareStatementHandler,
    HKShareIndicatorHandler,
    HKShareMarketHandler,
    HK_SHARE_STATEMENT_FIELDS,
    HK_SHARE_INDICATOR_FIELDS,
    HK_SHARE_MARKET_FIELDS,
)
from value_investment.core.types import Message


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_provider():
    """Create a mock provider"""
    provider = MagicMock()
    return provider


@pytest.fixture
def statement_handler(mock_provider):
    """Create HKShareStatementHandler with mock provider"""
    return HKShareStatementHandler(provider=mock_provider)


@pytest.fixture
def indicator_handler(mock_provider):
    """Create HKShareIndicatorHandler with mock provider"""
    return HKShareIndicatorHandler(provider=mock_provider)


@pytest.fixture
def market_handler(mock_provider):
    """Create HKShareMarketHandler with mock provider"""
    return HKShareMarketHandler(provider=mock_provider)


@pytest.fixture
def message():
    """Create a test message"""
    return Message(
        symbol="00700",
        market="港股",
        end="2024",
        years=10,
        require={"total_revenue", "net_profit", "roe"},
    )


# ============================================================================
# Test field constants
# ============================================================================

class TestFieldConstants:
    """Test field constants"""

    def test_statement_fields_is_set(self):
        """HK_SHARE_STATEMENT_FIELDS should be a set"""
        assert isinstance(HK_SHARE_STATEMENT_FIELDS, set)

    def test_statement_fields_contains_core(self):
        """Should contain core financial fields"""
        assert "total_revenue" in HK_SHARE_STATEMENT_FIELDS
        assert "net_profit" in HK_SHARE_STATEMENT_FIELDS
        assert "total_assets" in HK_SHARE_STATEMENT_FIELDS

    def test_indicator_fields_is_set(self):
        """HK_SHARE_INDICATOR_FIELDS should be a set"""
        assert isinstance(HK_SHARE_INDICATOR_FIELDS, set)

    def test_indicator_fields_contains_core(self):
        """Should contain core indicator fields"""
        assert "roe" in HK_SHARE_INDICATOR_FIELDS
        assert "roa" in HK_SHARE_INDICATOR_FIELDS
        assert "gross_margin" in HK_SHARE_INDICATOR_FIELDS

    def test_market_fields_is_set(self):
        """HK_SHARE_MARKET_FIELDS should be a set"""
        assert isinstance(HK_SHARE_MARKET_FIELDS, set)

    def test_market_fields_contains_core(self):
        """Should contain core market fields"""
        assert "market_cap" in HK_SHARE_MARKET_FIELDS
        assert "pe_ratio" in HK_SHARE_MARKET_FIELDS
        assert "pb_ratio" in HK_SHARE_MARKET_FIELDS


# ============================================================================
# Test Statement Handler
# ============================================================================

class TestStatementHandler:
    """Test HKShareStatementHandler"""

    def test_handler_properties(self, statement_handler):
        """Test handler target_market"""
        assert statement_handler.target_market == "港股"

    def test_handler_with_provider(self, mock_provider):
        """Test handler initialization with provider"""
        handler = HKShareStatementHandler(provider=mock_provider)
        assert handler._provider is not None

    def test_handler_without_provider(self):
        """Test handler initialization without provider"""
        handler = HKShareStatementHandler(provider=None)
        assert handler._provider is None

    def test_get_balance_fields(self, statement_handler):
        """Test _get_balance_fields method"""
        fields = statement_handler._get_balance_fields()
        assert isinstance(fields, set)
        assert "total_assets" in fields

    def test_get_income_fields(self, statement_handler):
        """Test _get_income_fields method"""
        fields = statement_handler._get_income_fields()
        assert isinstance(fields, set)
        assert "total_revenue" in fields

    def test_get_cashflow_fields(self, statement_handler):
        """Test _get_cashflow_fields method"""
        fields = statement_handler._get_cashflow_fields()
        assert isinstance(fields, set)
        assert "operating_cash_flow" in fields

    @pytest.mark.asyncio
    async def test_handle_with_empty_require(self, statement_handler, message):
        """Test handling when require is empty"""
        message.require = set()
        await statement_handler.handle(message)
        assert len(message.results) == 0

    @pytest.mark.asyncio
    async def test_handle_with_no_provider(self, message):
        """Test handling without provider"""
        handler = HKShareStatementHandler(provider=None)
        original_require = message.require.copy()
        await handler.handle(message)
        # Should not modify message when no provider

    def test_add_results_from_df(self, statement_handler, message):
        """Test _add_results_from_df method"""
        df = pd.DataFrame({
            "year": [2024, 2023],
            "total_revenue": [751766000000, 660000000000],
        })
        
        statement_handler._add_results_from_df(
            df, message, {"total_revenue"}
        )
        
        assert "total_revenue" in message.results

    def test_add_results_from_df_empty(self, statement_handler, message):
        """Test _add_results_from_df with empty DataFrame"""
        df = pd.DataFrame()
        original_len = len(message.results)
        
        statement_handler._add_results_from_df(
            df, message, {"total_revenue"}
        )
        
        assert len(message.results) == original_len

    def test_add_results_from_df_no_year(self, statement_handler, message):
        """Test _add_results_from_df without year column"""
        df = pd.DataFrame({
            "total_revenue": [100],
        })
        original_len = len(message.results)
        
        statement_handler._add_results_from_df(
            df, message, {"total_revenue"}
        )
        
        assert len(message.results) == original_len


# ============================================================================
# Test Indicator Handler
# ============================================================================

class TestIndicatorHandler:
    """Test HKShareIndicatorHandler"""

    def test_handler_properties(self, indicator_handler):
        """Test handler target_market"""
        assert indicator_handler.target_market == "港股"

    def test_handler_with_provider(self, mock_provider):
        """Test handler initialization with provider"""
        handler = HKShareIndicatorHandler(provider=mock_provider)
        assert handler._provider is not None

    @pytest.mark.asyncio
    async def test_handle_with_indicators(self, indicator_handler, mock_provider, message):
        """Test handling with indicator provider"""
        message.require = {"roe", "roa"}
        mock_provider.fetch_indicators.return_value = {
            "roe": {2024: 21.13},
            "roa": {2024: 11.77},
        }
        
        await indicator_handler.handle(message)
        
        mock_provider.fetch_indicators.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_with_empty_require(self, indicator_handler, message):
        """Test handling when require is empty"""
        message.require = set()
        await indicator_handler.handle(message)
        # Should not call provider


# ============================================================================
# Test Market Handler
# ============================================================================

class TestMarketHandler:
    """Test HKShareMarketHandler"""

    def test_handler_properties(self, market_handler):
        """Test handler target_market"""
        assert market_handler.target_market == "港股"

    def test_handler_with_provider(self, mock_provider):
        """Test handler initialization with provider"""
        handler = HKShareMarketHandler(provider=mock_provider)
        assert handler._provider is not None

    @pytest.mark.asyncio
    async def test_handle_with_market_data(self, market_handler, mock_provider, message):
        """Test handling with market data provider"""
        message.require = {"market_cap", "pe_ratio"}
        mock_provider.fetch_market_data.return_value = {
            "market_cap": 5013049046812.5,
            "pe_ratio": 20.138,
        }
        
        await market_handler.handle(message)
        
        mock_provider.fetch_market_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_with_empty_require(self, market_handler, message):
        """Test handling when require is empty"""
        message.require = set()
        await market_handler.handle(message)
        # Should not call provider
