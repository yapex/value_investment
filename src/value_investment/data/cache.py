"""Smart cache module with range-based reuse"""
from __future__ import annotations

import pickle
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Tuple

import pandas as pd


@dataclass
class CacheEntry:
    """A cache entry with metadata"""

    data: Any
    range_start: Optional[int] = None
    range_end: Optional[int] = None
    created_at: float = field(default_factory=time.time)
    ttl: int = 86400  # default 1 day

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        return time.time() - self.created_at > self.ttl


class SmartCache:
    """
    Smart cache with range-based reuse

    Rules:
    - Cached [2015, 2024] serves query [2020, 2024] → reuse, slice
    - Cached [2015, 2024] serves query [2010, 2024] → invalidate, re-fetch
    - Cached [2015, 2024] serves query [2015, 2020] → reuse, slice
    """

    def __init__(self, cache_dir: str = "./.cache", default_ttl: int = 86400):
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./.cache")
        self.default_ttl = default_ttl
        self._memory_cache: dict[str, CacheEntry] = {}
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _parse_key(self, key: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Parse cache key to extract range

        Keys like: fin_600519_2015_2024, info_600519
        """
        # Pattern: {type}_{symbol}_{start}_{end}
        match = re.match(r"^.+_(\d{4})_(\d{4})$", key)
        if match:
            return int(match.group(1)), int(match.group(2))
        return None, None

    def _range_contains(self, cached: Tuple[int, int], query: Tuple[int, int]) -> bool:
        """Check if cached range fully contains query range"""
        if cached[0] is None or cached[1] is None:
            return False
        return cached[0] <= query[0] and cached[1] >= query[1]

    def _range_overlaps(self, cached: Tuple[int, int], query: Tuple[int, int]) -> bool:
        """Check if ranges overlap"""
        if cached[0] is None or cached[1] is None:
            return False
        return not (cached[1] < query[0] or cached[0] > query[1])

    def _slice_by_range(self, data: Any, start: int, end: int) -> Any:
        """Slice data by year range"""
        if isinstance(data, pd.DataFrame):
            if "year" in data.index.names:
                return data.loc[start:end]
            # Try to find year column
            if isinstance(data.index, pd.MultiIndex):
                return data.xs(slice(start, end), level="year", drop_level=False)
            # Try column named 'year'
            if "year" in data.columns:
                return data[(data["year"] >= start) & (data["year"] <= end)]
        return data

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        # Check memory cache first
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if not entry.is_expired():
                return entry.data
            else:
                del self._memory_cache[key]

        # Check disk cache
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    entry: CacheEntry = pickle.load(f)
                if not entry.is_expired():
                    self._memory_cache[key] = entry
                    return entry.data
                else:
                    cache_file.unlink()
            except Exception:
                pass

        # Try range-based lookup
        query_start, query_end = self._parse_key(key)
        if query_start is not None and query_end is not None:
            return self._find_and_slice_cached(key, query_start, query_end)

        return None

    def _find_and_slice_cached(self, key: str, query_start: int, query_end: int) -> Optional[Any]:
        """Find a cached entry that can serve the query range"""
        # Check all cached entries
        all_keys = set(self._memory_cache.keys())

        # Also check disk cache
        for cache_file in self.cache_dir.glob("*.pkl"):
            all_keys.add(cache_file.stem)

        for cached_key in all_keys:
            cached_start, cached_end = self._parse_key(cached_key)
            if cached_start is None:
                continue

            # Check if this cached range contains our query
            if self._range_contains((cached_start, cached_end), (query_start, query_end)):
                # Try to get the cached data
                cached_data = None

                # Check memory first
                if cached_key in self._memory_cache:
                    cached_data = self._memory_cache[cached_key].data

                # Check disk
                if cached_data is None:
                    cache_file = self.cache_dir / f"{cached_key}.pkl"
                    if cache_file.exists():
                        try:
                            with open(cache_file, "rb") as f:
                                entry: CacheEntry = pickle.load(f)
                            cached_data = entry.data
                        except Exception:
                            continue

                if cached_data is not None:
                    # Slice the data to the requested range
                    return self._slice_by_range(cached_data, query_start, query_end)

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None, range_start: Optional[int] = None, range_end: Optional[int] = None) -> None:
        """Set value in cache"""
        ttl = ttl or self.default_ttl

        # Parse range from key if not provided
        if range_start is None or range_end is None:
            range_start, range_end = self._parse_key(key)

        entry = CacheEntry(
            data=value,
            range_start=range_start,
            range_end=range_end,
            ttl=ttl,
        )

        # Store in memory
        self._memory_cache[key] = entry

        # Store on disk
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(entry, f)
        except Exception:
            pass

    def invalidate(self, key: str) -> None:
        """Invalidate a cache entry"""
        # Remove from memory
        if key in self._memory_cache:
            del self._memory_cache[key]

        # Remove from disk
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            cache_file.unlink()

        # Also invalidate related range keys
        for cached_key in list(self._memory_cache.keys()):
            if cached_key.startswith(key.rsplit("_", 2)[0]):
                self.invalidate(cached_key)

    def get_or_fetch(
        self,
        key: str,
        query_range: Tuple[int, int],
        fetch_func: Callable,
        ttl: Optional[int] = None,
    ) -> Any:
        """
        Get from cache or fetch if not available

        Args:
            key: Cache key
            query_range: (start_year, end_year)
            fetch_func: Function to fetch data if not cached
            ttl: Optional TTL override
        """
        cached = self.get(key)
        if cached is not None:
            return cached

        # Fetch new data
        data = fetch_func()

        # Store with inferred range
        range_start, range_end = self._parse_key(key)
        if range_start is None:
            range_start = query_range[0]
            range_end = query_range[1]

        self.set(key, data, ttl=ttl, range_start=range_start, range_end=range_end)
        return data
