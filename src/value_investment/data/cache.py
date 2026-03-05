"""Smart cache module using diskcache"""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import diskcache
import pandas as pd


class SmartCache:
    """
    Simple cache wrapper around diskcache

    Features:
    - Disk-backed persistent cache
    - TTL support
    - LRU eviction
    """

    def __init__(self, cache_dir: str = "./.cache", default_ttl: int = 86400):
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./.cache")
        self.default_ttl = default_ttl
        self._cache = diskcache.Cache(str(self.cache_dir))

    def get(self, key: str) -> Any | None:
        """Get value from cache"""
        try:
            return self._cache.get(key)
        except KeyError:
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache with optional TTL"""
        ttl = ttl if ttl is not None else self.default_ttl
        self._cache.set(key, value, expire=ttl)

    def get_or_fetch(
        self,
        key: str,
        fetch_func: Callable[[], Any],
        ttl: int | None = None,
        force_refresh: bool = False,
    ) -> Any:
        """
        Get from cache or fetch and cache if not present.

        This method is now a wrapper around get_or_fetch_with_range for backward compatibility.

        Args:
            key: Cache key
            fetch_func: Function to fetch data if not cached
            ttl: Time to live in seconds (optional)
            force_refresh: If True, invalidate cache and fetch fresh data

        Returns:
            Cached or freshly fetched data
        """
        # Force refresh: invalidate cache first
        if force_refresh:
            self.invalidate(key)

        return self.get_or_fetch_with_range(
            key=key,
            date_column=None,  # 无需过滤
            fetch_func=fetch_func,
            start_date=None,
            end_date=None,
            ttl=ttl,
        )

    def _filter_by_date_range(
        self,
        df: pd.DataFrame,
        date_column: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        """
        Filter DataFrame by date range.

        Args:
            df: DataFrame to filter
            date_column: Name of the date column
            start_date: Start date (inclusive), format: YYYY-MM-DD
            end_date: End date (inclusive), format: YYYY-MM-DD

        Returns:
            Filtered DataFrame
        """
        if df.empty or date_column not in df.columns:
            return df

        # Convert date column to datetime for comparison
        df_copy = df.copy()
        df_copy["_date_temp"] = pd.to_datetime(df_copy[date_column])

        # Apply start_date filter
        if start_date:
            start_dt = pd.to_datetime(start_date)
            df_copy = df_copy[df_copy["_date_temp"] >= start_dt]

        # Apply end_date filter
        if end_date:
            end_dt = pd.to_datetime(end_date)
            df_copy = df_copy[df_copy["_date_temp"] <= end_dt]

        # Remove temporary column
        df_copy = df_copy.drop(columns=["_date_temp"])

        return df_copy

    def get_or_fetch_with_range(
        self,
        key: str,
        date_column: str | None,
        fetch_func: Callable[[], Any],
        start_date: str | None = None,
        end_date: str | None = None,
        ttl: int | None = None,
        force_refresh: bool = False,
    ) -> Any:
        """
        Get from cache or fetch and cache if not present, with intelligent date range handling.

        缓存策略：
        1. 缓存存储：end_date及之前的全量数据 + cached_end_date元数据
        2. 子集查询（end_date <= 缓存end_date）：使用缓存并过滤
        3. 更大范围查询（end_date > 缓存end_date）：重新获取并覆盖缓存
        4. TTL作为保底过期时间

        Args:
            key: Cache key
            date_column: Name of the date column to filter on (optional)
            fetch_func: Function to fetch data if not cached
            start_date: Start date for filtering (inclusive), format: YYYY-MM-DD
            end_date: End date for filtering (inclusive), format: YYYY-MM-DD
            ttl: Time to live in seconds (optional, used as fallback expiration)
            force_refresh: If True, invalidate cache and fetch fresh data

        Returns:
            Cached or freshly fetched data (filtered if date_column provided)
        """
        # Force refresh: invalidate cache first
        if force_refresh:
            self.invalidate(key)
        # If no date filtering needed, use simple path
        if date_column is None:
            cached = self.get(key)
            if cached is not None:
                return cached

            data = fetch_func()
            self.set(key, data, ttl=ttl)
            return data

        # With date filtering - check if we need to re-fetch
        cached_entry = self.get(key)

        if cached_entry is not None:
            # Check if cached data is a structured entry with metadata
            if isinstance(cached_entry, dict) and "_cached_end_date" in cached_entry:
                cached_end_date = cached_entry["_cached_end_date"]
                cached_data = cached_entry["data"]

                # Compare dates
                if end_date and cached_end_date:
                    query_end_dt = pd.to_datetime(end_date)
                    cached_end_dt = pd.to_datetime(cached_end_date)

                    if query_end_dt > cached_end_dt:
                        # Query range is larger - need to re-fetch
                        data = fetch_func()
                        # Store with new end_date metadata
                        self._set_with_metadata(key, data, end_date, ttl)
                        return self._filter_by_date_range(
                            data, date_column, start_date, end_date
                        )

                # Query end_date <= cached end_date - use cache and filter
                return self._filter_by_date_range(
                    cached_data, date_column, start_date, end_date
                )
            elif isinstance(cached_entry, pd.DataFrame):
                # Legacy format: plain DataFrame, use as-is with filtering
                return self._filter_by_date_range(
                    cached_entry, date_column, start_date, end_date
                )
            else:
                # Non-DataFrame data: return as-is
                return cached_entry

        # Cache miss: fetch full data
        data = fetch_func()

        # Store with end_date metadata
        self._set_with_metadata(key, data, end_date, ttl)

        # Return filtered data
        return self._filter_by_date_range(
            data, date_column, start_date, end_date
        )

    def _set_with_metadata(
        self,
        key: str,
        data: Any,
        end_date: str | None,
        ttl: int | None = None,
    ) -> None:
        """
        Store data with end_date metadata.

        Args:
            key: Cache key
            data: Data to cache
            end_date: The end_date used for this cache entry
            ttl: Time to live in seconds
        """
        if isinstance(data, pd.DataFrame) and end_date:
            # Store with metadata for smart cache invalidation
            entry = {
                "data": data,
                "_cached_end_date": end_date,
            }
            self.set(key, entry, ttl=ttl)
        else:
            # Non-DataFrame or no end_date: store as-is
            self.set(key, data, ttl=ttl)

    def invalidate(self, key: str) -> None:
        """Invalidate a cache entry"""
        try:
            del self._cache[key]
        except KeyError:
            pass

    def list_keys(self) -> list[str]:
        """List all cached keys"""
        return list(self._cache.iterkeys())

    def close(self) -> None:
        """Close the cache"""
        self._cache.close()
