"""Tests for AkshareProvider - Phase 4"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil


class TestAkshareProviderStockInfo:
    """Test stock info fetching"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory"""
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)

    def test_provider_initialization(self, temp_cache_dir):
        """Provider should initialize with cache"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        assert provider._cache is cache
        assert provider._market == "A"

    def test_get_stock_info_a_stock(self, temp_cache_dir):
        """Should get A股 stock info"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        # Mock the akshare call
        mock_data = pd.DataFrame({
            "item": ["股票代码", "股票简称", "总股本"],
            "value": ["600519", "贵州茅台", 1252270215.0]
        })

        with patch("akshare.stock_individual_info_em", return_value=mock_data):
            result = provider.get_stock_info("600519")

        assert isinstance(result, pd.DataFrame)
        assert "item" in result.columns
        assert "value" in result.columns

    def test_get_stock_info_uses_cache(self, temp_cache_dir):
        """Should use cache for stock info"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        # Pre-populate cache
        cached_data = pd.DataFrame({
            "item": ["股票代码"],
            "value": ["600519"]
        })
        cache.set("info_600519", cached_data)

        # Mock akshare to fail if called
        with patch("akshare.stock_individual_info_em") as mock_ak:
            result = provider.get_stock_info("600519")

        # Should return cached data, not call akshare
        mock_ak.assert_not_called()
        assert result is not None

    def test_stock_info_cache_expires_at_next_midnight(self, temp_cache_dir):
        """Stock info cache should expire at next midnight, not fixed TTL"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider
        from datetime import datetime, timedelta
        from pathlib import Path

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        # Mock akshare to return data
        mock_data = pd.DataFrame({
            "item": ["股票代码", "股票简称"],
            "value": ["600519", "贵州茅台"]
        })

        with patch("akshare.stock_individual_info_em", return_value=mock_data):
            result = provider.get_stock_info("600519")

        assert result is not None

        # Check the cache entry's TTL - should be until next midnight
        cache_key = "info_600519"
        cache_file = Path(temp_cache_dir) / f"{cache_key}.pkl"

        import pickle
        with open(cache_file, "rb") as f:
            entry = pickle.load(f)

        # TTL should be less than a full day (86400) and should expire at next midnight
        # At any time of day, TTL should be between 1 second and 86399 seconds
        assert entry.ttl > 0, "TTL should be positive"
        assert entry.ttl < 86400, "TTL should be less than 24 hours (next midnight)"

        # TTL should be approximately time until midnight (±1 second tolerance)
        now = datetime.now()
        tomorrow_midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        expected_ttl = int((tomorrow_midnight - now).total_seconds())

        assert abs(entry.ttl - expected_ttl) <= 1, (
            f"TTL {entry.ttl} should be within 1 second of time until midnight {expected_ttl}"
        )


class TestAkshareProviderHistorical:
    """Test historical data fetching"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory"""
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)

    def test_get_historical_data(self, temp_cache_dir):
        """Should get historical data"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        mock_data = pd.DataFrame({
            "日期": ["2024-01-02", "2024-01-03"],
            "股票代码": ["600519", "600519"],
            "开盘": [1715.0, 1681.11],
            "收盘": [1685.01, 1694.0]
        })

        with patch("akshare.stock_zh_a_hist", return_value=mock_data):
            result = provider.get_historical_data(
                "600519",
                start_date="20240101",
                end_date="20240131"
            )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2


class TestAkshareProviderFinancial:
    """Test financial data fetching"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory"""
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)

    def test_get_balance_sheet(self, temp_cache_dir):
        """Should get balance sheet data"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        mock_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"],
            "SECURITY_CODE": ["600519"],
            "REPORT_DATE": ["2024-12-31"]
        })

        with patch("akshare.stock_balance_sheet_by_yearly_em", return_value=mock_data):
            result = provider._get_balance_sheet("600519")

        assert isinstance(result, pd.DataFrame)

    def test_get_profit_sheet(self, temp_cache_dir):
        """Should get profit sheet data"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        mock_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"],
            "SECURITY_CODE": ["600519"],
            "TOTAL_OPERATE_INCOME": [1000000000]
        })

        with patch("akshare.stock_profit_sheet_by_yearly_em", return_value=mock_data):
            result = provider._get_profit_sheet("600519")

        assert isinstance(result, pd.DataFrame)

    def test_get_cashflow_sheet(self, temp_cache_dir):
        """Should get cashflow sheet data"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        mock_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"],
            "SECURITY_CODE": ["600519"],
            "SALES_SERVICES": [1200000000]
        })

        with patch("akshare.stock_cash_flow_sheet_by_yearly_em", return_value=mock_data):
            result = provider._get_cashflow_sheet("600519")

        assert isinstance(result, pd.DataFrame)
