from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from redis.asyncio import Redis

from core.config import settings
from db.abstract import AbstractStorage
from db.base_person import BaseElasticPersonID, BaseElasticPersonSearch, BaseElasticFilmByPerson
from db.cache import RedisCacheStorage, Cache
from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
from services.abstract import AbstractService

PERSON_CACHE_EXPIRE_IN_SECONDS = settings.person_cache_expire


class PersonServiceID(AbstractService):
    def __init__(self, cache: Cache, storage: AbstractStorage):
        self._cache = cache
        self._storage = storage

    async def get_data(self, person_id: str):
        person = await self._cache.get(uuid=person_id)
        if not person:
            person = await self._storage.get_by_id(person_id)
            if not person:
                return None
            await self._cache.set(person, uuid=person_id)
        return person


class PersonServiceSearch(AbstractService):
    def __init__(self, storage: AbstractStorage):
        self._storage = storage

    async def get_data(self, search, page_number, page_size):
        person = await self._storage.get_list(search, page_number, page_size)
        if not person:
            return []
        return person


class FilmByPersonService(AbstractService):
    def __init__(self, storage: AbstractStorage):
        self._storage = storage

    async def get_data(self, person_id, page_number, page_size):
        films = await self._storage.get_list(person_id, page_number, page_size)
        if not films:
            return []
        return films


@lru_cache()
def get_person_service_id(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonServiceID:
    cache_storage = RedisCacheStorage(redis, settings.genre_cache_expire)
    return PersonServiceID(Cache(Person, cache_storage), BaseElasticPersonID(elastic))


@lru_cache()
def get_person_service_search(
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonServiceSearch:
    return PersonServiceSearch(BaseElasticPersonSearch(elastic))


@lru_cache()
def get_film_by_person_service(
        elastic: AsyncElasticsearch = Depends(get_elastic)
) -> FilmByPersonService:
    return FilmByPersonService(BaseElasticFilmByPerson(elastic))
