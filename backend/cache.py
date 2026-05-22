import os
import time
import logging
from typing import Optional
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicDailyCache")

class InMemoryCache:
    """
    In-memory fallback cache using a simple Python dictionary.
    Supports TTL expiration for leaderboard and daily rotation caching.
    """
    def __init__(self):
        self._store = {}
        self._expires = {}
        logger.info("Initializing LogicDaily In-Memory Fallback Cache")

    def get(self, key: str) -> Optional[str]:
        if key in self._expires:
            expire_at = self._expires[key]
            if expire_at and time.time() > expire_at:
                self.delete(key)
                return None
        return self._store.get(key)

    def set(self, key: str, value: str, expire_seconds: Optional[int] = None):
        self._store[key] = value
        if expire_seconds:
            self._expires[key] = time.time() + expire_seconds
        else:
            self._expires[key] = None

    def delete(self, key: str):
        self._store.pop(key, None)
        self._expires.pop(key, None)

    def flush_all(self):
        self._store.clear()
        self._expires.clear()
        logger.info("In-memory cache flushed.")


class RedisCache:
    """
    Redis production cache wrapper.
    Decoupled from FastAPI direct dependencies for clean testing.
    """
    def __init__(self, redis_client):
        self.client = redis_client
        logger.info("Initializing LogicDaily Redis Production Cache")

    def get(self, key: str) -> Optional[str]:
        try:
            return self.client.get(key)
        except Exception as e:
            logger.warning(f"Redis get failed, returning None: {e}")
            return None

    def set(self, key: str, value: str, expire_seconds: Optional[int] = None):
        try:
            if expire_seconds:
                self.client.set(key, value, ex=expire_seconds)
            else:
                self.client.set(key, value)
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")

    def delete(self, key: str):
        try:
            self.client.delete(key)
        except Exception as e:
            logger.warning(f"Redis delete failed: {e}")

    def flush_all(self):
        try:
            self.client.flushdb()
            logger.info("Redis cache flushed.")
        except Exception as e:
            logger.warning(f"Redis flush failed: {e}")


def get_cache_client():
    """
    Factory function to retrieve the appropriate cache client.
    Attempts to connect to Redis using REDIS_URL first.
    Falls back to InMemoryCache if REDIS_URL is not set or Redis is unreachable.
    """
    import redis

    redis_url = settings.REDIS_URL
    if not redis_url:
        logger.warning("REDIS_URL environment variable is not set. Falling back to In-Memory Cache.")
        return InMemoryCache()

    try:
        # Setup short connection timeout so development doesn't hang if URL is offline
        client = redis.Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
        client.ping()
        logger.info("Successfully connected to Redis cache server!")
        return RedisCache(client)
    except Exception as e:
        logger.error(f"Failed to connect to Redis at {redis_url} ({e}). Falling back to In-Memory Cache.")
        return InMemoryCache()

# Singleton cache instance for simple application-wide access
cache = get_cache_client()

def get_cache():
    """
    FastAPI dependency injection provider for the cache client.
    Allows clean mocking and overriding in test environments.
    """
    return cache
