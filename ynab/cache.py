import json
from typing import Optional

import redis

from .types import Response

r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def get_redis_key(request_kwargs: dict):
    method = request_kwargs["method"]
    uri = request_kwargs["url"]
    params = request_kwargs.get("params", {})
    return f"ynab_api:{method}:{uri}:{json.dumps(params)}"


def _should_cache_response(response: Response):
    return response.is_success and response.method == "get"


def cache_response(key, response: Response):
    if _should_cache_response(response):
        r.set(key, response.json())


def get_cached_response(key) -> Optional[Response]:
    serialized_response = r.get(key)
    if not serialized_response:
        return None
    response = Response(**{**json.loads(serialized_response), "source": "redis"})
    return response if response.is_success else None
