"""Test API market routing functionality

Tests that ValueInvestment API correctly routes to different providers
based on market parameter (A/HK/US).
"""

import pytest
from unittest.mock import MagicMock, patch

from value_investment.api import ValueInvestment


class TestMarketRouting:
    """Test market routing in ValueInvestment API"""

    def test_a_share_uses_tushare_provider(self):
        """A 股初始化应使用 tushare provider
        
        When market='A':
        - Financial provider should be tushare_a
        - Market provider should be tushare_a
        """
        api = ValueInvestment(market="A")
        
        # Verify financial provider is tushare
        assert api._financial_provider is not None
        assert api._financial_provider.__class__.__name__ == "TushareProvider"
        
        # Verify market provider is also tushare
        assert api._market_provider is not None
        assert api._market_provider.__class__.__name__ == "TushareProvider"

    def test_hk_share_uses_akshare_yfinance_providers(self):
        """港股初始化应使用 akshare (financial) + yfinance (market)
        
        When market='HK':
        - Financial provider should be akshare
        - Market provider should be yfinance
        """
        api = ValueInvestment(market="HK")
        
        # Verify financial provider is akshare
        assert api._financial_provider is not None
        assert api._financial_provider.__class__.__name__ == "AkshareProvider"
        
        # Verify market provider is yfinance
        assert api._market_provider is not None
        assert api._market_provider.__class__.__name__ == "YFinanceProvider"

    def test_us_share_uses_akshare_yfinance_providers(self):
        """美股初始化应使用 akshare (financial) + yfinance (market)
        
        When market='US':
        - Financial provider should be akshare
        - Market provider should be yfinance
        """
        api = ValueInvestment(market="US")
        
        # Verify financial provider is akshare
        assert api._financial_provider is not None
        assert api._financial_provider.__class__.__name__ == "AkshareProvider"
        
        # Verify market provider is yfinance
        assert api._market_provider is not None
        assert api._market_provider.__class__.__name__ == "YFinanceProvider"


class TestMarketDetection:
    """Test market detection from stock codes"""

    def test_detect_a_share_from_code(self):
        """应从股票代码自动检测 A 股市场
        
        A 股代码特征：
        - 6 位数字
        - 0/3/6 开头
        """
        # 6 开头 - 上海主板
        assert ValueInvestment.detect_market("600519") == "A"  # 茅台
        assert ValueInvestment.detect_market("000001") == "A"  # 平安银行
        assert ValueInvestment.detect_market("300750") == "A"  # 宁德时代

    def test_detect_hk_share_from_code(self):
        """应从股票代码自动检测港股市场
        
        港股代码特征：
        - 5 位数字
        """
        assert ValueInvestment.detect_market("00700") == "HK"  # 腾讯
        assert ValueInvestment.detect_market("09988") == "HK"  # 阿里巴巴
        assert ValueInvestment.detect_market("01810") == "HK"  # 小米

    def test_detect_us_share_from_code(self):
        """应从股票代码自动检测美股市场
        
        美股代码特征：
        - 字母代码
        """
        assert ValueInvestment.detect_market("AAPL") == "US"  # 苹果
        assert ValueInvestment.detect_market("TSLA") == "US"  # 特斯拉
        assert ValueInvestment.detect_market("MSFT") == "US"  # 微软


class TestCrossMarketDataFetching:
    """Test cross-market data fetching capabilities"""

    def test_multiple_market_instances_independent(self):
        """不同市场的 API 实例应相互独立
        
        创建多个不同市场的 API 实例时：
        - 每个实例应有独立的 provider
        - 不应相互干扰
        """
        # 创建三个不同市场的实例
        api_a = ValueInvestment(market="A")
        api_hk = ValueInvestment(market="HK")
        api_us = ValueInvestment(market="US")
        
        # 验证 A 股实例使用 tushare
        assert api_a._financial_provider.__class__.__name__ == "TushareProvider"
        assert api_a._market_provider.__class__.__name__ == "TushareProvider"
        
        # 验证港股实例使用 akshare + yfinance
        assert api_hk._financial_provider.__class__.__name__ == "AkshareProvider"
        assert api_hk._market_provider.__class__.__name__ == "YFinanceProvider"
        
        # 验证美股实例使用 akshare + yfinance
        assert api_us._financial_provider.__class__.__name__ == "AkshareProvider"
        assert api_us._market_provider.__class__.__name__ == "YFinanceProvider"
        
        # 验证实例之间独立
        assert api_a._financial_provider is not api_hk._financial_provider
        assert api_hk._financial_provider is not api_us._financial_provider

    def test_get_market_method(self):
        """get_market() 方法应正确返回市场代码"""
        api = ValueInvestment(market="A")
        
        # 显式指定的市场
        assert api.get_market() == "A"
        
        # 从 symbol 自动检测
        assert api.get_market("600519") == "A"
        assert api.get_market("00700") == "HK"
        assert api.get_market("AAPL") == "US"
