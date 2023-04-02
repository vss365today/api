from functools import partial
from typing import Callable

from flask import Blueprint
from flask_smorest import Blueprint as APIBlueprint

from src.core import auth_helpers as v1_auth
from src.core import auth_helpers_v2 as v2_auth


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
        partial_module_string,
        import_path,
        url_prefix=f"/v1/{url_prefix}",
    )

    # Protect the endpoint with an authorization routine
    # if one was given
    if auth_function is not None:
        blueprint.before_request(auth_function)

    # This endpoint has been deprecated, attach a HTTP header
    # stating this and transition info
    if new_endpoint is not None:
        x = partial(v1_auth.send_deprecation_warning, new_endpoint)
        blueprint.after_request(x)  # type: ignore

    return blueprint


# v1 endpoints
browse = _factory("browse", "browse")  # documented
host = _factory("host", "host", new_endpoint="hosts")  # documented
prompt = _factory("prompt", "prompt", new_endpoint="prompts")  # documented
search = _factory("search", "search")  # documented
settings = _factory("settings", "settings", v1_auth.authorize_blueprint)  # documented
all_blueprints = (
    browse,
    host,
    prompt,
    search,
    settings,
)

# v2 endpoints
archive = _api_factory(
    "archive",
    "archive",
    description="Manage the Prompt archive.",
)  # done

emails = _api_factory(
    "emails",
    "emails",
    partial(v2_auth.protect_blueprint, "emails"),
    description="Manage email subscriptions.",
)  # done

hosts = _api_factory(
    "hosts",
    "hosts",
    description="Manage Hosts.",
)  # done

keys = _api_factory(
    "keys",
    "keys",
    partial(v2_auth.protect_blueprint, "keys"),
    description="Manage API key permissions.",
)  # done

notifications = _api_factory(
    "notifications",
    "notifications",
    partial(v2_auth.protect_blueprint, "notifications"),
    description="Manage email notifications.",
)  # done

prompts = _api_factory(
    "prompts",
    "prompts",
    description="Manage Prompts.",
)  # done

v2_blueprints = (archive, emails, hosts, keys, notifications, prompts)
