from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.requests import Request
from starlette import status

from api.v1 import messages
from models.genre import Genre
from models.utils import PaginatedResults
from services.auth import CheckAuth, get_check_auth_service
from services.genre import (
    GenreServiceID, get_genre_service_all,
    GenreServiceAll, get_genre_service_id
)
from limiter import rate_limit


router = APIRouter()


@router.get('/{genre_id}/',
            response_model=Genre,
            description="Получение жанра по id")
@rate_limit()
async def genre_details(
        request: Request,
        genre_id: str,
        genre_service: GenreServiceID = Depends(get_genre_service_id),
        check_auth: CheckAuth = Depends(get_check_auth_service),
) -> Genre:
    user = await check_auth.check_authorization(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Please login')
    genre = await genre_service.get_data(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.GENRE_NOT_FOUND)

    return Genre(id=genre.id, name=genre.name)


@router.get('/',
            response_model=PaginatedResults[Genre],
            description="Получение всех жанров. Сортировка по name")
async def all_genres(
        request: Request,
        page_number: Annotated[int, Query(ge=1,
                                          description="Pagination page number")] = 1,
        page_size: Annotated[int, Query(ge=1,
                                        description="Pagination page size")] = 10,
        sort: str | None = 'name',
        genre_service: GenreServiceAll = Depends(get_genre_service_all),
        check_auth: CheckAuth = Depends(get_check_auth_service),
) -> PaginatedResults[Genre]:
    user = await check_auth.check_authorization(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Please login')
    genres = await genre_service.get_data(page_number, page_size, sort)
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=messages.GENRE_NOT_FOUND)

    return PaginatedResults(results=genres, page_size=page_size, page=page_number)
