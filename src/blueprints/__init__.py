from typing import Callable, Optional

from flask import Blueprint

from src.core.auth_helpers import fake_authorize


def _factory(
    partial_module_string: str,
    url_prefix: str,
    api_version: str,
    auth_function: Optional[Callable] = None,
) -> Blueprint:
    # Build out the module import path
    endpoint_folder = "public" if auth_function is None else "protected"
    import_name = [
        "src",
        "blueprints",
        api_version,
        endpoint_folder,
        partial_module_string,
    ]
    import_path: str = ".".join(import_name)

    # Actually create the blueprint
    blueprint = Blueprint(
        partial_module_string, import_path, url_prefix=f"/{api_version}{url_prefix}"
    )

        # Protect the endpoint with an authorization routine
    # if one was given
    if auth_function is not None:
        blueprint.before_request(auth_function)
    return blueprint


account = _factory("account", "/account", "v1")
browse = _factory("browse", "/browse", "v1")
prompt = _factory("prompt", "/prompt", "v1")
search = _factory("search", "/search", "v1")
subscription = _factory("subscription", "/subscription", "v1")
host = _factory("host", "/host", "v1", fake_authorize)

all_blueprints = (browse, host, prompt, search, subscription)
