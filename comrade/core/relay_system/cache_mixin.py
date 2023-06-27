from collections import Counter, OrderedDict
from typing import Any


class RelayCacheMixin:
    # in-memory cache
    local_cache: OrderedDict[str, dict[str, Any]] = OrderedDict()
    cache_max_size: int = 1024  # maximum number of blobs to store in the cache

    cache_stats: Counter[str] = Counter()

    def get_cached_blob(self, source_url: str) -> dict[str, Any] | None:
        """
        Get a blob document from the in-memory cache
        (if it exists)

        Parameters
        ----------
        source_url : str
            The source URL of the blob
        """
        self.cache_stats["get"] += 1

        doc = self.local_cache.get(source_url)
        if doc is not None:
            self.cache_stats["hit"] += 1
            return doc
        self.cache_stats["miss"] += 1
        return None

    def cache_blob(self, blob: dict[str, Any]) -> None:
        """
        Cache a blob document

        Parameters
        ----------
        blob : dict
            The blob document to cache
        """
        self.local_cache[blob["_id"]] = blob
        if len(self.local_cache) > self.cache_max_size:
            self.local_cache.popitem(last=False)

    def uncache_blob(self, source_url: str) -> None:
        """
        Remove a blob document from the cache

        Parameters
        ----------
        source_url : str
            The source URL of the blob
        """
        self.local_cache.pop(source_url, None)
