FROM python:3.10 AS fastAPI

WORKDIR /app

COPY requirements.txt requirements.txt

COPY entrypoint.sh entrypoint.sh

RUN  pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir

RUN apt-get update && apt-get install -y netcat-traditional

COPY ./src .

EXPOSE 8000

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/bin/bash", "./entrypoint.sh"]

FROM python:3.10 AS tests

WORKDIR /tests/functional

COPY tests/functional/requirements.txt requirements.txt
COPY tests/functional/entrypoint.sh /entrypoint

RUN  pip install --upgrade pip --no-cache-dir\
     && pip install -r requirements.txt --no-cache-dir

COPY ./tests/functional .

RUN chmod +x /entrypoint
ENTRYPOINT ["/entrypoint"]
