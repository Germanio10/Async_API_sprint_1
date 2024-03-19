import pytest
import json
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


async def test_index(es_client):
    index = await es_client.indices.get(
        index='movies', ignore=[HTTPStatus.NOT_FOUND]
    )

    assert 'error' not in index.keys()
    assert 'movies' in index.keys()


@pytest.mark.parametrize(
    'movie_data, status',
    [
        (
                {
                    'id': 'test_1',
                    'imdb_rating': 8.5,
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
                },
                HTTPStatus.OK
        )
    ]
)
async def test_movie_get_by_id(es_client, redis_client, make_get_request,
                               es_write_data, movie_data, status):
    film_id = movie_data['id']
    data = [{'_index': 'movies', '_id': film_id, '_source': movie_data}]
    await es_write_data(data)

    response = await make_get_request(params={}, method=f'films/{film_id}')

    await es_client.delete(index='movies', id=film_id)

    redis_data = redis_client.get("Film:query:{'uuid': '%s'}" % film_id)
    redis_client.delete("Film:query:{'uuid': '%s'}" % film_id)
    redis_data = json.loads(redis_data)

    assert redis_data
    assert response['status'] == status

    fields_to_remove = ['directors_names', 'actors_names', 'writers_names', 'genre']
    for field in fields_to_remove:
        movie_data.pop(field)

    assert redis_data == movie_data
    assert response['body'].pop('genre') == redis_data.pop('genres_list')
    assert response['body'] == redis_data


async def test_movie_invalid_id(make_get_request):
    film_id = '1234'
    movie = await make_get_request(params={'film_id': film_id},
                                   method=f'films/{film_id}')
    assert movie.get('status') == HTTPStatus.NOT_FOUND
    assert movie.get('body') == {"detail": "film not found"}


async def test_movie_search_not_found(make_get_request):
    error_film = await make_get_request(method='films/search', params={
        'search': 'movie123456',
        'page_number': 1,
        'page_size': 10
    })

    assert error_film.get('status') == HTTPStatus.NOT_FOUND
    assert error_film.get('body') == {'detail': 'film not found'}


@pytest.mark.parametrize(
    'page_number, page_size, length, status',
    [
        (1, 10, 10, HTTPStatus.OK),
        (4, 10, 3, HTTPStatus.OK),
        (0, 10, 1, HTTPStatus.UNPROCESSABLE_ENTITY),
        (1, 0, 1, HTTPStatus.UNPROCESSABLE_ENTITY)
    ]
)
async def test_movie_search_pagination(make_get_request, add_movies, page_number,
                                       page_size, length, status):
    films = await make_get_request(method='films/search', params={
        'search': 'Test_title',
        'page_number': page_number,
        'page_size': page_size
    })

    assert films.get('status') == status
    if 'results' in films.get('body'):
        assert len(films.get('body', {}).get('results')) == length
    else:
        assert len(films.get('body')) == length


async def test_movie_main_page_without_genre(make_get_request, add_movies):
    films = await make_get_request(method='films', params={
        'sort': '-imdb_rating',
        'page_number': 1,
        'page_size': 10
    })

    body = films.get('body', {})
    results = body.get('results', [])
    assert films.get('status') == HTTPStatus.OK
    assert len(results) == 10
    assert results[0].get('imdb_rating') >= results[1].get('imdb_rating')
    assert results[1].get('imdb_rating') >= results[2].get('imdb_rating')


async def test_movie_main_page_with_genre(make_get_request, add_movies):
    films = await make_get_request(method='films', params={
        'sort': 'imdb_rating',
        'page_number': 1,
        'page_size': 10,
        'genre': 'test_id_movie'
    })

    body = films.get('body', {})
    results = body.get('results', [])
    assert films.get('status') == HTTPStatus.OK
    assert len(results) == 10
    assert results[0].get('imdb_rating') <= results[1].get('imdb_rating')


async def test_movie_main_page_invalid_genre(make_get_request):

    error_film = await make_get_request(method='films', params={
        'sort': 'imdb_rating',
        'page_number': 1,
        'page_size': 10,
        'genre': '123'
    })

    assert error_film.get('status') == HTTPStatus.NOT_FOUND
    assert error_film.get('body') == {'detail': 'film not found'}
