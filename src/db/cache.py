import json
from abc import ABC, abstractmethod

import orjson
from redis.asyncio import Redis
from typing import Type
from pydantic import BaseModel


class AbstractCache(ABC):
    @abstractmethod
    def get(self, key: str):
        ...

    @abstractmethod
    def set(self, key: str, value: str):
        ...


class RedisCacheStorage(AbstractCache):
    def __init__(self, redis: Redis, cache_time: int):
        self._redis = redis
        self._cache_time = cache_time

    async def get(self, key: str):
        data = await self._redis.get(key)
        return data

    async def set(self, key: str, value: str):
        await self._redis.set(key, value, ex=self._cache_time)


class Cache:
    def __init__(self, model_class: Type[BaseModel], storage: AbstractCache):
        self._model_class = model_class
        self._storage = storage

    async def get(self, *args, **kwargs):
        key = '%s:query:%s' % (self._model_class.__name__, str(kwargs))
        data = await self._storage.get(key)
        if not data:
            return None

        data = orjson.loads(data)
        if isinstance(data, dict):
            return self._model_class(**data)
        elif isinstance(data, list):
            data = [self._model_class.model_validate_json(obj) for obj in data]
            return data

    async def set(self, *args, **kwargs):
        key = '%s:query:%s' % (self._model_class.__name__, str(kwargs))
        if isinstance(args[0], list):
            value = [obj.model_dump_json() for obj in args[0]]
            value = orjson.dumps(value, default=None)
        else:
            value = json.dumps(args[0].dict())
        await self._storage.set(key=key, value=value)
