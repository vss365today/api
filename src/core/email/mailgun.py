import json

import requests

from src.configuration import get_config, get_secret


__all__ = [
    "mailing_list",
    "create",
    "delete",
    "validate",
]


def mailing_list() -> str:
    """Construct the Mailgun mailing list address."""
    # Construct the mailing list address. It is written this way
    # because the development and production lists are different
    # and we need to use the proper one depending on the env
    return f'{get_config("MG_MAILING_LIST_ADDR")}@{get_secret("MG_DOMAIN")}'


def create(addresses: list[str]) -> requests.Response:
    """Add a subscription email address."""
    members = [{"subscribed": True, "address": address} for address in addresses]
    return requests.post(
        f"https://api.mailgun.net/v3/lists/{mailing_list()}/members.json",
        auth=("api", get_secret("MG_API_KEY")),
        data={"upsert": True, "members": json.dumps(members)},
    )


def delete(addr: str) -> requests.Response:
    """Remove a subscription email address."""
    return requests.delete(
        f"https://api.mailgun.net/v3/lists/{mailing_list()}/members/{addr}",
        auth=("api", get_secret("MG_API_KEY")),
    )


def validate(addr: str) -> bool:
    """Validate an email address using the Mailgun Email Verification service."""
    # Assume the address is valid if we can't send out emails
    if not get_config("ENABLE_EMAIL_SENDING"):
        return True

    r = requests.get(
        "https://api.mailgun.net/v4/address/validate",
        auth=("api", get_secret("MG_API_KEY")),
        params={"address": addr},
    ).json()

    # The address can be added if it's marked as deliverable
    return r["result"] == "deliverable"
