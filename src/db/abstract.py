from abc import ABC, abstractmethod

from elasticsearch import AsyncElasticsearch
from redis.asyncio.client import Redis


class AbstractStorage(ABC):
    @abstractmethod
    def get_by_id(self, *args, **kwargs):
        ...

    @abstractmethod
    def get_list(self, *args, **kwargs):
        ...


class ElasticStorage(AbstractStorage):

    def get_by_id(self, *args, **kwargs):
        pass

    def get_list(self, *args, **kwargs):
        pass


class AbstractRedis(ABC):

    @abstractmethod
    def get_cache(self, *args, **kwargs):
        ...

    @abstractmethod
    def set_cache(self, *args, **kwargs):
        ...

    @abstractmethod
    def _redis(self) -> Redis:
        ...
