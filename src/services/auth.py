from functools import lru_cache

import aiohttp
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import MissingTokenError, JWTDecodeError
from fastapi import Depends, HTTPException
from starlette import status
from starlette.requests import Request

from models.users import User
from core.config import settings


class CheckAuth:
    def __init__(self, authorize: AuthJWT):
        self._authorize = authorize

    async def check_authorization(self, request: Request):
        try:
            await self._authorize.jwt_required()
            user_id = await self._authorize.get_jwt_subject()
            role_id = (await self._authorize.get_raw_jwt())["role_id"]
            return User(user_id=user_id, role_id=role_id)

        except MissingTokenError:
            return

        except JWTDecodeError:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token is invalid")


@lru_cache()
def get_check_auth_service(
        authorize: AuthJWT = Depends(),
) -> CheckAuth:
    return CheckAuth(authorize)
