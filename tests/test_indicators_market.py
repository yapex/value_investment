"""Tests for market indicators"""
import pandas as pd
import pytest

from value_investment.indicators.market import Market, detect_market, A_SHARE_CODE_PREFIXES


class TestMarket:
    """Test Market enum"""
    
    def test_market_a_value(self):
        """Test Market.A value"""
        assert Market.A.value == 'A股'
    
    def test_market_hk_value(self):
        """Test Market.HK value"""
        assert Market.HK.value == '港股'
    
    def test_market_us_value(self):
        """Test Market.US value"""
        assert Market.US.value == '美股'


class TestDetectMarket:
    """Test detect_market function"""
    
    def test_detect_a_share(self):
        """Test A share detection"""
        assert detect_market('600519') == Market.A
        assert detect_market('000001') == Market.A
        assert detect_market('300001') == Market.A
    
    def test_detect_hk_share(self):
        """Test HK share detection"""
        assert detect_market('00700') == Market.HK
        assert detect_market('09988') == Market.HK
    
    def test_detect_us_share(self):
        """Test US share detection"""
        assert detect_market('AAPL') == Market.US
        assert detect_market('TSLA') == Market.US
    
    def test_a_share_prefixes(self):
        """Test A share code prefixes"""
        assert '6' in A_SHARE_CODE_PREFIXES
        assert '0' in A_SHARE_CODE_PREFIXES
        assert '3' in A_SHARE_CODE_PREFIXES
