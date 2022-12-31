from functools import partial
from typing import Callable

from flask import Blueprint
from flask_smorest import Blueprint as APIBlueprint

from src.core.auth_helpers import (
    authorize_blueprint,
    authorize_blueprint_v2,
    send_deprecation_warning,
)


def _api_factory(
    partial_module_string: str,
    url_prefix: str,
    auth_function: Callable | None = None,
    *,
    description: str = "",
) -> APIBlueprint:
    """Register a flask_smorest blueprint."""
    # Build out the module import path
    endpoint_folder = "public" if auth_function is None else "protected"
    import_name = [
        "src",
        "views",
        endpoint_folder,
        partial_module_string,
    ]
    import_path: str = ".".join(import_name)

    # Actually create the blueprint
    blueprint = APIBlueprint(
        partial_module_string,
        import_path,
        url_prefix=f"/v2/{url_prefix}",
        description=description,
    )

    # Protect the endpoint with an authorization routine
    # if one was given
    if auth_function is not None:
        blueprint.before_request(auth_function)
        blueprint.description += (
            "\n\n<strong>Note</strong>: This endpoint can only be used with an API key "
            "with the appropriate permissions."
        )
    return blueprint


def _factory(
    partial_module_string: str,
    url_prefix: str,
    auth_function: Callable | None = None,
    new_endpoint: str | None = None,
) -> Blueprint:
    """Generate a blueprint registration."""
    # Build out the module import path
    endpoint_folder = "public" if auth_function is None else "protected"
    import_name = [
        "src",
        "blueprints",
        "v1",
        endpoint_folder,
        partial_module_string,
    ]
    import_path: str = ".".join(import_name)

    # Actually create the blueprint
    blueprint = Blueprint(
        partial_module_string, import_path, url_prefix=f"/v1/{url_prefix}"
    )

    # Protect the endpoint with an authorization routine
    # if one was given
    if auth_function is not None:
        blueprint.before_request(auth_function)

    # This endpoint has been deprecated, attach a HTTP header
    # stating this and transition info
    if new_endpoint is not None:
        x = partial(send_deprecation_warning, new_endpoint)
        blueprint.after_request(x)  # type: ignore

    return blueprint


# v1 endpoints
archive = _factory("archive", "archive")  # documented
broadcast = _factory(
    "broadcast",
    "broadcast",
    authorize_blueprint,
    new_endpoint="notifications",
)  # documented
browse = _factory("browse", "browse")  # documented
host = _factory("host", "host", new_endpoint="hosts")  # documented
prompt = _factory("prompt", "prompt")  # documented
search = _factory("search", "search")  # documented
settings = _factory("settings", "settings", authorize_blueprint)  # documented
all_blueprints = (
    archive,
    broadcast,
    browse,
    host,
    prompt,
    search,
    settings,
)

# v2 endpoints
emails = _api_factory(
    "emails",
    "emails",
    authorize_blueprint_v2,
    description="Manage email subscriptions.",
)  # done

hosts = _api_factory(
    "hosts",
    "hosts",
    description="Manage hosts.",
)
keys = _api_factory(
    "keys",
    "keys",
    authorize_blueprint_v2,
    description="Manage API key permissions.",
)  # done

notifications = _api_factory(
    "notifications",
    "notifications",
    authorize_blueprint_v2,
    description="Manage email notifications.",
)

v2_blueprints = (emails, keys)
