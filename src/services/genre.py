from functools import lru_cache
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from core.config import settings
from db.abstract import AbstractStorage
from db.cache import Cache, RedisCacheStorage
from services.abstract import AbstractService
from db.elastic import get_elastic
from db.redis import get_redis
from db.base_genre import BaseElasticGenreID, BaseElasticAllGenre
from models.genre import Genre


class GenreServiceID(AbstractService):
    def __init__(self, cache: Cache, storage: AbstractStorage):
        self._cache = cache
        self._storage = storage

    async def get_data(self, genre_id: str) -> Genre | None:
        genre = await self._cache.get(uuid=genre_id)
        if not genre:
            genre = await self._storage.get_by_id(genre_id)
            if not genre:
                return None
            await self._cache.set(genre, uuid=genre_id)
        return genre


class GenreServiceAll(AbstractService):
    def __init__(self, cache: Cache, storage: AbstractStorage):
        self._cache = cache
        self._storage = storage

    async def get_data(self, page_number, page_size, sort) -> list[Genre] | None:
        genres = await self._cache.get(page_size=page_size,
                                       page_number=page_number,
                                       sort=sort)
        if not genres:
            genres = await self._storage.get_list(page_number, page_size, sort)
            if not genres:
                return []
            await self._cache.set(genres,
                                  page_size=page_size,
                                  page_number=page_number,
                                  sort=sort)
        return genres


@lru_cache
def get_genre_service_id(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreServiceID:
    cache_storage = RedisCacheStorage(redis, settings.genre_cache_expire)
    return GenreServiceID(Cache(Genre, cache_storage), BaseElasticGenreID(elastic))


@lru_cache()
def get_genre_service_all(
        redis: Redis = Depends(get_redis),
        elastic:  AsyncElasticsearch = Depends(get_elastic),
) -> GenreServiceAll:
    cache_storage = RedisCacheStorage(redis, settings.genre_cache_expire)
    return GenreServiceAll(Cache(Genre, cache_storage), BaseElasticAllGenre(elastic))
