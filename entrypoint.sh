#!/bin/bash

while ! nc -z redis 6379; do
    sleep 1
done

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
