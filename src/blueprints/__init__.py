from typing import Callable, Optional

from flask import Blueprint

from src.core.auth_helpers import authorize_request


def _factory(
    partial_module_string: str,
    url_prefix: str,
    api_version: str,
    protected: bool = False,
    auth_function: Optional[Callable] = None
) -> Blueprint:
    # Build out the module import path
    endpoint_folder = "protected" if protected else "public"
    import_name = [
        "src", "blueprints", api_version,
        endpoint_folder, partial_module_string
    ]
    import_path: str = ".".join(import_name)

    # Actually create the blueprint
    blueprint = Blueprint(
        partial_module_string,
        import_path,
        url_prefix=f"/{api_version}{url_prefix}"
    )

    # This endpoint is not to be publicly used
    if protected:
        # Protected endpoints must have an authorization method
        if auth_function is None:
            raise NotImplementedError(
                "An authorization method must be given for protected endpoints!"  # noqa
            )

        # Protect the endpoint with an authorization routine
        blueprint.before_request(auth_function)
    return blueprint


browse = _factory("browse", "/browse", "v1")
prompt = _factory("prompt", "/prompt", "v1")
search = _factory("search", "/search", "v1")
subscription = _factory(
    "subscription",
    "/subscription",
    "v1",
    True,
    authorize_request
)

all_blueprints = (browse, prompt, search,)
