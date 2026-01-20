import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class __Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.env', '.env.prod'),
        env_file_encoding='utf-8',
        extra='ignore',
    )
    DEBUG: bool = True
    API_URL: str = os.getenv('API_URL', 'http://localhost:8000/')
    DB_URL: str = os.getenv(
        'DB_URL',
        'postgresql+psycopg://user:password@127.0.0.1:5432/database',
    )
    OSRM_URL: str = os.getenv('OSRM_URL', 'http://localhost:5000/')
    H3_RESOLUTION: int = int(os.getenv('H3_RESOLUTION', '9'))

    TOKEN_TYPE: str = os.getenv('TOKEN_TYPE', 'Bearer')
    TOKEN_EXPIRE_MINUTES: int = int(os.getenv('TOKEN_EXPIRE_MINUTES', '60'))
    TOKEN_SECRET_KEY: str = os.getenv('TOKEN_SECRET_KEY', 'secret-key')
    TOKEN_ALGORITHM: str = os.getenv('TOKEN_ALGORITHM', 'HS256')

    CACHE_IP: str = os.getenv('CACHE_IP', 'cache')
    CACHE_PORT: int = int(os.getenv('CACHE_PORT', '60'))
    CACHE_PASSWORD: str = os.getenv('CACHE_PASSWORD', 'password')
    CACHE_TTL_SECONDS: int = int(os.getenv('CACHE_TTL_SECONDS', '600'))


@lru_cache
def __get_settings() -> __Settings:
    return __Settings()


settings = __get_settings()
