"""Tests for SmartCache - Phase 3"""
import pytest
import pandas as pd
from pathlib import Path
import tempfile
import shutil


class TestSmartCache:
    """Test smart cache with range-based reuse"""

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


class TestSmartCacheRangeReuse:
    """Test range-based cache reuse"""

    @pytest.fixture
    def temp_cache_dir(self):
        """Create a temporary cache directory"""
        tmp = tempfile.mkdtemp()
        yield tmp
        shutil.rmtree(tmp)

    @pytest.fixture
    def sample_dataframe(self):
        """Create sample dataframe with year index"""
        return pd.DataFrame(
            {"revenue": [100, 120, 140, 160, 180, 200, 220, 240, 260, 280]},
            index=pd.Index([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024], name="year"),
        )

    def test_range_contains_reuse(self, temp_cache_dir, sample_dataframe):
        """Cached [2015, 2024] should serve query [2020, 2024]"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        # Cache has data for 2015-2024
        cache.set("fin_600519_2015_2024", sample_dataframe)

        # Query for 2020-2024 should reuse cache
        result = cache.get("fin_600519_2020_2024")

        assert result is not None
        assert len(result) == 5
        assert result.index[0] == 2020
        assert result.index[-1] == 2024

    def test_range_subset_reuse(self, temp_cache_dir, sample_dataframe):
        """Cached [2015, 2024] should serve query [2015, 2020]"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        # Cache has data for 2015-2024
        cache.set("fin_600519_2015_2024", sample_dataframe)

        # Query for 2015-2020 should reuse cache
        result = cache.get("fin_600519_2015_2020")

        assert result is not None
        assert len(result) == 6
        assert result.index[0] == 2015
        assert result.index[-1] == 2020

    def test_range_superset_invalidates(self, temp_cache_dir, sample_dataframe):
        """Cached [2015, 2024] should NOT serve query [2010, 2024]"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        # Cache has data for 2015-2024
        cache.set("fin_600519_2015_2024", sample_dataframe)

        # Query for 2010-2024 should invalidate cache
        result = cache.get("fin_600519_2010_2024")

        # Result should be None (cache invalidated)
        assert result is None

    def test_non_overlapping_invalidates(self, temp_cache_dir, sample_dataframe):
        """Non-overlapping ranges should invalidate"""
        from value_investment.data.cache import SmartCache

        cache = SmartCache(cache_dir=temp_cache_dir)

        # Cache has data for 2015-2024
        cache.set("fin_600519_2015_2024", sample_dataframe)

        # Query for 2010-2012 should invalidate
        result = cache.get("fin_600519_2010_2012")

        assert result is None
