"""Smart cache module using diskcache"""
from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional

import diskcache


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

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            return self._cache.get(key)
        except KeyError:
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL"""
        ttl = ttl if ttl is not None else self.default_ttl
        self._cache.set(key, value, expire=ttl)

    def invalidate(self, key: str) -> None:
        """Invalidate a cache entry"""
        try:
            del self._cache[key]
        except KeyError:
            pass

    def list_keys(self) -> List[str]:
        """List all cached keys"""
        return list(self._cache.iterkeys())

    def close(self) -> None:
        """Close the cache"""
        self._cache.close()
