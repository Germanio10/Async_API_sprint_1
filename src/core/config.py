import logging

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings


from logging import config as logging_config

from core.logger import LOGGING

BASE_DIR = Path(__file__).resolve().parent.parent.parent

logging_config.dictConfig(LOGGING)

load_dotenv(f"{BASE_DIR}/.env")


class RedisSettings(BaseSettings):
    host: str = Field(validation_alias='REDIS_HOST')
    port: int = Field(validation_alias='REDIS_PORT')


class ElasticsearchSettings(BaseSettings):
    host: str = Field(validation_alias='ELASTIC_HOST')
    port: int = Field(validation_alias='ELASTIC_PORT')

    def url(self):
        return f'http://{self.host}:{self.port}'


class RateLimitSettings(BaseSettings):
    limit: int = Field(validation_alias='LIMIT', default=1000)
    interval: int = Field(validation_alias='INTERVAL', default=60)


class Settings(BaseSettings):
    log_level: int | str = Field(validation_alias='LOG_LEVEL', default=logging.DEBUG)
    person_cache_expire: int = Field(validation_alias='PERSON_CACHE_EXPIRE_IN_SECONDS', default=60 * 5)
    film_cache_expire: int = Field(validation_alias='FILM_CACHE_EXPIRE_IN_SECONDS', default=60 * 5)
    genre_cache_expire: int = Field(validation_alias='GENRE_CACHE_EXPIRE_IN_SECONDS', default=60 * 5)
    redis: RedisSettings = RedisSettings()
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()
    rate_limit: RateLimitSettings = RateLimitSettings()


settings = Settings()
