"""Tests for SmartCache - simplified with diskcache"""
import pytest
import pandas as pd
import tempfile
import shutil
import time


class TestSmartCache:
    """Test smart cache basic operations"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory"""
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)

    def test_cache_initialization(self, temp_cache_dir):
        """Cache should initialize with directory"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir, default_ttl=3600)
        assert str(cache.cache_dir) == temp_cache_dir
        assert cache.default_ttl == 3600

    def test_set_and_get_basic(self, temp_cache_dir):
        """Should set and get basic values"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)
        cache.set("test_key", {"data": "value"})
        result = cache.get("test_key")
        assert result == {"data": "value"}

    def test_get_nonexistent(self, temp_cache_dir):
        """Should return None for nonexistent keys"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)
        result = cache.get("nonexistent")
        assert result is None

    def test_invalidate(self, temp_cache_dir):
        """Should invalidate cache entry"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)
        cache.set("test_key", {"data": "value"})
        cache.invalidate("test_key")
        result = cache.get("test_key")
        assert result is None

    def test_list_keys(self, temp_cache_dir):
        """Should list all cached keys"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        keys = cache.list_keys()
        assert "key1" in keys
        assert "key2" in keys

    def test_persistence_after_restart(self, temp_cache_dir):
        """Should persist data to disk and survive restart"""
        from value_investment.data.cache import SmartCache

        # First instance: set value
        cache1 = SmartCache(cache_dir=temp_cache_dir)
        cache1.set("persist_key", {"data": "persisted"})

        # Second instance: should get value from disk
        cache2 = SmartCache(cache_dir=temp_cache_dir)
        result = cache2.get("persist_key")
        assert result == {"data": "persisted"}

    def test_ttl_expiration(self, temp_cache_dir):
        """Should expire after TTL"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir, default_ttl=1)
        cache.set("ttl_key", "value")

        # Immediately should exist
        assert cache.get("ttl_key") == "value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("ttl_key") is None

    def test_set_with_ttl(self, temp_cache_dir):
        """Should respect TTL passed to set()"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir, default_ttl=3600)
        cache.set("custom_ttl", "value", ttl=1)

        # Immediately should exist
        assert cache.get("custom_ttl") == "value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("custom_ttl") is None

    def test_cache_dataframe(self, temp_cache_dir):
        """Should cache pandas DataFrame"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        cache.set("dataframe", df)

        result = cache.get("dataframe")
        assert isinstance(result, pd.DataFrame)
        assert result.equals(df)

    def test_get_or_fetch_cache_hit(self, temp_cache_dir):
        """get_or_fetch应返回缓存数据，不调用fetch_func"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        # Pre-populate cache
        cached_data = {"key": "cached_value"}
        cache.set("test_key", cached_data)

        # fetch_func should not be called
        call_count = [0]

        def fetch_func():
            call_count[0] += 1
            return {"key": "new_value"}

        result = cache.get_or_fetch("test_key", fetch_func)

        assert result == cached_data
        assert call_count[0] == 0  # fetch_func was not called

    def test_get_or_fetch_cache_miss(self, temp_cache_dir):
        """get_or_fetch应调用fetch_func并缓存结果"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        fetched_data = {"key": "fetched_value"}
        call_count = [0]

        def fetch_func():
            call_count[0] += 1
            return fetched_data

        result = cache.get_or_fetch("test_key", fetch_func)

        assert result == fetched_data
        assert call_count[0] == 1  # fetch_func was called once
        assert "test_key" in cache.list_keys()

    def test_get_or_fetch_second_call_uses_cache(self, temp_cache_dir):
        """get_or_fetch第二次调用应使用缓存"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        call_count = [0]

        def fetch_func():
            call_count[0] += 1
            return {"key": f"value_{call_count[0]}"}

        # First call - should fetch
        result1 = cache.get_or_fetch("test_key", fetch_func)
        assert call_count[0] == 1

        # Second call - should use cache
        result2 = cache.get_or_fetch("test_key", fetch_func)
        assert call_count[0] == 1  # Still 1, not incremented
        assert result1 == result2

    def test_get_or_fetch_with_ttl(self, temp_cache_dir):
        """get_or_fetch应支持TTL参数"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        def fetch_func():
            return "value"

        cache.get_or_fetch("ttl_key", fetch_func, ttl=1)

        # Immediately should exist
        assert cache.get("ttl_key") == "value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired
        assert cache.get("ttl_key") is None


class TestSmartCacheRangeFilter:
    """Test date range filtering in cache"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory"""
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)

    def test_filter_by_date_range_basic(self, temp_cache_dir):
        """测试基础日期过滤"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)
        df = pd.DataFrame({
            "日期": ["2024-01-01", "2024-06-15", "2024-12-31", "2025-01-01"]
        })

        result = cache._filter_by_date_range(df, "日期", "2024-06-01", "2024-12-31")
        assert len(result) == 2
        assert result["日期"].iloc[0] == "2024-06-15"

    def test_filter_by_date_range_only_start(self, temp_cache_dir):
        """测试只有start_date"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)
        df = pd.DataFrame({"日期": ["2024-01-01", "2024-06-15", "2025-01-01"]})

        result = cache._filter_by_date_range(df, "日期", "2024-06-01", None)
        assert len(result) == 2

    def test_filter_by_date_range_only_end(self, temp_cache_dir):
        """测试只有end_date"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)
        df = pd.DataFrame({"日期": ["2024-01-01", "2024-06-15", "2025-01-01"]})

        result = cache._filter_by_date_range(df, "日期", None, "2024-06-30")
        assert len(result) == 2

    def test_get_or_fetch_with_range_cache_hit(self, temp_cache_dir):
        """测试缓存命中时过滤"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        # 模拟已缓存的数据
        cached_data = pd.DataFrame({
            "日期": ["2024-01-01", "2024-06-15", "2024-12-31"]
        })
        cache.set("hist_test_hfq", cached_data)

        result = cache.get_or_fetch_with_range(
            key="hist_test_hfq",
            date_column="日期",
            fetch_func=lambda: pd.DataFrame({"日期": []}),
            start_date="2024-06-01",
            end_date="2024-12-31"
        )

        assert len(result) == 2
        assert result["日期"].iloc[0] == "2024-06-15"

    def test_get_or_fetch_with_range_cache_miss(self, temp_cache_dir):
        """测试缓存未命中时获取并过滤"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        def fetch():
            return pd.DataFrame({
                "日期": ["2024-01-01", "2024-06-15", "2024-12-31"]
            })

        result = cache.get_or_fetch_with_range(
            key="hist_test2_hfq",
            date_column="日期",
            fetch_func=fetch,
            start_date="2024-06-01",
            end_date="2024-12-31"
        )

        assert len(result) == 2
        # 验证缓存中存的是全量（带元数据的结构化数据）
        cached = cache.get("hist_test2_hfq")
        assert isinstance(cached, dict)
        assert len(cached["data"]) == 3

    def test_get_or_fetch_without_range(self, temp_cache_dir):
        """测试 get_or_fetch 复用 get_or_fetch_with_range（无需过滤）"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        def fetch():
            return {"key": "value", "data": [1, 2, 3]}

        result = cache.get_or_fetch(
            key="test_key",
            fetch_func=fetch,
            ttl=3600
        )

        assert result == {"key": "value", "data": [1, 2, 3]}
        # 验证缓存中存的是全量
        cached = cache.get("test_key")
        assert cached == {"key": "value", "data": [1, 2, 3]}

    def test_smart_cache_subset_query_uses_cache(self, temp_cache_dir):
        """子集查询（end_date <= 缓存end_date）应使用缓存并过滤"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        call_count = [0]

        def fetch_full():
            call_count[0] += 1
            return pd.DataFrame({
                "日期": ["2024-01-01", "2024-06-15", "2024-12-31"]
            })

        # 第一次查询：end_date=2024-12-31
        result1 = cache.get_or_fetch_with_range(
            key="hist_smart_hfq",
            date_column="日期",
            fetch_func=fetch_full,
            start_date=None,
            end_date="2024-12-31"
        )
        assert call_count[0] == 1
        assert len(result1) == 3

        # 第二次查询：end_date=2024-06-30（子集）
        result2 = cache.get_or_fetch_with_range(
            key="hist_smart_hfq",
            date_column="日期",
            fetch_func=fetch_full,
            start_date=None,
            end_date="2024-06-30"
        )
        # 应该使用缓存，不应再次fetch
        assert call_count[0] == 1
        assert len(result2) == 2

    def test_smart_cache_larger_range_triggers_refetch(self, temp_cache_dir):
        """更大范围查询（end_date > 缓存end_date）应重新获取并覆盖缓存"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        call_count = [0]

        def fetch_v1():
            call_count[0] += 1
            return pd.DataFrame({
                "日期": ["2024-01-01", "2024-06-15", "2024-12-31"]
            })

        def fetch_v2():
            call_count[0] += 1
            return pd.DataFrame({
                "日期": ["2024-01-01", "2024-06-15", "2024-12-31", "2025-01-01"]
            })

        # 第一次查询：end_date=2024-06-30
        result1 = cache.get_or_fetch_with_range(
            key="hist_smart2_hfq",
            date_column="日期",
            fetch_func=fetch_v1,
            start_date=None,
            end_date="2024-06-30"
        )
        assert call_count[0] == 1
        assert len(result1) == 2

        # 第二次查询：end_date=2024-12-31（更大范围）
        result2 = cache.get_or_fetch_with_range(
            key="hist_smart2_hfq",
            date_column="日期",
            fetch_func=fetch_v2,
            start_date=None,
            end_date="2024-12-31"
        )
        # 应该重新fetch
        assert call_count[0] == 2
        assert len(result2) == 3

        # 验证缓存已更新为新数据
        cached = cache.get("hist_smart2_hfq")
        assert len(cached["data"]) == 4

    def test_smart_cache_stores_end_date_metadata(self, temp_cache_dir):
        """缓存应存储cached_end_date元数据"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        def fetch():
            return pd.DataFrame({
                "日期": ["2024-01-01", "2024-06-15", "2024-12-31"]
            })

        cache.get_or_fetch_with_range(
            key="hist_meta_hfq",
            date_column="日期",
            fetch_func=fetch,
            start_date=None,
            end_date="2024-12-31"
        )

        # 验证缓存中存储了元数据
        cached = cache.get("hist_meta_hfq")
        assert isinstance(cached, dict)
        assert "_cached_end_date" in cached
        assert cached["_cached_end_date"] == "2024-12-31"
        assert len(cached["data"]) == 3

