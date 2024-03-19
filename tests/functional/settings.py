from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(f"{BASE_DIR}/.env")


class TestRedisSettings(BaseSettings):
    host: str = Field(validation_alias='REDIS_HOST')
    port: int = Field(validation_alias='REDIS_PORT')


class TestElasticsearchSettings(BaseSettings):
    host: str = Field(validation_alias='ELASTIC_HOST')
    port: int = Field(validation_alias='ELASTIC_PORT')

    def url(self):
        return f'http://{self.host}:{self.port}'


class TestFastAPISettings(BaseSettings):
    host: str = Field(validation_alias='FASTAPI_HOST', default='localhost')
    port: int = Field(validation_alias='FASTAPI_PORT', default=80)

    def url(self):
        return f'http://{self.host}:{self.port}/api/v1'


class TestSettings(BaseSettings):
    redis: TestRedisSettings = TestRedisSettings()
    elasticsearch: TestElasticsearchSettings = TestElasticsearchSettings()
    fastapi: TestFastAPISettings = TestFastAPISettings()


settings = TestSettings()
