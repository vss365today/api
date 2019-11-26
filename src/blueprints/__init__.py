from typing import Callable, Optional

from flask import Blueprint


def _factory(
    partial_module_string: str,
    url_prefix: str,
    api_version: str,
    login_required: bool = False,
    auth_function: Optional[Callable] = None
) -> Blueprint:
    import_name = f"src.blueprints.{api_version}.public.{partial_module_string}"
    blueprint = Blueprint(
        partial_module_string,
        import_name,
        url_prefix=f"/{api_version}/{url_prefix}"
    )

    # This blueprint can only be accessed via a login
    if login_required:
        # blueprint.before_request(login)

        # But only allowed people can see it
        if auth_function is not None:
            pass
            # blueprint.before_request(auth_function)

    return blueprint


prompt = _factory("prompt", "prompt", "v1")
search = _factory("search", "search", "v1")
writer = _factory("writer", "writer", "v1")

all_blueprints = (prompt, search, writer)
