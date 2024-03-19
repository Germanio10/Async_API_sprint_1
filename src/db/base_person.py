from elasticsearch import AsyncElasticsearch, NotFoundError

from db.abstract import ElasticStorage
from models.film import MainFilmInformation
from models.person import Person


class BaseElasticPersonID(ElasticStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self._elastic = elastic

    async def get_by_id(self, object_id: str) -> Person | None:
        try:
            doc = await self._elastic.get(index='persons', id=object_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])


class BaseElasticPersonSearch(ElasticStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self._elastic = elastic

    async def get_list(self, person_name, page_number, page_size) -> list[Person] | None:
        body = {
            'query': {
                'bool': {
                    'must': [
                        {'match': {'full_name': person_name}}
                    ]
                }
            },
            'size': page_size,
            'from': (page_number - 1) * page_size
        }
        try:
            doc = await self._elastic.search(
                index='persons',
                body=body
            )
        except NotFoundError:
            return []
        answer = [Person(**hit['_source']) for hit in doc['hits']['hits']]
        return answer


class BaseElasticFilmByPerson(ElasticStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self._elastic = elastic

    async def get_list(
            self,
            person_id: str,
            page_number: int,
            page_size: int
    ) -> list[MainFilmInformation] | None:
        body = {
            'sort': [
                {'imdb_rating': 'desc'}
            ],
            'query': {
                'bool': {
                    'should': [
                        {'nested': {
                            'path': 'actors',
                            'query': {
                                'bool': {
                                    'must': [
                                        {'match': {'actors.id': person_id}}
                                    ]
                                }
                            }
                        }},
                        {'nested': {
                            'path': 'writers',
                            'query': {
                                'bool': {
                                    'must': [
                                        {'match': {'writers.id': person_id}}
                                    ]
                                }
                            }
                        }},
                        {'nested': {
                            'path': 'directors',
                            'query': {
                                'bool': {
                                    'must': [
                                        {'match': {'directors.id': person_id}}
                                    ]
                                }
                            }
                        }},
                    ]
                }
            },
            'size': page_size,
            'from': (page_number - 1) * page_size
        }
        try:
            doc = await self._elastic.search(
                index='movies',
                body=body
            )
        except NotFoundError:
            return []
        answer = [MainFilmInformation(**hit['_source']) for hit in doc['hits']['hits']]
        return answer
