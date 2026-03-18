"""Unit tests for TushareProvider (no API token required)"""

import pytest  # type: ignore
import pandas as pd
from unittest.mock import Mock, MagicMock, patch

from value_investment.data.providers.tushare_provider import TushareProvider


class MockCache:
    """Mock cache for testing"""

    def __init__(self):
        self._data = {}
        self.get_call_count = 0
        self.set_call_count = 0

    def get(self, key):
        self.get_call_count += 1
        return self._data.get(key)

    def set(self, key, value, ttl=None):
        self.set_call_count += 1
        self._data[key] = value

    def invalidate(self, key):
        if key in self._data:
            del self._data[key]

    def get_or_fetch_with_range(
        self,
        key,
        date_column,
        fetch_func,
        start_date=None,
        end_date=None,
        ttl=None,
        force_refresh=False,
    ):
        """Mock implementation of SmartCache.get_or_fetch_with_range"""
        if force_refresh:
            self.invalidate(key)

        cached = self.get(key)
        if cached is not None:
            # 模拟 SmartCache 的行为
            if isinstance(cached, dict) and "data" in cached:
                data = cached["data"]
            else:
                data = cached
            # 如果有日期过滤，应用过滤
            if date_column and isinstance(data, pd.DataFrame) and not data.empty:
                data = self._filter_by_date(data, date_column, start_date, end_date)
            return data

        # 缓存未命中，调用 fetch_func
        data = fetch_func()
        # 存储带元数据的缓存
        if isinstance(data, pd.DataFrame) and not data.empty and end_date:
            self.set(key, {"data": data, "_cached_end_date": end_date}, ttl=ttl)
        else:
            self.set(key, data, ttl=ttl)
        # 如果有日期过滤，应用过滤
        if date_column and isinstance(data, pd.DataFrame) and not data.empty:
            data = self._filter_by_date(data, date_column, start_date, end_date)
        return data

    def _filter_by_date(self, df, date_column, start_date, end_date):
        """模拟 SmartCache 的日期过滤"""
        if df.empty or date_column not in df.columns:
            return df
        df_copy = df.copy()
        df_copy["_date_temp"] = pd.to_datetime(df_copy[date_column])
        if start_date:
            start_dt = pd.to_datetime(start_date)
            df_copy = df_copy[df_copy["_date_temp"] >= start_dt]
        if end_date:
            end_dt = pd.to_datetime(end_date)
            df_copy = df_copy[df_copy["_date_temp"] <= end_dt]
        return df_copy.drop(columns=["_date_temp"])


class TestTushareProviderUnit:
    """Unit tests without API calls"""

    def test_init_without_token_raises(self):
        """Should raise error if token not provided"""
        with pytest.raises(ValueError, match="Tushare token is required"):
            TushareProvider(cache=MockCache(), token="")

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_init_with_token(self, mock_ts):
        """Should initialize with token"""
        mock_api = Mock()
        mock_ts.pro_api.return_value = mock_api
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        mock_ts.set_token.assert_called_once_with("test_token")
        mock_ts.pro_api.assert_called_once()
        assert provider._api == mock_api

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_field_mapping_stored(self, mock_ts):
        """Should store field mappings"""
        mock_ts.pro_api.return_value = Mock()
        
        mappings = {
            "balance": {"ts_code": "stock_code"},
            "income": {"total_revenue": "total_revenue"},
        }
        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings=mappings
        )
        
        assert provider.get_field_mapping("balance") == {"ts_code": "stock_code"}
        assert provider.get_field_mapping("income") == {"total_revenue": "total_revenue"}
        assert provider.get_field_mapping("unknown") == {}

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_apply_mapping_integration(self, mock_ts):
        """Should apply field mapping to data"""
        mock_ts.pro_api.return_value = Mock()
        
        mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
                "total_assets": "total_assets",
            }
        }
        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings=mappings
        )
        
        # Create mock data
        df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "end_date": ["2023-12-31"],
            "total_assets": [1000],
            "other_field": [999],
        })
        
        result = provider._apply_mapping(df, "balance")
        assert result is not None
        
        # Check mapping applied
        assert "stock_code" in result.columns
        assert "report_date" in result.columns
        assert "total_assets" in result.columns
        assert "other_field" in result.columns  # Unmapped fields kept
        assert "ts_code" not in result.columns
        assert "end_date" not in result.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cache_key_generation(self, mock_ts):
        """Should generate cache keys correctly"""
        mock_ts.pro_api.return_value = Mock()
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        key1 = provider._get_cache_key("balance", "000001.SZ", "2023")
        assert key1 == "balance:000001.SZ:2023"
        
        key2 = provider._get_cache_key("income", "600519.SH", "2023")
        assert key2 == "income:600519.SH:2023"

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cache_integration(self, mock_ts):
        """Should use cache"""
        mock_ts.pro_api.return_value = Mock()
        cache = MockCache()
        provider = TushareProvider(cache=cache, token="test_token")
        
        # Store in cache
        cache.set("test_key", pd.DataFrame({"data": [1]}))
        
        # Retrieve from cache
        result = provider._get_from_cache("test_key")
        assert result is not None
        assert len(result) == 1
        
        # Cache get was called
        assert cache.get_call_count == 1

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cache_set(self, mock_ts):
        """Should set cache"""
        mock_ts.pro_api.return_value = Mock()
        cache = MockCache()
        provider = TushareProvider(cache=cache, token="test_token")
        
        df = pd.DataFrame({"data": [1, 2, 3]})
        provider._set_to_cache("my_key", df)
        
        assert cache.set_call_count == 1
        assert "my_key" in cache._data

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_get_balance_sheet_with_mock(self, mock_ts):
        """Should fetch and map balance sheet data"""
        # Mock API response
        mock_api = Mock()
        mock_df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "end_date": ["2023-12-31"],
            "ann_date": ["20240330"],
            "update_flag": [1],
            "total_assets": [1000],
        })
        mock_api.balancesheet.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api

        mappings = {
            "balance": {
                "ts_code": "stock_code",
                "end_date": "report_date",
            }
        }
        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings=mappings
        )

        df = provider.get_balance_sheet("000001.SZ", 2023)

        # Verify API was called
        mock_api.balancesheet.assert_called_once()

        # Verify mapping applied
        assert "stock_code" in df.columns
        assert "report_date" in df.columns
        assert "ts_code" not in df.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_get_income_statement_with_mock(self, mock_ts):
        """Should fetch and map income statement data"""
        mock_api = Mock()
        mock_df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "end_date": ["2023-12-31"],
            "ann_date": ["20240330"],
            "update_flag": [1],
            "total_revenue": [1000],
            "net_profit": [100],
        })
        mock_api.income.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api

        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings={"income": {"ts_code": "stock_code", "end_date": "report_date"}}
        )

        df = provider.get_income_statement("000001.SZ", 2023)

        mock_api.income.assert_called_once()
        assert "stock_code" in df.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_get_cash_flow_with_mock(self, mock_ts):
        """Should fetch and map cash flow data"""
        mock_api = Mock()
        mock_df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "end_date": ["2023-12-31"],
            "ann_date": ["20240330"],
            "update_flag": [1],
            "operating_cash_flow": [500],
        })
        mock_api.cashflow.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api

        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings={"cashflow": {"ts_code": "stock_code", "end_date": "report_date"}}
        )

        df = provider.get_cash_flow_statement("000001.SZ", 2023)

        mock_api.cashflow.assert_called_once()
        assert "stock_code" in df.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_get_historical_data_with_mock(self, mock_ts):
        """Should fetch and map historical data using pro_bar"""
        mock_api = Mock()
        mock_df = pd.DataFrame({
            "trade_date": ["20231231"],
            "close": [10.5],
            "open": [10.0],
            "vol": [1000],
        })
        # pro_bar 返回 DataFrame
        mock_ts.pro_bar.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api

        provider = TushareProvider(
            cache=MockCache(),
            token="test_token",
            field_mappings={"market": {"close": "close"}}
        )

        df = provider.get_historical_data(
            "000001.SZ",
            start_date="20230101",
            end_date="20231231",
            adjust="qfq"
        )

        # 验证 pro_bar 被调用
        mock_ts.pro_bar.assert_called_once()
        call_args = mock_ts.pro_bar.call_args
        assert call_args[1]["ts_code"] == "000001.SZ"
        assert call_args[1]["adj"] == "qfq"
        # daily 不应该被调用
        mock_api.daily.assert_not_called()

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_get_stock_info_with_mock(self, mock_ts):
        """Should fetch stock info"""
        mock_api = Mock()
        mock_df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "name": ["平安银行"],
            "area": ["深圳"],
        })
        mock_api.stock_basic.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        df = provider.get_stock_info("000001.SZ")
        
        mock_api.stock_basic.assert_called_once()
        assert "name" in df.columns

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_empty_result_handling(self, mock_ts):
        """Should handle empty results"""
        mock_api = Mock()
        mock_api.balancesheet.return_value = pd.DataFrame()
        mock_ts.pro_api.return_value = mock_api
        
        provider = TushareProvider(cache=MockCache(), token="test_token")
        
        df = provider.get_balance_sheet("INVALID.SZ", 2023)
        
        assert df.empty

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cache_hit(self, mock_ts):
        """Should use cached data on cache hit"""
        mock_api = Mock()
        mock_df = pd.DataFrame({
            "ts_code": ["000001.SZ"],
            "end_date": ["2023-12-31"],
            "ann_date": ["20240330"],
            "update_flag": [1],
        })
        mock_api.balancesheet.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api

        cache = MockCache()
        provider = TushareProvider(
            cache=cache,
            token="test_token",
            field_mappings={"balance": {"ts_code": "stock_code", "end_date": "report_date"}}
        )

        # First call - cache miss
        df1 = provider.get_balance_sheet("000001.SZ", 2023)
        assert mock_api.balancesheet.call_count == 1

        # Second call - cache hit
        df2 = provider.get_balance_sheet("000001.SZ", 2023)
        # Should not call API again
        assert mock_api.balancesheet.call_count == 1


class TestTushareProviderSmartCacheStrategy:
    """测试 TushareProvider 的智能缓存策略

    核心原则：
    1. 缓存键不含年份范围（只有 balance:stock_code）
    2. 缓存存储10年全量数据
    3. 查询时按 start_year/end_year 过滤
    4. 不同年份范围的查询复用同一个缓存
    """

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory"""
        import tempfile
        import shutil
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cache_key_should_not_include_years(self, mock_ts, temp_cache_dir):
        """缓存键不应包含年份范围

        当前实现: balance:600519.SH:2015:2024 (失败)
        期望实现: balance:600519.SH (通过)
        """
        from value_investment.data.cache import SmartCache

        mock_api = Mock()
        mock_ts.pro_api.return_value = mock_api

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = TushareProvider(cache=cache, token="test_token")

        # 获取缓存键（模拟内部调用）
        key = provider._get_cache_key("balance", "600519.SH")

        # 缓存键不应包含年份
        assert key == "balance:600519.SH", f"缓存键应不含年份，实际: {key}"

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_different_year_ranges_should_reuse_cache(self, mock_ts, temp_cache_dir):
        """不同年份范围的查询应复用同一个缓存

        查询1: get_balance_sheet("600519", end_year=2024, start_year=2020)
        查询2: get_balance_sheet("600519", end_year=2024, start_year=2015)
        应该只调用一次 API，第二次使用缓存
        """
        from value_investment.data.cache import SmartCache

        mock_api = Mock()
        # 模拟10年数据（使用映射后的字段名 report_date）
        mock_df = pd.DataFrame({
            "ts_code": ["600519.SH"] * 10,
            "report_date": [f"{year}-12-31" for year in range(2015, 2025)],
            "ann_date": [f"{year}0331" for year in range(2015, 2025)],
            "total_assets": list(range(1000, 2000, 100)),
            "update_flag": [1] * 10,
        })
        mock_api.balancesheet.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = TushareProvider(cache=cache, token="test_token")

        # 第一次查询: 2020-2024 (5年)
        df1 = provider.get_balance_sheet("600519", end_year=2024, start_year=2020)
        assert mock_api.balancesheet.call_count == 1, "第一次应调用 API"

        # 第二次查询: 2015-2024 (10年) - 应使用缓存
        df2 = provider.get_balance_sheet("600519", end_year=2024, start_year=2015)
        assert mock_api.balancesheet.call_count == 1, "第二次应使用缓存，不调用 API"

        # 第三次查询: 2018-2022 (5年) - 应使用缓存并过滤
        df3 = provider.get_balance_sheet("600519", end_year=2022, start_year=2018)
        assert mock_api.balancesheet.call_count == 1, "第三次应使用缓存，不调用 API"

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_result_should_filter_by_year_range(self, mock_ts, temp_cache_dir):
        """查询结果应按 start_year/end_year 过滤

        缓存: 2015-2024 (10年)
        查询: start_year=2020, end_year=2023
        期望: 返回 2020-2023 (4年)
        """
        from value_investment.data.cache import SmartCache

        mock_api = Mock()
        # 模拟10年数据（使用映射后的字段名 report_date）
        mock_df = pd.DataFrame({
            "ts_code": ["600519.SH"] * 10,
            "report_date": [f"{year}-12-31" for year in range(2015, 2025)],
            "ann_date": [f"{year}0331" for year in range(2015, 2025)],
            "total_assets": list(range(1000, 2000, 100)),
            "update_flag": [1] * 10,
        })
        mock_api.balancesheet.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = TushareProvider(cache=cache, token="test_token")

        # 查询 2020-2023 (4年)
        df = provider.get_balance_sheet("600519", end_year=2023, start_year=2020)

        # 应该只返回 2020-2023 的数据 (4条)
        assert len(df) == 4, f"期望 4 条记录，实际: {len(df)}"

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_fetch_should_get_10_years_by_default(self, mock_ts, temp_cache_dir):
        """默认应获取10年数据

        查询: get_balance_sheet("600519", end_year=2024)
        期望: 获取 2015-2024 (10年)
        """
        from value_investment.data.cache import SmartCache

        mock_api = Mock()
        mock_df = pd.DataFrame({
            "ts_code": ["600519.SH"],
            "report_date": ["2024-12-31"],
            "ann_date": ["20250331"],
            "total_assets": [1000],
            "update_flag": [1],
        })
        mock_api.balancesheet.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = TushareProvider(cache=cache, token="test_token")

        # 不指定 start_year
        provider.get_balance_sheet("600519", end_year=2024)

        # 验证 API 调用参数
        call_args = mock_api.balancesheet.call_args
        assert call_args is not None
        # start_date 应该是 10 年前 (2015-01-01)
        start_date = call_args[1]["start_date"]
        assert start_date == "20150101", f"期望 start_date=20150101，实际: {start_date}"

    @patch('value_investment.data.providers.tushare_provider.ts')
    def test_cache_stores_full_data_with_metadata(self, mock_ts, temp_cache_dir):
        """缓存应存储全量数据 + end_date 元数据

        SmartCache._set_with_metadata() 应该被调用，
        存储结构: {"data": DataFrame, "_cached_end_date": "2024-12-31"}
        """
        from value_investment.data.cache import SmartCache

        mock_api = Mock()
        # 模拟10年数据（使用映射后的字段名 report_date）
        mock_df = pd.DataFrame({
            "ts_code": ["600519.SH"] * 10,
            "report_date": [f"{year}-12-31" for year in range(2015, 2025)],
            "ann_date": [f"{year}0331" for year in range(2015, 2025)],
            "total_assets": list(range(1000, 2000, 100)),
            "update_flag": [1] * 10,
        })
        mock_api.balancesheet.return_value = mock_df
        mock_ts.pro_api.return_value = mock_api

        cache = SmartCache(cache_dir=temp_cache_dir)
        provider = TushareProvider(cache=cache, token="test_token")

        # 第一次查询
        provider.get_balance_sheet("600519", end_year=2024)

        # 检查缓存内容（缓存键是 balance:600519，不含 .SH 后缀）
        cached = cache.get("balance:600519")
        assert cached is not None, f"缓存应该存在，实际缓存键: {cache.list_keys()}"
        assert isinstance(cached, dict), "缓存应该是带元数据的字典"
        assert "data" in cached, "缓存应包含 data 字段"
        assert "_cached_end_date" in cached, "缓存应包含 _cached_end_date 字段"
        assert len(cached["data"]) == 10, f"缓存应包含 10 年数据，实际: {len(cached['data'])}"
