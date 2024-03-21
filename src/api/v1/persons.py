from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.requests import Request
from starlette import status

from api.v1 import messages
from models.film import FilmGenreOut
from models.person import Person
from models.utils import PaginatedResults
from services.auth import CheckAuth, get_check_auth_service
from services.person import (
    get_person_service_id, PersonServiceID,
    get_person_service_search, PersonServiceSearch,
    get_film_by_person_service, FilmByPersonService
)


router = APIRouter()


@router.get('/{person_id}/',
            response_model=Person,
            description="Получение персоны по id")
async def person_details(
        request: Request,
        person_id: str,
        person_service: PersonServiceID = Depends(get_person_service_id),
        check_auth: CheckAuth = Depends(get_check_auth_service),
) -> Person:
    user = await check_auth.check_authorization(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Please login')
    person = await person_service.get_data(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.PERSON_NOT_FOUND)

    return Person(id=person.id, full_name=person.full_name, films=person.films)


@router.get('/search',
            response_model=PaginatedResults[Person],
            description="Поиск персоны по name")
async def persons_search(
        request: Request,
        name: str,
        page_number: Annotated[int, Query(ge=1,
                               description="Pagination page number")] = 1,
        page_size: Annotated[int, Query(ge=1,
                             description="Pagination page size")] = 10,
        person_service: PersonServiceSearch = Depends(get_person_service_search),
        check_auth: CheckAuth = Depends(get_check_auth_service),
) -> PaginatedResults[Person]:
    user = await check_auth.check_authorization(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Please login')
    persons = await person_service.get_data(name, page_number, page_size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.OK, detail=messages.PERSON_NOT_FOUND)

    return PaginatedResults(results=persons, page_size=page_size, page=page_number)


@router.get('/{person_id}/film/',
            response_model=PaginatedResults[FilmGenreOut],
            description="Получение фильмов с участием персоны по id")
async def films_by_persons(
        request: Request,
        person_id: str,
        page_number: Annotated[int, Query(ge=1,
                                          description="Pagination page number")] = 1,
        page_size: Annotated[int, Query(ge=1,
                                        description="Pagination page size")] = 10,
        person_service: FilmByPersonService = Depends(get_film_by_person_service),
        check_auth: CheckAuth = Depends(get_check_auth_service),
) -> PaginatedResults[FilmGenreOut]:
    user = await check_auth.check_authorization(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Please login')
    films = await person_service.get_data(person_id, page_number, page_size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.OK, detail=messages.PERSON_NOT_FOUND)
    films_out = [FilmGenreOut.from_film(film) for film in films]

    return PaginatedResults(results=films_out, page_size=page_size, page=page_number)
