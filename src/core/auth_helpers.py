import functools

from flask import abort, request

from src.core.database import api_key
from src.core.database.v2 import keys


__all__ = [
    "authorize_blueprint",
    "authorize_blueprint_v2",
    "authorize_route",
    "authorize_route_v2",
    "fake_authorize",
    "send_deprecation_warning",
]


def authorize_blueprint():
    """Determine if the request to a blueprint has been properly authorized."""
    # Was an Authorization header sent?
    if "Authorization" not in request.headers:
        abort(400)

    # Attempt to get the API key and validate it
    try:
        token = get_auth_token()
        if not api_key.exists(token):
            raise KeyError
    except (KeyError, IndexError):
        abort(403)

    # The key is valid, now see if it has permission to access this route
    flask_route = request.endpoint.split(".")[0].replace("-", "_")
    if not api_key.can_access(flask_route, token):
        abort(403)


def authorize_blueprint_v2():
    """Determine if the request to a blueprint has been properly authorized."""
    # Was an Authorization header sent?
    if "Authorization" not in request.headers:
        abort(400)

    # Attempt to get the API key and validate it
    try:
        token = get_auth_token()
        if not keys.exists(token):
            raise KeyError
    except (KeyError, IndexError):
        abort(403)

    # The key is valid, now see if it has permission to access this route
    flask_route = request.endpoint.split(".")[0].replace("-", "_")
    if not keys.can_access(flask_route, token):
        abort(403)


def authorize_route(func):
    """Protect a single route.

    This decorator is useful when a single endpoint
    needs to be protected but not the entire blueprint.
    """

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        authorize_blueprint()
        return func(*args, **kwargs)

    return wrap


def authorize_route_v2(func):
    """Protect a single route.

    This decorator is useful when a single endpoint
    needs to be protected but not the entire blueprint.
    """

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        authorize_blueprint_v2()
        return func(*args, **kwargs)

    return wrap


def get_auth_token() -> str:
    """Attempt to extract the auth token from the request."""
    return request.headers["Authorization"].split("Bearer")[1].strip()


def fake_authorize():
    """Just a no-op for dummy authorization."""


def send_deprecation_warning(endpoint: str, response) -> dict[str, str]:
    """Send a deprecation notice with a request."""
    response.headers["X-Deprecation-Notice"] = f"Replaced by /v2/{endpoint} endpoint"
    return response
