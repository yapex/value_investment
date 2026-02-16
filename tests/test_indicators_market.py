"""Tests for market module"""
import pytest
from enum import Enum


class TestMarketEnum:
    """Test Market enum values"""

    def test_market_enum_has_abc(self):
        """Market enum should have A股 value"""
        from value_investment.indicators.market import Market
        assert hasattr(Market, "A")

    def test_market_enum_has_hk(self):
        """Market enum should have 港股 value"""
        from value_investment.indicators.market import Market
        assert hasattr(Market, "HK")

    def test_market_enum_has_us(self):
        """Market enum should have 美股 value"""
        from value_investment.indicators.market import Market
        assert hasattr(Market, "US")


class TestDetectMarket:
    """Test market detection function"""

    def test_detect_abc_stock_code(self):
        """Should detect A股 market from 6-digit stock code"""
        from value_investment.indicators.market import detect_market
        assert detect_market("600519") == "A股"
        assert detect_market("000001") == "A股"
        assert detect_market("300750") == "A股"

    def test_detect_hk_stock_code(self):
        """Should detect HK market from 5-digit stock code"""
        from value_investment.indicators.market import detect_market
        assert detect_market("00700") == "港股"
        assert detect_market("09988") == "港股"

    def test_detect_us_stock_code(self):
        """Should detect US market from ticker symbol"""
        from value_investment.indicators.market import detect_market
        assert detect_market("AAPL") == "美股"
        assert detect_market("MSFT") == "美股"

    def test_detect_hk_with_prefix(self):
        """Should handle HK prefix like 0"""
        from value_investment.indicators.market import detect_market
        assert detect_market("00005") == "港股"
        assert detect_market("03690") == "港股"

    def test_detect_invalid_code(self):
        """Should return None for invalid stock codes"""
        from value_investment.indicators.market import detect_market
        assert detect_market("") is None
        assert detect_market("123") is None  # Too short
        assert detect_market("600") is None  # Too short
