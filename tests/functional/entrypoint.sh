#!/bin/bash

python3 utils/wait_for_es.py && python3 utils/wait_for_redis.py

pytest
