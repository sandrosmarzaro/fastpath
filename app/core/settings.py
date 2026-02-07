from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.env', '.env.prod'),
        env_file_encoding='utf-8',
        extra='ignore',
    )
    DEBUG: bool = True
    LOG_LEVEL: str = 'INFO'
    API_URL: str = 'http://localhost:8000/'
    DB_URL: str = 'postgresql+psycopg://user:password@127.0.0.1:5432/database'
    OSRM_URL: str = 'http://localhost:5000/'
    H3_RESOLUTION: int = 9

    TOKEN_TYPE: str = ''
    TOKEN_EXPIRE_MINUTES: int = 60
    TOKEN_SECRET_KEY: str = ''
    TOKEN_ALGORITHM: str = ''

    CACHE_IP: str = 'cache'
    CACHE_PORT: int = 60
    CACHE_PASSWORD: str = ''
    CACHE_TTL_SECONDS: int = 600


@lru_cache
def _get_settings() -> _Settings:
    return _Settings()


settings = _get_settings()
