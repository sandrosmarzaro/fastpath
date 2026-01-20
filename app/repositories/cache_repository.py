from json import loads
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.core.cache_manager import get_cache_client


class CacheRepository:
    def __init__(
        self, cache_client: Annotated[Redis, Depends(get_cache_client)]
    ) -> None:
        self.cache_client = cache_client

    def _make_key(self, prefix: str, key: str) -> str:
        return f'{prefix}:{key}'

    async def get_value(self, prefix: str, key: str) -> dict | None:
        cache_key = self._make_key(prefix, key)
        value = await self.cache_client.get(cache_key)
        if value is None:
            return None
        return loads(value)

    async def get_many(self, prefix: str, keys: list[str]) -> dict | None:
        cache_keys = [self._make_key(prefix, key) for key in keys]
        values = await self.cache_client.mget(cache_keys)

        return {
            key: loads(value)
            for key, value in zip(keys, values, strict=False)
            if value is not None
        }

    async def set_value(
        self,
        prefix: str,
        key: str,
        value: str | bytes | float,
        ttl: int = 600,
    ) -> None:
        cache_key = self._make_key(prefix, key)
        await self.cache_client.setex(cache_key, ttl, value)

    async def set_many(
        self,
        prefix: str,
        keys: list[str],
        values: list,
        ttl: int = 600,
    ) -> None:
        pipe = self.cache_client.pipeline()
        for key, value in zip(keys, values, strict=False):
            cache_key = self._make_key(prefix, key)
            pipe.setex(cache_key, ttl, value)
        await pipe.execute()
