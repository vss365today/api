from typing import Callable, Optional

from flask import Blueprint
from flask_smorest import Blueprint as APIBlueprint

from src.core.auth_helpers import authorize_blueprint


def _api_factory(
    partial_module_string: str,
    url_prefix: str,
    auth_function: Optional[Callable] = None,
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
        partial_module_string, import_path, url_prefix=f"/v2/{url_prefix}"
    )

    # Protect the endpoint with an authorization routine
    # if one was given
    if auth_function is not None:
        blueprint.before_request(auth_function)
    return blueprint


def _factory(
    partial_module_string: str,
    url_prefix: str,
    auth_function: Optional[Callable] = None,
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
    return blueprint


# v1 endpoints
api_key = _factory("api_key", "api-key", authorize_blueprint)
archive = _factory("archive", "archive")
broadcast = _factory("broadcast", "broadcast", authorize_blueprint)
browse = _factory("browse", "browse")
host = _factory("host", "host")
prompt = _factory("prompt", "prompt")
search = _factory("search", "search")
subscription = _factory("subscription", "subscription")
settings = _factory("settings", "settings", authorize_blueprint)
all_blueprints = (
    api_key,
    archive,
    broadcast,
    browse,
    host,
    prompt,
    search,
    subscription,
    settings,
)

# v2 endpoints
keys = _api_factory("keys", "keys", authorize_blueprint)
v2_blueprints = (keys,)
