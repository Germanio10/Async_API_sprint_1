import json
import uuid
import pytest
from http import HTTPStatus

pytestmark = pytest.mark.asyncio


async def test_index(es_client):
    index = await es_client.indices.get(
        index="persons", ignore=[HTTPStatus.NOT_FOUND]
    )

    assert 'error' not in index.keys()
    assert 'persons' in index.keys()


@pytest.mark.parametrize(
    'person_data, status',
    [
        (
            {
                "id": "test_1",
                "full_name": "Test Name 1",
                "films": [{
                    "id": str(uuid.uuid4()),
                    "roles": ["actor"]
                }]
            },
            HTTPStatus.OK
        ),
        (
            {
                "id": "test_2",
                "full_name": "Test Name 2",
                "films": [{
                    "id": str(uuid.uuid4()),
                    "roles": ["actor", "writer"]
                }]
            },
            HTTPStatus.OK
        )
    ]
)
async def test_person_pk(es_client, redis_client, make_get_request,
                         es_write_data, person_data, status):

    person_id = person_data["id"]

    data = [{'_index': 'persons', '_id': person_id, '_source': person_data}]
    await es_write_data(data)
    response = await make_get_request({}, "persons/%s/" % person_id)

    await es_client.delete(index="persons", id=person_id)

    redis_data = redis_client.get("Person:query:{'uuid': '%s'}" % person_id)
    redis_client.delete("Person:query:{'uuid': '%s'}" % person_id)
    redis_data = json.loads(redis_data)

    assert redis_data
    assert redis_data == person_data
    assert response['status'] == status
    assert response['body'] == person_data


async def test_person_search_not_found(make_get_request):
    query_data = {
        'name': 'person1234567890',
    }
    response = await make_get_request(query_data, 'persons/search')

    assert response['status'] == HTTPStatus.OK
    assert response['body'] == {'detail': 'person not found'}


@pytest.mark.parametrize(
    'page_number, page_size, answer_len, status_code',
    [
        (1, 10, 10, HTTPStatus.OK),
        (6, 10, 2, HTTPStatus.OK),
        (11, 5, 2, HTTPStatus.OK),
        (0, 10, 1, HTTPStatus.UNPROCESSABLE_ENTITY),
        (1, 0, 1, HTTPStatus.UNPROCESSABLE_ENTITY)
    ]
)
async def test_person_search_pagination(make_get_request, add_persons, page_number,
                                        page_size, answer_len, status_code):
    query_data = {
        'name': 'Test_Name',
        'page_number': page_number,
        'page_size': page_size
    }
    response = await make_get_request(query_data, 'persons/search')

    assert response['status'] == status_code
    if 'results' in response['body']:
        assert len(response['body']['results']) == answer_len
    else:
        assert len(response['body']) == answer_len


async def test_films_by_person(make_get_request, add_movies):
    query_data = {
        'name': 'Test_Name',
        'page_number': 1,
        'page_size': 40
    }
    person_id = 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95'
    response = await make_get_request(query_data, f'persons/{person_id}/film/')

    assert response['status'] == HTTPStatus.OK
    assert len(response['body']['results']) == 33
