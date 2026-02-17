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

