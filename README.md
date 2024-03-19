# Асинхронный API для кинотеатра
Этот сервис будет точкой входа для всех клиентов. В первой итерации в сервисе будут только анонимные пользователи.

### Используемые технологии
- **Язык**: python + FastAPI
- **Сервер**: ASGI(uvicorn)
- **Веб-сервер**: Nginx
- **Хранилище**: ElasticSearch
- **Кеширование**: Redis 
- **Контейнеризация**: Docker
- **Тестирование**: Pytest

## Установка и запуск
1. Для запуска проекта необходимо склонировать и запустить в докере проектное задание третьего спринта. 
 - Ссылка на спринт: https://github.com/ReplayForever/new_admin_panel_sprint_3.

2. Склонировать данный репозиторий c API:
```shell
git clone git@github.com:ReplayForever/Async_API_sprint_1.git
```

3. Скопировать настройки переменных окружения из .env.example в .env:
```shell
cp .env.example .env
```

4. Запустить проект:
```shell
docker-compose up
```
5. Тесты запустятся автоматически после подъёма всех контейнеров.
Для повторного запуска необходимо ввести:
```shell
docker-compose up tests
```

## Переменные окружения

| Variable                         | Explanation                                         | Example           |
|----------------------------------|-----------------------------------------------------|-------------------|
| `DB_HOST`                        | PostgreSQL Hostname                                 | `localhost`       |
| `DB_PASSWORD`                    | PostgreSQL Password                                 | `123qwe`          |
| `DB_USER`                        | PostgreSQL User                                     | `app`             |
| `DB_NAME`                        | PostgreSQL Database Name                            | `movies_database` |
| `DB_PORT`                        | PostgreSQL Port                                     | `5432`            |
| `REDIS_HOST`                     | Redis Hostname                                      | `redis`           |
| `REDIS_PORT`                     | Redis Port                                          | `6379`            |
| `PERSON_CACHE_EXPIRE_IN_SECONDS` | Time of data storage <br/>in Redis cache for person | `1000`            |
| `FILM_CACHE_EXPIRE_IN_SECONDS`   | Time of data storage <br/>in Redis cache for films  | `1000`            |
| `GENRE_CACHE_EXPIRE_IN_SECONDS`  | Time of data storage <br/>in Redis cache for genres | `1000`            |
| `ELASTIC_HOST`                   | ElasticSearch Hostname                              | `elasticsearch`   |
| `ELASTIC_PORT`                   | ElasticSearch Port                                  | `9200`            |
| `PARCE_SIZE`                     | Count data from db                                  | `1000`            |
| `UPDATED_DAYS_LIMIT`             | Day updated limit                                   | `1`               |
| `RERUN`                          | Work time etl in sec                                | `10`              |
| `ELASTIC_LOAD_SIZE`              | Data count in elastic                               | `1000`            |
| `LOG_LEVEL`                      | Level of logging                                    | `DEBUG`           |
| `FASTAPI_HOST`                   | FastAPI Hostname                                    | `fastapi`         |
| `FASTAPI_PORT`                   | FastAPI Port                                        | `8001`            |

## OpenAPI
Для проверки работоспособности проекта используется Swagger. 
Запускаем проект и по `http://localhost/api/openapi` переходим на Swager. Здесь можно проверить работу ендпоинтов