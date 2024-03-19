from models.genre import Genre
from models.person import RolePerson
from models.utils import BaseOrjsonModel


class Film(BaseOrjsonModel):
    id: str
    title: str
    imdb_rating: float | None
    description: str | None
    genres_list: list[Genre] | None
    actors: list[RolePerson] | None
    writers: list[RolePerson] | None
    directors: list[RolePerson] | None


class MainFilmInformation(BaseOrjsonModel):
    id: str
    title: str
    imdb_rating: float | None
    genres_list: list[Genre] | None


class FilmOut(BaseOrjsonModel):
    id: str
    title: str
    imdb_rating: float | None
    description: str | None
    genre: list[Genre] | None
    actors: list[RolePerson] | None
    writers: list[RolePerson] | None
    directors: list[RolePerson] | None

    @classmethod
    def from_film(cls, film: Film):
        return cls(
            id=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
            description=film.description,
            genre=film.genres_list,
            actors=film.actors,
            writers=film.writers,
            directors=film.directors
        )


class FilmGenreOut(BaseOrjsonModel):
    id: str
    title: str
    imdb_rating: float | None
    genre: list[Genre] | None

    @classmethod
    def from_film(cls, film: Film):
        return cls(
            id=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
            genre=film.genres_list,
        )
