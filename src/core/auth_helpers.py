from functools import wraps
from typing import NoReturn

from flask import request
from flask_smorest import abort

from src.core.database.v2 import keys


__all__ = [
    "protect_blueprint",
    "require_permission",
    "fake_authorize",
]


ALL_PERMISSIONS = keys.available_permissions()


def protect_blueprint(*perms: str) -> None | NoReturn:
    # Sanity-check myself to make sure I don't use an non-existent permission
    all_perms = set(ALL_PERMISSIONS)
    requested_perms = set(perms)
    if unknown := requested_perms - all_perms:
        abort(
            403,
            message=f"Unknown permissions attempted to be used: {','.join(unknown)}.",
        )

    # Check if the token has the proper permissions
    token = get_token_from_request()
    if not keys.can_access_v2(token, requested_perms):
        abort(
            403,
            message="API key does not contain all required permissions for this endpoint.",
        )
    return None


def require_permission(*perms: str):
    """Protect a single endpoint with the specified permissions.

    This decorator is useful when a single endpoint
    needs to be protected but not the entire blueprint.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            protect_blueprint(*perms)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_auth_token() -> str:
    """Attempt to extract the auth token from the request."""
    return request.headers["Authorization"].split("Bearer")[1].strip()


def get_token_from_request() -> str | NoReturn:
    """Extract an API key/token from an active request."""
    # Was an Authorization header sent?
    if "Authorization" not in request.headers:
        abort(400, message="Missing HTTP Authorization header.")

    # Attempt to get the API key and validate it
    try:
        token = get_auth_token()
        if not keys.exists(token):
            raise KeyError
        return token
    except (KeyError, IndexError):
        abort(403, message="Invalid API key provided.")


def fake_authorize():
    """Just a no-op for dummy authorization."""
