"""
Shared Cache Layer
=================
Provides caching mechanisms for parsed scripts, analysis results,
and pattern lookups across all MCP servers to improve performance.
"""

import time
import hashlib
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from threading import Lock


class CacheEntry:
    """Represents a single cache entry with expiry."""

    def __init__(self, key: str, value: Any, ttl_seconds: int = 300):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
        self.access_count = 0

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds

    @property
    def age_seconds(self) -> float:
        return time.time() - self.created_at

    def access(self):
        """Record an access to this cache entry."""
        self.access_count += 1


class AnalysisCache:
    """
    Thread-safe cache for analysis results with TTL-based expiry.
    Automatically evicts old entries when cache is full.
    """

    def __init__(self, max_entries: int = 100, default_ttl: int = 300):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_entries = max_entries
        self._default_ttl = default_ttl
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired:
                del self._cache[key]
                return None

            entry.access()
            return entry.value

    def set(self, key: str, value: Any, ttl: int = None):
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: class default_ttl)
        """
        with self._lock:
            # Evict if full
            if len(self._cache) >= self._max_entries:
                self._evict_oldest()

            self._cache[key] = CacheEntry(
                key, value, ttl or self._default_ttl
            )

    def make_key(self, *args, **kwargs) -> str:
        """
        Create a deterministic cache key from arguments.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            SHA256 hash as cache key
        """
        content = str(args) + str(sorted(kwargs.items()))
        return hashlib.sha256(content.encode()).hexdigest()

    def invalidate(self, key: str):
        """Remove a specific key from cache."""
        with self._lock:
            self._cache.pop(key, None)

    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()

    def _evict_oldest(self):
        """Evict the oldest entry when cache is full."""
        if not self._cache:
            return

        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]

    @property
    def size(self) -> int:
        return len(self._cache)

    @property
    def stats(self) -> Dict:
        with self._lock:
            total_access = sum(e.access_count for e in self._cache.values())
            expired = sum(1 for e in self._cache.values() if e.is_expired)
            return {
                'size': len(self._cache),
                'max_entries': self._max_entries,
                'total_accesses': total_access,
                'expired_count': expired,
                'default_ttl': self._default_ttl
            }


# Global cache instances
_script_cache = None
_analysis_cache = None
_pattern_cache = None


def get_script_cache() -> AnalysisCache:
    """Get or create the global script cache."""
    global _script_cache
    if _script_cache is None:
        _script_cache = AnalysisCache(max_entries=50, default_ttl=600)
    return _script_cache


def get_analysis_cache() -> AnalysisCache:
    """Get or create the global analysis cache."""
    global _analysis_cache
    if _analysis_cache is None:
        _analysis_cache = AnalysisCache(max_entries=50, default_ttl=300)
    return _analysis_cache


def get_pattern_cache() -> AnalysisCache:
    """Get or create the global pattern cache."""
    global _pattern_cache
    if _pattern_cache is None:
        _pattern_cache = AnalysisCache(max_entries=20, default_ttl=900)
    return _pattern_cache