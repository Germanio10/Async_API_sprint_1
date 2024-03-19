import orjson
from pydantic import BaseModel
from typing import List, TypeVar, Generic


T = TypeVar('T')


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseOrjsonModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class PaginatedResults(BaseOrjsonModel, Generic[T]):
    results: List[T]
    page_size: int
    page: int
