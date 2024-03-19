from elasticsearch import AsyncElasticsearch, NotFoundError

from db.abstract import ElasticStorage
from models.film import Film, MainFilmInformation


class BaseElasticFilmID(ElasticStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self._elastic = elastic

    async def get_by_id(self, object_id: str) -> Film | None:
        try:
            doc = await self._elastic.get(index='movies', id=object_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])


class BaseElasticFilmSearch(ElasticStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self._elastic = elastic

    async def get_list(self, search, page_number, page_size) -> list[MainFilmInformation] | None:
        body = {
            "query": {
                "multi_match": {
                    "query": search,
                    "fields": ["title", "description"]
                }
            },
            "size": page_size,
            "from": (page_number - 1) * page_size
        }
        try:
            doc = await self._elastic.search(index='movies', body=body)
            answer = [MainFilmInformation(**hit['_source']) for hit in doc['hits']['hits']]
            return answer
        except NotFoundError:
            return []


class BaseElasticFilmSort(ElasticStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self._elastic = elastic

    async def get_list(self, page_number, page_size, genre, sort) -> list[MainFilmInformation] | None:
        try:
            direction = 'desc' if sort.startswith('-') else 'asc'
            field = sort.lstrip('-')
            if not genre:
                query = {
                    'sort': [{field: {'order': direction}}],
                    'size': page_size,
                    'from': (page_number - 1) * page_size
                }
            else:
                query = {
                    'query': {
                        'bool': {
                            'filter': [
                                {'nested': {
                                    'path': 'genres_list',
                                    'query': {
                                        'bool': {
                                            'must': [
                                                {'match': {'genres_list.id': genre}},
                                            ]
                                        }
                                    }
                                }},
                            ],
                        }
                    },
                    'sort': [{field: {'order': direction}}],
                    'size': page_size,
                    'from': (page_number - 1) * page_size
                }
            doc = await self._elastic.search(index='movies', body=query)
        except NotFoundError:
            return None
        answer = [MainFilmInformation(**hit['_source']) for hit in doc['hits']['hits']]
        return answer
