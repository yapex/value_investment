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
