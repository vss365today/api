import functools

from flask import request
from flask import abort

from jwt import decode
from jwt.exceptions import DecodeError, InvalidSignatureError

from src.core.database import is_auth_token_valid


__all__ = ["authorize_blueprint", "authorize_route", "fake_authorize"]


def authorize_blueprint():
    """Determine if the request to a blueprint has been properly authorized."""
    # Was an Authorization header sent?
    if "Authorization" in request.headers:
        bearer = request.headers["Authorization"]
    else:
        abort(400)

    # No token was given or the provided token is not in the proper format
    try:
        identity = bearer.split("Bearer")[1].strip()
    except IndexError:
        abort(422)

    # Decode the passed token
    try:
        token = decode(identity, verify=True, algorithms=["HS256"])
        if not is_auth_token_valid(token):
            raise KeyError

    # The given username and token combo is not valid
    except (KeyError, DecodeError, InvalidSignatureError):
        abort(401)


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


def fake_authorize():
    """Just a no-op for dummy authorization."""
    pass
