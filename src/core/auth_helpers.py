import functools

from flask import request
from flask import abort

from src.core.database import api_key_is_valid, api_key_has_permission


__all__ = ["authorize_blueprint", "authorize_route", "fake_authorize"]


def authorize_blueprint():
    """Determine if the request to a blueprint has been properly authorized."""
    # Was an Authorization header sent?
    if "Authorization" in request.headers:
        bearer = request.headers["Authorization"]
    else:
        abort(400)

    # Attempt to get the API key and validate it
    try:
        api_key = bearer.split("Bearer")[1].strip()
        if not api_key_is_valid(api_key):
            raise KeyError
    except (KeyError, IndexError):
        abort(403)

    # The key is valid, now see if it has permission to access this route
    flask_route = request.endpoint.split(".")[0]
    if not api_key_has_permission(flask_route, api_key):
        abort(403)


def authorize_route(func):
    """Protect a single route.

    This decorator is useful when a single endpoint
    needs to be protected but not the entire blueprint.
    """

    @functools.wraps(func)
    def wrap(*args, **kwargs):
        # TODO Change this back to authorize_blueprint
        fake_authorize()
        return func(*args, **kwargs)

    return wrap


def fake_authorize():
    """Just a no-op for dummy authorization."""
