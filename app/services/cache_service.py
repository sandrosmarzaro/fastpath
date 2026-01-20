from typing import Annotated

from fastapi import Depends

from app.repositories.cache_repository import CacheRepository


class CacheService:
    def __init__(
        self, repository: Annotated[CacheRepository, Depends()]
    ) -> None:
        self.repository = repository

    async def get_value(self, prefix: str, key: str) -> dict | None:
        return await self.repository.get_value(prefix, key)

    async def get_many(self, prefix: str, keys: list[str]) -> dict | None:
        return await self.repository.get_many(prefix, keys)

    async def set_value(
        self, prefix: str, key: str, value: str | bytes | float, ttl: int = 600
    ) -> None:
        await self.repository.set_value(prefix, key, value, ttl)

    async def set_many(
        self, prefix: str, keys: list[str], values: list, ttl: int = 600
    ) -> None:
        await self.repository.set_many(prefix, keys, values, ttl)
