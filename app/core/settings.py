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
    DB_URL: str = os.getenv(
        'DB_URL',
        'postgresql+psycopg://user:password@127.0.0.1:5432/database',
    )
    OSRM_URL: str = os.getenv('OSRM_URL', 'http://localhost:5000/')
    API_URL: str = os.getenv('API_URL', 'http://localhost:8000/')
    TOKEN_TYPE: str = os.getenv('TOKEN_TYPE', 'Bearer')
    TOKEN_EXPIRE_MINUTES: int = int(os.getenv('TOKEN_EXPIRE_MINUTES', '60'))
    TOKEN_SECRET_KEY: str = os.getenv('TOKEN_SECRET_KEY', 'secret-key')
    TOKEN_ALGORITHM: str = os.getenv('TOKEN_ALGORITHM', 'HS256')


@lru_cache
def __get_settings() -> __Settings:
    return __Settings()


settings = __get_settings()
