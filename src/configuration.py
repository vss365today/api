import json
from pathlib import Path
from typing import Any

import sys_vars
from flask import current_app


__all__ = ["get_app_config", "get_secrets_list", "get_config", "get_secret"]


def get_app_config(config_file: str) -> dict:
    """Collect the app configuration values.

    @param {str} config_file - The config file name to use.
    @return {dict} - A dictionary with all config values.
    """
    path = (Path() / "configuration" / f"{config_file}.json").resolve()
    file_content = json.loads(path.read_text())

    # Immediately add the app-specific values to the final values
    # because there is no need to fetch these from an outside source
    app_config: dict[str, Any] = {}
    app_config.update(file_content["appConfig"])
    return app_config


def get_secrets_list(env: str) -> dict[str, set]:
    """Create a list of available app secrets, without their values."""
    path = (Path() / "configuration").resolve()
    default_file = json.loads((path / "default.json").read_text())
    env_file = json.loads((path / f"{env}.json").read_text())

    config_keys: set[str] = set()
    config_keys.update(default_file["secrets"], env_file["secrets"])
    return {"AVAILABLE_SECRETS": config_keys}


def get_config(key: str) -> Any:
    """Get an app config value, confirming it is available for use."""
    if key not in current_app.config:
        raise sys_vars.SysVarNotFoundError(
            f'Config "{key}" is not available in this app'
        )
    return current_app.config[key]


def get_secret(key: str) -> str:
    """Get an app secret value, confirming it is available for use."""
    if key not in current_app.config["AVAILABLE_SECRETS"]:
        raise sys_vars.SysVarNotFoundError(
            f'Secret "{key}" is not available in this app'
        )
    return sys_vars.get(key)
