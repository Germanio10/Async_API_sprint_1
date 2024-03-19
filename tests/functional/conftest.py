import asyncio
import random
import uuid
from time import sleep

import aiohttp
import pytest
import redis
from elasticsearch import AsyncElasticsearch
from elasticsearch._async.helpers import async_bulk

from functional.settings import settings


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=settings.elasticsearch.url())
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def aiohttp_client():
    client = aiohttp.ClientSession()
    yield client
    await client.close()


@pytest.fixture(scope='session')
def make_get_request(aiohttp_client):
    async def inner(params: dict, method: str):
        url = f'{settings.fastapi.url()}/{method}'
        async with aiohttp_client.get(url, params=params) as response:
            body = await response.json()
            status = response.status
            return {
                'body': body,
                'status': status
            }

    return inner


@pytest.fixture(scope='session')
async def redis_client():
    client = redis.Redis(host=settings.redis.host, port=settings.redis.port)
    yield client
    client.close()


@pytest.fixture
def es_write_data(es_client):
    async def inner(data: list[dict]):
        updated, errors = await async_bulk(client=es_client, actions=data)
        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner


@pytest.fixture
async def add_movies(es_client, es_write_data):
    es_data = [{
                'id': f'test_{i}',
                'imdb_rating': 5.0 + (i + 1) / 10,
                'genre': ['Action'],
                'genres_list': [{'id': 'test_id_movie', 'name': 'Action'}],
                'title': 'Test_title',
                'description': 'Test_description',
                'directors_names': ['Test_director'],
                'actors_names': ['Test_actor_1', 'Test_actor_2'],
                'writers_names': ['Test_writer_1', 'Test_writer_2'],
                'actors': [
                    {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Test_actor_1'},
                    {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Test_actor_2'}
                ],
                'writers': [
                    {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Test_writer_1'},
                    {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Test_writer_2'}
                ],
                'directors': [
                    {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f88', 'name': 'Test_director'}
                ]
            } for i in range(33)]

    bulk_query: list[dict] = []
    delete_bulk: list[dict] = []

    for row in es_data:
        data = {'_index': 'movies', '_id': row['id'], '_source': row}
        bulk_query.append(data)
        delete_bulk.append({'delete': {'_index': 'movies', '_id': row['id']}})

    await es_write_data(bulk_query)
    sleep(2)
    yield
    await es_client.bulk(body=delete_bulk, index='movies')


@pytest.fixture
async def add_persons(es_client, es_write_data):
    data = []
    person_to_delete = []
    for ind in range(52):
        films = []
        for film_id in range(random.randint(1, 10)):
            films.append({
                "id": str(uuid.uuid4()),
                "roles": ["actor"]

            })

        person_data = {
            "id": f"test_{ind}",
            "full_name": "Test_Name",
            "films": films
        }
        data.append({"_index": "persons", "_id": f"test_{ind}", "_source": person_data})
        person_to_delete.append({"delete": {"_index": 'persons', "_id": f"test_{ind}"}})
    await es_write_data(data)
    sleep(2)
    yield
    await es_client.bulk(body=person_to_delete, index='persons')


@pytest.fixture
async def add_genres(es_client, es_write_data):
    data = []
    genres_to_delete = []
    for i in range(20):
        genre_data = {
            "id": f"test_{i}",
            "name": "Test"
        }
        data.append({"_index": "genres", "_id": f"test_{i}", "_source": genre_data})
        genres_to_delete.append({"delete": {"_index": 'genres', "_id": f"test_{i}"}})
    await es_write_data(data)
    sleep(1)
    yield
    await es_client.bulk(body=genres_to_delete, index='genres')
