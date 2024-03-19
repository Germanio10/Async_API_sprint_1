from db.abstract import ElasticStorage
from elasticsearch import AsyncElasticsearch, NotFoundError
from models.genre import Genre


class BaseElasticGenreID(ElasticStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self._elastic = elastic

    async def get_by_id(self, genre_id: str) -> Genre | None:
        try:
            doc = await self._elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])


class BaseElasticAllGenre(ElasticStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self._elastic = elastic

    async def get_list(self,
                       page_number: int,
                       page_size: int,
                       sort: str | None) -> list[Genre] | None:
        try:
            direction = 'desc' if sort.startswith('-') else 'asc'
            field = sort.lstrip('-')
            doc = await self._elastic.search(
                index='genres',
                body={
                    "query": {"match_all": {}},
                    "size": page_size,
                    "from": (page_number - 1) * page_size,
                    "sort": [{field: {"order": direction}}]
                }
            )
        except NotFoundError:
            return None

        genres = [Genre(**doc['_source']) for doc in doc['hits']['hits']]
        return genres
