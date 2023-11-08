from functools import partial
from typing import Callable

from flask_smorest import Blueprint as APIBlueprint

from src.core import auth_helpers


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

    # Protect the endpoint with an authorization routine if one was given
    if auth_function is not None:
        blueprint.before_request(auth_function)
        blueprint.description += (
            "\n\n<strong>Note</strong>: This endpoint can only be used with an API key "
            "with the appropriate permissions."
        )
    else:
        blueprint.description += (
            "\n\n<strong>Note</strong>: Some endpoints may require an API key "
            "with the appropriate permissions."
        )

    return blueprint


# v2 endpoints
archive = _api_factory(
    "archive",
    "archive",
    description="Manage the Prompt archive.",
)

browse = _api_factory(
    "browse",
    "browse",
    description="Browse recorded Prompts.",
)

emails = _api_factory(
    "emails",
    "emails",
    partial(auth_helpers.protect_blueprint, "emails"),
    description="Manage email subscriptions.",
)

hosts = _api_factory(
    "hosts",
    "hosts",
    description="Manage Hosts.",
)

keys = _api_factory(
    "keys",
    "keys",
    partial(auth_helpers.protect_blueprint, "keys"),
    description="Manage API key permissions.",
)

notifications = _api_factory(
    "notifications",
    "notifications",
    partial(auth_helpers.protect_blueprint, "notifications"),
    description="Manage email notifications.",
)

prompts = _api_factory(
    "prompts",
    "prompts",
    description="Manage Prompts.",
)

search = _api_factory(
    "search",
    "search",
    description="Search the Prompts by Hosts and arbitrary queries.",
)

v2_blueprints = (
    archive,
    browse,
    emails,
    hosts,
    keys,
    notifications,
    prompts,
    search,
)
