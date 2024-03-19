import json
import pytest
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


async def test_index(es_client):
    index = await es_client.indices.get(
        index="genres", ignore=[HTTPStatus.NOT_FOUND]
    )

    assert 'error' not in index.keys()
    assert 'genres' in index.keys()


@pytest.mark.parametrize(
    'genre_data, status',
    [
        (
            {
                "id": 'test1',
                "name": "Test_1"
            },
            HTTPStatus.OK
        ),
        (
            {
                "id": 'test2',
                "name": "Test_2"
            },
            HTTPStatus.OK
        )
    ]
)
async def test_genre(es_client, make_get_request, redis_client,
                     es_write_data, genre_data, status):

    genre_id = genre_data["id"]

    data = [{'_index': 'genres', '_id': genre_id, '_source': genre_data}]
    await es_write_data(data)
    response = await make_get_request({}, "genres/%s/" % genre_id)
    await es_client.delete(index="genres", id=genre_id)

    redis_data = redis_client.get("Genre:query:{'uuid': '%s'}" % genre_id)
    redis_client.delete("Genre:query:{'uuid': '%s'}" % genre_id)
    redis_data = json.loads(redis_data)

    assert redis_data
    assert redis_data == genre_data
    assert response['status'] == status
    assert response['body'] == genre_data


async def test_genre_not_found_id(make_get_request):
    genre_id = '123'

    genre = await make_get_request(params={'genre_id': genre_id},
                                   method=f'genres/{genre_id}')

    assert genre.get('status') == HTTPStatus.NOT_FOUND
    assert genre.get('body') == {"detail": "genre not found"}


async def test_all_genres(make_get_request, add_genres):
    params = {
        'page_number': 1,
        'page_size': 10,
        'sort': '-name',
    }
    result = await make_get_request(params=params, method='genres')

    assert result['status'] == HTTPStatus.OK
    assert len(result['body']['results']) == 10
    # проверка сортировки
    # genres = result['body']
    # sorted_genres = sorted(genres, key=lambda x: x['name'], reverse=True)
    # assert genres == sorted_genres
