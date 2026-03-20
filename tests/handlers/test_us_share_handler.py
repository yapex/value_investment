"""Comprehensive tests for US Share Handlers"""
import pytest
from unittest.mock import MagicMock
import pandas as pd

from value_investment.handlers.us_share import (
    USShareStatementHandler,
    USShareIndicatorHandler,
    USShareMarketHandler,
    US_SHARE_STATEMENT_FIELDS,
    US_SHARE_INDICATOR_FIELDS,
    US_SHARE_MARKET_FIELDS,
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
    """Create USShareStatementHandler with mock provider"""
    return USShareStatementHandler(provider=mock_provider)


@pytest.fixture
def indicator_handler(mock_provider):
    """Create USShareIndicatorHandler with mock provider"""
    return USShareIndicatorHandler(provider=mock_provider)


@pytest.fixture
def market_handler(mock_provider):
    """Create USShareMarketHandler with mock provider"""
    return USShareMarketHandler(provider=mock_provider)


@pytest.fixture
def message():
    """Create a test message"""
    return Message(
        symbol="AAPL",
        market="美股",
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
        """US_SHARE_STATEMENT_FIELDS should be a set"""
        assert isinstance(US_SHARE_STATEMENT_FIELDS, set)

    def test_statement_fields_contains_core(self):
        """Should contain core financial fields"""
        assert "total_revenue" in US_SHARE_STATEMENT_FIELDS
        assert "net_profit" in US_SHARE_STATEMENT_FIELDS
        assert "total_assets" in US_SHARE_STATEMENT_FIELDS

    def test_indicator_fields_is_set(self):
        """US_SHARE_INDICATOR_FIELDS should be a set"""
        assert isinstance(US_SHARE_INDICATOR_FIELDS, set)

    def test_indicator_fields_contains_core(self):
        """Should contain core indicator fields"""
        assert "roe" in US_SHARE_INDICATOR_FIELDS
        assert "roa" in US_SHARE_INDICATOR_FIELDS
        assert "gross_margin" in US_SHARE_INDICATOR_FIELDS

    def test_market_fields_is_set(self):
        """US_SHARE_MARKET_FIELDS should be a set"""
        assert isinstance(US_SHARE_MARKET_FIELDS, set)

    def test_market_fields_contains_core(self):
        """Should contain core market fields"""
        assert "market_cap" in US_SHARE_MARKET_FIELDS
        assert "pe_ratio" in US_SHARE_MARKET_FIELDS
        assert "pb_ratio" in US_SHARE_MARKET_FIELDS


# ============================================================================
# Test Statement Handler
# ============================================================================

class TestStatementHandler:
    """Test USShareStatementHandler"""

    def test_handler_properties(self, statement_handler):
        """Test handler target_market"""
        assert statement_handler.target_market == "美股"

    def test_handler_with_provider(self, mock_provider):
        """Test handler initialization with provider"""
        handler = USShareStatementHandler(provider=mock_provider)
        assert handler._provider is not None

    def test_handler_without_provider(self):
        """Test handler initialization without provider"""
        handler = USShareStatementHandler(provider=None)
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
        handler = USShareStatementHandler(provider=None)
        await handler.handle(message)
        # Should not modify message when no provider

    def test_add_results_from_df(self, statement_handler, message):
        """Test _add_results_from_df method"""
        df = pd.DataFrame({
            "year": [2024, 2023],
            "total_revenue": [100000000000, 90000000000],
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


# ============================================================================
# Test Indicator Handler
# ============================================================================

class TestIndicatorHandler:
    """Test USShareIndicatorHandler"""

    def test_handler_properties(self, indicator_handler):
        """Test handler target_market"""
        assert indicator_handler.target_market == "美股"

    def test_handler_with_provider(self, mock_provider):
        """Test handler initialization with provider"""
        handler = USShareIndicatorHandler(provider=mock_provider)
        assert handler._provider is not None

    @pytest.mark.asyncio
    async def test_handle_with_indicators(self, indicator_handler, mock_provider, message):
        """Test handling with indicator provider"""
        message.require = {"roe", "roa"}
        mock_provider.fetch_indicators.return_value = {
            "roe": {2024: 25.0},
            "roa": {2024: 15.0},
        }
        
        await indicator_handler.handle(message)
        
        mock_provider.fetch_indicators.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_with_empty_require(self, indicator_handler, message):
        """Test handling when require is empty"""
        message.require = set()
        await indicator_handler.handle(message)


# ============================================================================
# Test Market Handler
# ============================================================================

class TestMarketHandler:
    """Test USShareMarketHandler"""

    def test_handler_properties(self, market_handler):
        """Test handler target_market"""
        assert market_handler.target_market == "美股"

    def test_handler_with_provider(self, mock_provider):
        """Test handler initialization with provider"""
        handler = USShareMarketHandler(provider=mock_provider)
        assert handler._provider is not None

    @pytest.mark.asyncio
    async def test_handle_with_market_data(self, market_handler, mock_provider, message):
        """Test handling with market data provider"""
        message.require = {"market_cap", "pe_ratio"}
        mock_provider.fetch_market_data.return_value = {
            "market_cap": 3000000000000,
            "pe_ratio": 30.0,
        }
        
        await market_handler.handle(message)
        
        mock_provider.fetch_market_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_with_empty_require(self, market_handler, message):
        """Test handling when require is empty"""
        message.require = set()
        await market_handler.handle(message)
