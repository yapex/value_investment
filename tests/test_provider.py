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

        # 使用YYYY-MM-DD格式(akshare返回的格式)
        mock_data = pd.DataFrame({
            "日期": ["2024-01-02", "2024-01-03"],
            "股票代码": ["600519", "600519"],
            "开盘": [1715.0, 1681.11],
            "收盘": [1685.01, 1694.0]
        })

        with patch("akshare.stock_zh_a_hist", return_value=mock_data):
            result = provider.get_historical_data(
                "600519",
                end_date="2024-01-31",
                start_date="2024-01-01"
            )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_get_historical_data_without_start_date_returns_all(self, temp_cache_dir):
        """不传start_date时应获取全量数据"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        # Mock返回全量数据(2023-2024)
        mock_data = pd.DataFrame({
            "日期": ["2023-01-02", "2023-12-29", "2024-01-02", "2024-12-31"],
            "股票代码": ["600519"] * 4,
            "开盘": [1500.0, 1600.0, 1700.0, 1800.0],
            "收盘": [1550.0, 1650.0, 1750.0, 1850.0]
        })

        with patch("akshare.stock_zh_a_hist", return_value=mock_data) as mock_ak:
            result = provider.get_historical_data(
                "600519",
                end_date="20241231"
            )

        # 验证返回了全量数据
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        # 验证调用akshare时使用19700101作为start_date
        mock_ak.assert_called_once()
        call_kwargs = mock_ak.call_args.kwargs
        assert call_kwargs["start_date"] == "19700101"
        assert call_kwargs["end_date"] == "20241231"

    def test_historical_data_cache_key_includes_end_date(self, temp_cache_dir):
        """不同end_date应生成不同的缓存key"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        mock_data = pd.DataFrame({
            "日期": ["2024-12-31"],
            "股票代码": ["600519"],
            "开盘": [1800.0],
            "收盘": [1850.0]
        })

        with patch("akshare.stock_zh_a_hist", return_value=mock_data):
            # 查询 end_date=20241231
            provider.get_historical_data("600519", end_date="20241231")
            # 查询 end_date=20241230
            provider.get_historical_data("600519", end_date="20241230")

        # 验证生成了两个不同的缓存key
        cache_keys = list(cache._memory_cache.keys())
        assert "hist_600519_20241231_hfq" in cache_keys
        assert "hist_600519_20241230_hfq" in cache_keys

    def test_historical_data_cache_filters_by_start_date(self, temp_cache_dir):
        """缓存命中后应按start_date过滤"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        # 全量数据(2023-2024)
        mock_full_data = pd.DataFrame({
            "日期": ["2023-01-02", "2023-12-29", "2024-01-02", "2024-12-31"],
            "股票代码": ["600519"] * 4,
            "开盘": [1500.0, 1600.0, 1700.0, 1800.0],
            "收盘": [1550.0, 1650.0, 1750.0, 1850.0]
        })

        with patch("akshare.stock_zh_a_hist", return_value=mock_full_data):
            # 首次调用 get_historical_data("600519", end_date="20241231") 获取全量
            result1 = provider.get_historical_data("600519", end_date="20241231")
            # 再次调用带 start_date 过滤
            result2 = provider.get_historical_data(
                "600519",
                end_date="20241231",
                start_date="20240101"
            )

        # 首次调用返回全量(4条)
        assert len(result1) == 4
        # 第二次调用返回过滤后数据(2条，2024年的)
        assert len(result2) == 2
        # 验证数据被正确过滤
        assert all(result2["日期"] >= "2024")


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


class TestFinancialDataCache:
    """Test financial data merged cache functionality"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory"""
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)

    def test_get_financial_data_without_start_year_returns_all(
        self, temp_cache_dir
    ):
        """不传start_year时应获取全量数据"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import (
            AkshareProvider,
            _get_ttl_until_june_next_year,
        )

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        # Mock data with multiple years
        balance_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"] * 3,
            "SECURITY_CODE": ["600519"] * 3,
            "REPORT_DATE": ["2024-12-31", "2023-12-31", "2022-12-31"],
            "TOTAL_ASSETS": [1000, 900, 800],
        })
        income_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"] * 3,
            "SECURITY_CODE": ["600519"] * 3,
            "REPORT_DATE": ["2024-12-31", "2023-12-31", "2022-12-31"],
            "TOTAL_OPERATE_INCOME": [100, 90, 80],
        })
        cashflow_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"] * 3,
            "SECURITY_CODE": ["600519"] * 3,
            "REPORT_DATE": ["2024-12-31", "2023-12-31", "2022-12-31"],
            "SALES_SERVICES": [100, 90, 80],
        })

        with patch(
            "akshare.stock_balance_sheet_by_yearly_em",
            return_value=balance_data,
        ), patch(
            "akshare.stock_profit_sheet_by_yearly_em",
            return_value=income_data,
        ), patch(
            "akshare.stock_cash_flow_sheet_by_yearly_em",
            return_value=cashflow_data,
        ):
            # Call without end_year - should return all data
            result = provider.get_financial_data("600519", start_year=0)

        # Should have 3 years of data
        assert len(result) == 3

    def test_financial_data_cache_key_includes_end_year(self, temp_cache_dir):
        """不同end_year应生成不同的缓存key"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        # Mock data with multiple years
        balance_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"] * 3,
            "SECURITY_CODE": ["600519"] * 3,
            "REPORT_DATE": ["2024-12-31", "2023-12-31", "2022-12-31"],
            "TOTAL_ASSETS": [1000, 900, 800],
        })
        income_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"] * 3,
            "SECURITY_CODE": ["600519"] * 3,
            "REPORT_DATE": ["2024-12-31", "2023-12-31", "2022-12-31"],
            "TOTAL_OPERATE_INCOME": [100, 90, 80],
        })
        cashflow_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"] * 3,
            "SECURITY_CODE": ["600519"] * 3,
            "REPORT_DATE": ["2024-12-31", "2023-12-31", "2022-12-31"],
            "SALES_SERVICES": [100, 90, 80],
        })

        with patch(
            "akshare.stock_balance_sheet_by_yearly_em",
            return_value=balance_data,
        ), patch(
            "akshare.stock_profit_sheet_by_yearly_em",
            return_value=income_data,
        ), patch(
            "akshare.stock_cash_flow_sheet_by_yearly_em",
            return_value=cashflow_data,
        ):
            # Query with start_year=2020, end_year=2024
            provider.get_financial_data("600519", start_year=2020, end_year=2024)
            # Query with start_year=2020, end_year=2023
            provider.get_financial_data("600519", start_year=2020, end_year=2023)

        # Check that both cache keys exist
        assert cache._memory_cache.get("financial_600519_2024") is not None
        assert cache._memory_cache.get("financial_600519_2023") is not None

    def test_financial_data_cache_ttl_until_june(self, temp_cache_dir):
        """缓存TTL应到次年6月底"""
        from datetime import datetime
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import (
            AkshareProvider,
            _get_ttl_until_june_next_year,
        )

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        # Mock data
        balance_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"],
            "SECURITY_CODE": ["600519"],
            "REPORT_DATE": ["2024-12-31"],
            "TOTAL_ASSETS": [1000],
        })
        income_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"],
            "SECURITY_CODE": ["600519"],
            "REPORT_DATE": ["2024-12-31"],
            "TOTAL_OPERATE_INCOME": [100],
        })
        cashflow_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"],
            "SECURITY_CODE": ["600519"],
            "REPORT_DATE": ["2024-12-31"],
            "SALES_SERVICES": [100],
        })

        with patch(
            "akshare.stock_balance_sheet_by_yearly_em",
            return_value=balance_data,
        ), patch(
            "akshare.stock_profit_sheet_by_yearly_em",
            return_value=income_data,
        ), patch(
            "akshare.stock_cash_flow_sheet_by_yearly_em",
            return_value=cashflow_data,
        ):
            provider.get_financial_data("600519", start_year=2020, end_year=2024)

        # Check TTL is approximately correct
        expected_ttl = _get_ttl_until_june_next_year(2024)
        june_next_year = datetime(datetime.now().year + 1, 6, 30, 23, 59, 59)
        expected_seconds = int((june_next_year - datetime.now()).total_seconds())

        # Allow some tolerance (within 60 seconds)
        assert abs(expected_ttl - expected_seconds) < 60
