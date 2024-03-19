import time

from elasticsearch import Elasticsearch

from utils_config import settings


if __name__ == '__main__':
    es_client = Elasticsearch(hosts=settings.elasticsearch.url(), validate_cert=False, use_ssl=False)
    while True:
        if es_client.ping():
            break
        time.sleep(1)
