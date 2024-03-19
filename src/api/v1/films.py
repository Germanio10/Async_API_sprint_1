from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.requests import Request

from api.v1 import messages
from models.film import FilmOut, FilmGenreOut
from models.utils import PaginatedResults
from services.auth import CheckAuth, get_check_auth_service
from services.film import (
    FilmServiceID, get_film_service_id, 
    FilmServiceSearch, get_film_service_search,
    FilmServiceSort, get_film_service_sort
)
from limiter import rate_limit


router = APIRouter()


@router.get('/{film_id}/',
            response_model=FilmOut,
            description="Получение фильма по id")
@rate_limit()
async def film_details(
        request: Request,
        film_id: str,
        film_service: FilmServiceID = Depends(get_film_service_id),
        check_auth: CheckAuth = Depends(get_check_auth_service),
) -> FilmOut:
    user = await check_auth.check_authorization(request)
    film = await film_service.get_data(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.FILM_NOT_FOUND)

    return FilmOut.from_film(film)


@router.get('/search',
            response_model=PaginatedResults[FilmGenreOut],
            description="Поиск фильма по title и description")
@rate_limit()
async def search_by_params(
        request: Request,
        search: str,
        page_number: Annotated[int, Query(ge=1,
                                          description=" Pagination page number")] = 1,
        page_size: Annotated[int, Query(ge=1,
                                        description="Pagination page size")] = 10,
        film_service: FilmServiceSearch = Depends(get_film_service_search),
        check_auth: CheckAuth = Depends(get_check_auth_service),
) -> PaginatedResults[FilmGenreOut]:
    user = await check_auth.check_authorization(request)
    films = await film_service.get_data(search=search,
                                        page_number=page_number,
                                        page_size=page_size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.FILM_NOT_FOUND)

    films_out = [FilmGenreOut.from_film(film) for film in films]
    return PaginatedResults(results=films_out, page_size=page_size, page=page_number)


@router.get('/',
            response_model=PaginatedResults[FilmGenreOut],
            description="Главная страница с фильмами. Сортировка по рейтингу. "
                        "Возможно указание жанра фильма по id жанра")
@rate_limit()
async def main_page(
        request: Request,
        page_number: Annotated[int, Query(ge=1,
                                          description="Pagination page number")] = 1,
        page_size: Annotated[int, Query(ge=1,
                                        description="Pagination page size")] = 10,
        genre: str = None,
        film_service: FilmServiceSort = Depends(get_film_service_sort),
        sort: str = '-imdb_rating',
        check_auth: CheckAuth = Depends(get_check_auth_service),
) -> PaginatedResults[FilmGenreOut]:
    user = await check_auth.check_authorization(request)
    films = await film_service.get_data(page_number, page_size, genre, sort=sort)
    films_out = [FilmGenreOut.from_film(film) for film in films]
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.FILM_NOT_FOUND)
    return PaginatedResults(results=films_out, page_size=page_size, page=page_number)
