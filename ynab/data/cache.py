import json
from typing import Optional

import redis

from ynab.data.types import Response

r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def get_redis_key(request_kwargs: dict):
    method = request_kwargs["method"]
    uri = request_kwargs["url"]
    return f"ynab_api:{method}:{uri}"


def cache_response(key, response: Response):
    if response.is_success:
        r.set(key, response.json())
    else:
        r.delete(key)


def get_cached_response(key) -> Optional[Response]:
    serialized_response = r.get(key)
    if not serialized_response:
        return None
    response = Response(**{**json.loads(serialized_response), "source": "redis"})
    return response if response.is_success else None
