import json
import logging
import os

import requests

from .cache import get_redis_key, cache_response, get_cached_response
from .types import Response, YnabException

API_KEY = os.getenv("YNAB_API_KEY")
YNAB_HOST = "https://api.ynab.com/v1"

logger = logging.getLogger(__name__)


def _get_response(**kwargs):
    redis_key = get_redis_key(kwargs)

    cached_response = get_cached_response(redis_key)
    if cached_response:
        logger.info(f"Using cached response for {redis_key}")
        return cached_response

    logger.info(f"Making request: {redis_key}")
    response = requests.request(**kwargs)
    response = Response.from_requests_response(response)

    cache_response(redis_key, response)
    return response


def make_ynab_request(method, uri, additional_headers=None, **kwargs):
    additional_headers = additional_headers or {}
    default_headers = {"Authorization": f"Bearer {API_KEY}"}
    response = _get_response(
        method=method,
        url=YNAB_HOST + uri,
        headers={**default_headers, **additional_headers},
        **kwargs,
    )
    if response.status_code >= 300:
        raise YnabException(
            f"{response.status_code}: {json.dumps(response.data, indent=2)}"
        )
    return response
