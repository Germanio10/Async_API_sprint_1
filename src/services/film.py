from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from core.config import settings
from db.abstract import AbstractStorage
from db.cache import Cache, RedisCacheStorage
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

from services.abstract import AbstractService
from db.base_film import BaseElasticFilmID, BaseElasticFilmSort, BaseElasticFilmSearch


class FilmServiceID(AbstractService):
    def __init__(self, cache: Cache, storage: AbstractStorage):
        self._cache = cache
        self._storage = storage

    async def get_data(self, film_id: str):
        film = await self._cache.get(uuid=film_id)
        if not film:
            film = await self._storage.get_by_id(film_id)
            if not film:
                return None
            await self._cache.set(film, uuid=film_id)
        return film


class FilmServiceSearch(AbstractService):
    def __init__(self, storage: AbstractStorage):
        self._storage = storage

    async def get_data(self, search, page_number, page_size):
        film = await self._storage.get_list(search, page_number, page_size)
        if not film:
            return []
        return film


class FilmServiceSort(AbstractService):
    def __init__(self, storage: AbstractStorage):
        self._storage = storage

    async def get_data(self, page_number, page_size, genre, sort):
        films = await self._storage.get_list(page_number, page_size, genre, sort)
        if not films:
            return []
        return films


@lru_cache()
def get_film_service_id(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmServiceID:
    cache_storage = RedisCacheStorage(redis, settings.genre_cache_expire)
    return FilmServiceID(Cache(Film, cache_storage), BaseElasticFilmID(elastic))


@lru_cache()
def get_film_service_search(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmServiceSearch:
    return FilmServiceSearch(BaseElasticFilmSearch(elastic))


@lru_cache()
def get_film_service_sort(
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> FilmServiceSort:
    return FilmServiceSort(BaseElasticFilmSort(elastic))
