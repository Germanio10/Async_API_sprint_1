from models.utils import BaseOrjsonModel


class PersonFilm(BaseOrjsonModel):
    id: str | None
    roles: list[str | None] = []


class Person(BaseOrjsonModel):
    id: str
    full_name: str
    films: list[PersonFilm | None] | None


class RolePerson(BaseOrjsonModel):
    id: str
    name: str
