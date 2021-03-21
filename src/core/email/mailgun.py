from flask import current_app
import requests

__all__ = [
    "mailing_list_addr_get",
    "subscription_email_create",
    "subscription_email_delete",
    "validate_email_address",
]


def mailing_list_addr_get() -> str:
    """Construct the Mailgun mailing list address."""
    # Construct the mailing list address. It is written this way
    # because the development and production lists are different
    # and we need to use the proper one depending on the env
    return f'{current_app.config["MG_MAILING_LIST_ADDR"]}@{current_app.config["MG_DOMAIN"]}'  # skipcq: FLK-E501


def subscription_email_create(addr: str) -> requests.Response:
    """Add a subscription email address."""
    mg_list_addr = mailing_list_addr_get()
    return requests.post(
        f"https://api.mailgun.net/v3/lists/{mg_list_addr}/members",
        auth=("api", current_app.config["MG_API_KEY"]),
        data={"upsert": True, "subscribed": True, "address": addr},
    )


def subscription_email_delete(addr: str) -> requests.Response:
    """Remove a subscription email address."""
    mg_list_addr = mailing_list_addr_get()
    return requests.delete(
        f"https://api.mailgun.net/v3/lists/{mg_list_addr}/members/{addr}",
        auth=("api", current_app.config["MG_API_KEY"]),
    )


def validate_email_address(addr: str) -> bool:
    """Validate an email address using the Mailgun Email Validation API."""
    r = requests.get(
        "https://api.mailgun.net/v4/address/validate",
        auth=("api", current_app.config["MG_API_KEY"]),
        params={"address": addr},
    ).json()

    # The address can be added if it's marked as deliverable
    return r["result"] == "deliverable"
