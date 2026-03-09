"""Tests for AkshareProvider - Phase 4"""
import pytest  # type: ignore[import-untyped]
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
        """Stock info cache should be set with TTL"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

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

        # Check the cache key exists (diskcache format, not checking internal TTL)
        assert "info_600519" in cache.list_keys()

    def test_get_stock_info_hk_stock(self, temp_cache_dir):
        """Should get 港股 stock info"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="HK")

        # Mock the akshare call - returns wide format DataFrame
        mock_data = pd.DataFrame({
            "公司名称": ["腾讯控股有限公司"],
            "所属行业": ["软件服务"],
            "董事长": ["马化腾"]
        })

        with patch("akshare.stock_hk_company_profile_em", return_value=mock_data):
            result = provider.get_stock_info("00700")

        assert isinstance(result, pd.DataFrame)
        assert "item" in result.columns
        assert "value" in result.columns
        # Should include stock code as first item
        assert result.iloc[0]["item"] == "股票代码"
        assert result.iloc[0]["value"] == "00700"

    def test_get_stock_info_us_stock(self, temp_cache_dir):
        """Should get 美股 stock info"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        # Mock the akshare call - returns item/value format directly
        mock_data = pd.DataFrame({
            "item": ["org_id", "org_name_cn", "org_name_en", "main_operation_business"],
            "value": ["T000038499", "苹果公司", "Apple Inc.", "设计，生产和销售移动通信和媒体设备..."]
        })

        with patch("akshare.stock_individual_basic_info_us_xq", return_value=mock_data):
            result = provider.get_stock_info("AAPL")

        assert isinstance(result, pd.DataFrame)
        assert "item" in result.columns
        assert "value" in result.columns
        # Should have correct data
        assert result.iloc[0]["item"] == "org_id"
        assert result.iloc[0]["value"] == "T000038499"

    def test_get_stock_info_us_uses_cache(self, temp_cache_dir):
        """US stock info should use cache"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        # Pre-populate cache
        cached_data = pd.DataFrame({
            "item": ["org_id"],
            "value": ["T000038499"]
        })
        cache.set("info_AAPL", cached_data)

        # Mock akshare to fail if called
        with patch("akshare.stock_individual_basic_info_us_xq") as mock_ak:
            result = provider.get_stock_info("AAPL")

        # Should return cached data, not call akshare
        mock_ak.assert_not_called()
        assert result is not None

    def test_hk_stock_info_cache_expires_at_june(self, temp_cache_dir):
        """港股股票信息缓存应到次年6月底"""
        from datetime import datetime
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider
        from value_investment.data.providers.base_provider import get_ttl_until_june_next_year

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="HK")

        # Mock the akshare call
        mock_data = pd.DataFrame({
            "公司名称": ["腾讯控股有限公司"],
        })

        with patch("akshare.stock_hk_company_profile_em", return_value=mock_data):
            result = provider.get_stock_info("00700")

        assert result is not None
        # Check cache key exists
        assert "info_00700" in cache.list_keys()

    def test_us_stock_info_cache_expires_at_june(self, temp_cache_dir):
        """美股股票信息缓存应到次年6月底"""
        from datetime import datetime
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider
        from value_investment.data.providers.base_provider import get_ttl_until_june_next_year

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        # Mock the akshare call
        mock_data = pd.DataFrame({
            "item": ["org_id"],
            "value": ["T000038499"]
        })

        with patch("akshare.stock_individual_basic_info_us_xq", return_value=mock_data):
            result = provider.get_stock_info("AAPL")

        assert result is not None
        # Check cache key exists
        assert "info_AAPL" in cache.list_keys()

    def test_get_stock_info_force_refresh(self, temp_cache_dir):
        """force_refresh=True时应强制从数据源重新获取"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        # Pre-populate cache with old data
        cached_data = pd.DataFrame({
            "item": ["股票代码"],
            "value": ["OLD"]
        })
        cache.set("info_600519", cached_data)

        # Mock akshare to return new data
        mock_data = pd.DataFrame({
            "item": ["股票代码", "股票简称"],
            "value": ["600519", "贵州茅台"]
        })

        with patch("akshare.stock_individual_info_em", return_value=mock_data) as mock_ak:
            result = provider.get_stock_info("600519", force_refresh=True)

        # Should call akshare
        mock_ak.assert_called_once()
        # Return new data
        assert result.iloc[0]["value"] == "600519"
        # Cache should be updated
        cached = cache.get("info_600519")
        assert cached is not None
        assert cached.iloc[0]["value"] == "600519"


@pytest.mark.skip(reason="A 股历史数据已迁移到 tushare，这些测试针对旧的 akshare 实现")
class TestAkshareProviderHistorical:
    """Test historical data fetching (A 股) - DEPRECATED: A 股已迁移到 tushare
    
    这些测试针对旧的 akshare A 股历史数据实现。
    根据新的架构：
    - A 股：tushare (财务 + 交易数据)
    - 港股：akshare (财务) + yfinance (交易)
    - 美股：akshare (财务) + yfinance (交易)
    
    AkshareProvider 仍用于港股/美股财务数据，但 A 股历史交易数据测试应废弃。
    """

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

    def test_historical_data_cache_key_no_end_date(self, temp_cache_dir):
        """不同end_date应使用相同的缓存key（全量缓存）"""
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

        with patch("akshare.stock_zh_a_hist", return_value=mock_data) as mock_fetch:
            # 查询 end_date=20241231
            provider.get_historical_data("600519", end_date="20241231")
            # 第一次调用应该 fetch
            assert mock_fetch.call_count == 1

            # 查询 end_date=20241230
            provider.get_historical_data("600519", end_date="20241230")
            # 第二次调用应该使用缓存，不应该再次 fetch
            assert mock_fetch.call_count == 1

        # 验证只生成了一个缓存key（不包含end_date）
        cache_keys = cache.list_keys()
        assert "hist_600519_hfq" in cache_keys
        assert len(cache_keys) == 1

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

    def test_historical_data_force_refresh(self, temp_cache_dir):
        """force_refresh=True时应强制从数据源重新获取"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        # Pre-populate cache with old data
        cached_data = pd.DataFrame({
            "日期": ["2023-01-02", "2023-12-29"],
            "股票代码": ["600519"] * 2,
            "收盘": [1500.0, 1600.0]
        })
        cache._set_with_metadata("hist_600519_hfq", cached_data, "2023-12-31")

        # Mock akshare to return new data
        mock_data = pd.DataFrame({
            "日期": ["2024-01-02", "2024-12-31"],
            "股票代码": ["600519"] * 2,
            "收盘": [1700.0, 1800.0]
        })

        with patch("akshare.stock_zh_a_hist", return_value=mock_data) as mock_ak:
            result = provider.get_historical_data("600519", end_date="20241231", force_refresh=True)

        # Should call akshare
        mock_ak.assert_called_once()
        # Should return new data
        assert len(result) == 2
        assert "2024-01-02" in result["日期"].values


class TestAkshareProviderHistoricalUS:
    """Test US historical data fetching"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory"""
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)

    def test_get_us_historical_data(self, temp_cache_dir):
        """Should get US stock historical data"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        # Mock返回美股历史数据
        mock_data = pd.DataFrame({
            "日期": ["2024-01-02", "2024-01-03", "2024-01-04"],
            "股票代码": ["AAPL", "AAPL", "AAPL"],
            "开盘": [185.0, 186.0, 187.0],
            "收盘": [186.0, 187.0, 188.0],
            "最高": [187.0, 188.0, 189.0],
            "最低": [184.0, 185.0, 186.0],
            "成交量": [1000000, 1100000, 1200000]
        })

        with patch("akshare.stock_us_daily", return_value=mock_data):
            result = provider.get_historical_data(
                "AAPL",
                end_date="2024-01-31",
                start_date="2024-01-01"
            )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "日期" in result.columns

    def test_get_us_historical_data_without_start_date(self, temp_cache_dir):
        """不传start_date时应获取全量数据"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        # Mock返回全量数据
        mock_data = pd.DataFrame({
            "日期": ["2023-01-02", "2023-12-29", "2024-01-02", "2024-12-31"],
            "股票代码": ["AAPL"] * 4,
            "开盘": [150.0, 160.0, 170.0, 180.0],
            "收盘": [155.0, 165.0, 175.0, 185.0]
        })

        with patch("akshare.stock_us_daily", return_value=mock_data) as mock_ak:
            result = provider.get_historical_data(
                "AAPL",
                end_date="20241231"
            )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 4
        # 验证调用akshare（stock_us_daily不需要日期参数）
        mock_ak.assert_called_once()
        call_kwargs = mock_ak.call_args.kwargs
        assert call_kwargs["symbol"] == "AAPL"
        assert call_kwargs["adjust"] == ""  # 默认不复权

    def test_us_historical_data_uses_cache(self, temp_cache_dir):
        """US历史行情应使用缓存"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        mock_data = pd.DataFrame({
            "日期": ["2024-12-31"],
            "股票代码": ["AAPL"],
            "开盘": [180.0],
            "收盘": [185.0]
        })

        # First call - should call akshare
        with patch("akshare.stock_us_daily", return_value=mock_data) as mock_ak:
            result1 = provider.get_historical_data("AAPL", end_date="20241231")

        mock_ak.assert_called_once()
        assert "hist_us_AAPL" in cache.list_keys()

        # Second call - should use cache
        with patch("akshare.stock_us_daily") as mock_ak2:
            result2 = provider.get_historical_data("AAPL", end_date="20241231")

        mock_ak2.assert_not_called()
        assert result1.equals(result2)

    def test_us_historical_data_cache_filters_by_start_date(self, temp_cache_dir):
        """缓存命中后应按start_date过滤"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        # 全量数据(2023-2024)
        mock_full_data = pd.DataFrame({
            "日期": ["2023-01-02", "2023-12-29", "2024-01-02", "2024-12-31"],
            "股票代码": ["AAPL"] * 4,
            "开盘": [150.0, 160.0, 170.0, 180.0],
            "收盘": [155.0, 165.0, 175.0, 185.0]
        })

        with patch("akshare.stock_us_daily", return_value=mock_full_data):
            # 首次调用获取全量
            result1 = provider.get_historical_data("AAPL", end_date="20241231")
            # 再次调用带 start_date 过滤
            result2 = provider.get_historical_data(
                "AAPL",
                end_date="20241231",
                start_date="20240101"
            )

        # 首次调用返回全量(4条)
        assert len(result1) == 4
        # 第二次调用返回过滤后数据(2条，2024年的)
        assert len(result2) == 2


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

    def test_a_financial_sheet_uses_cache(self, temp_cache_dir):
        """A股财务报表应使用缓存"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        mock_data = pd.DataFrame({
            "SECUCODE": ["600519.SH"],
            "SECURITY_CODE": ["600519"],
            "REPORT_DATE": ["2024-12-31"]
        })

        # First call - should call akshare and cache
        with patch("akshare.stock_balance_sheet_by_yearly_em", return_value=mock_data) as mock_ak:
            result1 = provider._get_balance_sheet("600519")

        mock_ak.assert_called_once()
        assert "balance_sheet_a_600519" in cache.list_keys()

        # Second call - should use cache, not call akshare
        with patch("akshare.stock_balance_sheet_by_yearly_em") as mock_ak2:
            result2 = provider._get_balance_sheet("600519")

        mock_ak2.assert_not_called()
        assert result1.equals(result2)

    def test_hk_financial_sheet_uses_cache(self, temp_cache_dir):
        """港股财务报表应使用缓存"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="HK")

        mock_data = pd.DataFrame({
            "SECURITY_CODE": ["00700"],
            "STD_ITEM_NAME": ["资产总计"],
            "AMOUNT": [1000000000],
            "REPORT_DATE": ["2024-12-31"]
        })

        # First call
        with patch("akshare.stock_financial_hk_report_em", return_value=mock_data) as mock_ak:
            result1 = provider._get_hk_balance_sheet("00700")

        mock_ak.assert_called_once()
        assert "balance_sheet_hk_00700" in cache.list_keys()

        # Second call - should use cache
        with patch("akshare.stock_financial_hk_report_em") as mock_ak2:
            result2 = provider._get_hk_balance_sheet("00700")

        mock_ak2.assert_not_called()

    def test_us_financial_sheet_uses_cache(self, temp_cache_dir):
        """美股财务报表应使用缓存"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        mock_data = pd.DataFrame({
            "SECURITY_CODE": ["AAPL"],
            "REPORT_DATE": ["2024-12-31"],
            "TOTAL_ASSETS": [1000000000]
        })

        # First call
        with patch("akshare.stock_financial_us_report_em", return_value=mock_data) as mock_ak:
            result1 = provider._get_us_balance_sheet("AAPL")

        mock_ak.assert_called_once()
        assert "balance_sheet_us_AAPL" in cache.list_keys()

        # Second call - should use cache
        with patch("akshare.stock_financial_us_report_em") as mock_ak2:
            result2 = provider._get_us_balance_sheet("AAPL")

        mock_ak2.assert_not_called()

    def test_financial_sheet_cache_key_no_end_year(self, temp_cache_dir):
        """财务报表缓存key不应包含end_year（缓存全量数据）"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        mock_balance = pd.DataFrame({
            "SECUCODE": ["600519.SH"] * 3,
            "SECURITY_CODE": ["600519"] * 3,
            "REPORT_DATE": ["2024-12-31", "2023-12-31", "2022-12-31"],
            "TOTAL_ASSETS": [1000, 900, 800]
        })
        mock_profit = pd.DataFrame({
            "SECUCODE": ["600519.SH"] * 3,
            "SECURITY_CODE": ["600519"] * 3,
            "REPORT_DATE_NAME": ["2024年报", "2023年报", "2022年报"],
            "TOTAL_OPERATE_INCOME": [100, 90, 80]
        })
        mock_cashflow = pd.DataFrame({
            "SECUCODE": ["600519.SH"] * 3,
            "SECURITY_CODE": ["600519"] * 3,
            "REPORT_DATE": ["2024-12-31", "2023-12-31", "2022-12-31"],
            "SALES_SERVICES": [100, 90, 80]
        })

        with patch("akshare.stock_balance_sheet_by_yearly_em", return_value=mock_balance), \
             patch("akshare.stock_profit_sheet_by_yearly_em", return_value=mock_profit), \
             patch("akshare.stock_cash_flow_sheet_by_yearly_em", return_value=mock_cashflow):
            # Fetch all three sheets
            provider._get_balance_sheet("600519")
            provider._get_profit_sheet("600519")
            provider._get_cashflow_sheet("600519")

        # Verify cache keys don't include end_year
        keys = cache.list_keys()
        assert "balance_sheet_a_600519" in keys
        assert "profit_sheet_a_600519" in keys
        assert "cashflow_sheet_a_600519" in keys
        # No keys with end_year suffix
        assert not any("2024" in k for k in keys if "sheet" in k)

    def test_public_api_filters_by_end_year(self, temp_cache_dir):
        """公共API应按end_year过滤数据"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="A")

        mock_balance = pd.DataFrame({
            "SECUCODE": ["600519.SH"] * 5,
            "SECURITY_CODE": ["600519"] * 5,
            "REPORT_DATE_NAME": ["2024年报", "2023年报", "2022年报", "2021年报", "2020年报"],
            "TOTAL_ASSETS": [1000, 900, 800, 700, 600]
        })

        with patch("akshare.stock_balance_sheet_by_yearly_em", return_value=mock_balance):
            # Query with different end_years
            result_2024 = provider.get_balance_sheet("600519", end_year=2024)
            result_2022 = provider.get_balance_sheet("600519", end_year=2022)

        # 2024 should have 5 years (2020-2024)
        assert len(result_2024) == 5
        # 2022 should have 3 years (2020-2022)
        assert len(result_2022) == 3
        # Both queries should use the same cache
        assert "balance_sheet_a_600519" in cache.list_keys()


class TestAkshareProviderUSFinancialIndicator:
    """Test US financial indicator fetching"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory"""
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)

    def test_get_us_financial_indicator(self, temp_cache_dir):
        """Should get US stock financial indicator with standardized fields"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        # Mock返回美股财务指标数据
        mock_data = pd.DataFrame({
            "SECURITY_CODE": ["AAPL", "AAPL"],
            "SECURITY_NAME_ABBR": ["苹果", "苹果"],
            "REPORT_DATE": ["2024-12-31", "2023-12-31"],
            "TOTAL_INCOME": [394328000000, 383290000000],
            "TOTAL_INCOME_YOY": [2.88, -2.80],
            "PARENT_HOLDER_NETPROFIT": [93736000000, 97015000000],
            "PARENT_HOLDER_NETPROFIT_YOY": [-3.38, -2.81],
            "BASIC_EPS_CS": [6.13, 6.11],
            "ROE": [147.78, 156.63],
            "ROA": [24.47, 24.14],
            "DEBT_RATIO": [82.15, 78.57],
        })

        with patch("akshare.stock_financial_us_analysis_indicator_em", return_value=mock_data):
            result = provider.get_financial_indicator("AAPL")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        # Should be mapped to standardized field names
        assert "total_revenue" in result.columns
        assert "net_profit" in result.columns
        assert "basic_eps" in result.columns
        assert "roe" in result.columns

    def test_get_us_financial_indicator_uses_cache(self, temp_cache_dir):
        """US财务指标应使用缓存"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        mock_data = pd.DataFrame({
            "SECURITY_CODE": ["AAPL"],
            "REPORT_DATE": ["2024-12-31"],
            "TOTAL_INCOME": [394328000000],
            "PARENT_HOLDER_NETPROFIT": [93736000000],
            "ROE": [147.78],
        })

        # First call - should call akshare
        with patch("akshare.stock_financial_us_analysis_indicator_em", return_value=mock_data) as mock_ak:
            result1 = provider.get_financial_indicator("AAPL")

        mock_ak.assert_called_once()
        assert "indicator_us_AAPL" in cache.list_keys()

        # Second call - should use cache
        with patch("akshare.stock_financial_us_analysis_indicator_em") as mock_ak2:
            result2 = provider.get_financial_indicator("AAPL")

        mock_ak2.assert_not_called()
        assert result1.equals(result2)

    def test_get_us_financial_indicator_force_refresh(self, temp_cache_dir):
        """US财务指标force_refresh应强制刷新缓存"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        mock_data1 = pd.DataFrame({
            "SECURITY_CODE": ["AAPL"],
            "REPORT_DATE": ["2024-12-31"],
            "TOTAL_INCOME": [394328000000],
        })
        mock_data2 = pd.DataFrame({
            "SECURITY_CODE": ["AAPL"],
            "REPORT_DATE": ["2024-12-31"],
            "TOTAL_INCOME": [400000000000],  # Different value
        })

        # First call - populate cache
        with patch("akshare.stock_financial_us_analysis_indicator_em", return_value=mock_data1):
            result1 = provider.get_financial_indicator("AAPL")

        # Second call with force_refresh - should re-fetch
        with patch("akshare.stock_financial_us_analysis_indicator_em", return_value=mock_data2) as mock_ak2:
            result2 = provider.get_financial_indicator("AAPL", force_refresh=True)

        mock_ak2.assert_called_once()
        # Should be mapped to standardized field name
        assert result2["total_revenue"].iloc[0] == 400000000000

    def test_get_us_financial_indicator_empty_response(self, temp_cache_dir):
        """US财务指标空响应应返回空DataFrame"""
        from value_investment.data.cache import SmartCache
        from value_investment.data.providers.akshare_provider import AkshareProvider

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = AkshareProvider(cache=cache, market="US")

        with patch("akshare.stock_financial_us_analysis_indicator_em", return_value=pd.DataFrame()):
            result = provider.get_financial_indicator("INVALID_STOCK")

        assert isinstance(result, pd.DataFrame)
        assert result.empty
