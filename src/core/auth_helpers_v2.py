import functools
from typing import NoReturn

from flask import abort, request

from src.core.database.v2 import keys


__all__ = [
    "authorize_blueprint",
    "authorize_route",
    "require_permission",
    "fake_authorize",
]


ALL_PERMISSIONS = keys.available_permissions()


def authorize_blueprint():
    """Determine if the request to a blueprint has been properly authorized."""
    # The key is valid, now see if it has permission to access this route,
    # converting v2 route names to v1 route names as needed
    token = get_token_from_request()
    flask_route = request.endpoint.split(".")[-2].lower()
    if not keys.can_access(flask_route, token):
        abort(403)


def require_permission(*perms: str):
    """Determine if the request to an endpoint has been properly authorized."""

    def decorator(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            # Sanity-check myself to make sure I don't use an non-existent permission
            all_perms = set(ALL_PERMISSIONS)
            requested_perms = set(perms)
            if unknown := requested_perms - all_perms:
                abort(
                    403,
                    f"Unknown permissions attempted to be used: {','.join(unknown)}",
                )

            # Check if the token has the proper permissions
            token = get_token_from_request()
            if not keys.can_access_v2(token, requested_perms):
                abort(
                    403,
                    "API key does not contain all required permissions for this endpoint.",
                )

            return func(*args, **kwargs)

        return wrap

    return decorator


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


def get_auth_token() -> str:
    """Attempt to extract the auth token from the request."""
    return request.headers["Authorization"].split("Bearer")[1].strip()


def get_token_from_request() -> str | NoReturn:
    """Extract an API key/token from an active request."""
    # Was an Authorization header sent?
    if "Authorization" not in request.headers:
        abort(400)

    # Attempt to get the API key and validate it
    try:
        token = get_auth_token()
        if not keys.exists(token):
            raise KeyError
        return token
    except (KeyError, IndexError):
        abort(403)


def fake_authorize():
    """Just a no-op for dummy authorization."""
