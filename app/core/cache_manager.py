from redis.asyncio import ConnectionPool, Redis

from app.core.settings import settings


class CacheManager:
    _pool: ConnectionPool | None = None
    _self: Redis | None = None

    @classmethod
    async def init_session(cls) -> None:
        cls._pool = ConnectionPool(
            host=settings.CACHE_IP,
            port=settings.CACHE_PORT,
            password=settings.CACHE_PASSWORD,
            decode_responses=True,
        )
        cls._client = Redis(connection_pool=cls._pool)

    @classmethod
    async def close_session(cls) -> None:
        if cls._pool:
            await cls._pool.disconnect()
        if cls._client:
            await cls._client.aclose()

    @classmethod
    def get_client(cls) -> Redis:
        if not cls._client:
            raise RuntimeError
        return cls._client


def get_cache_client() -> Redis:
    return CacheManager.get_client()
