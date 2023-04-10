from json import dumps
from typing import Any

from flask import current_app, render_template
import requests

from src.configuration import get_secret
from src.core.models.v2.EmailTemplate import EmailTemplate


__all__ = ["batch_construct", "construct", "render", "send", "make_and_send"]


def batch_construct(
    mailing_list: list[str], subject: str, content: EmailTemplate
) -> dict:
    """Construct a Mailgun email dictionary for batching sending.

    https://documentation.mailgun.com/en/latest/user_manual.html#batch-sending
    """
    # Create a Recipient Variables dict to generate unique messages
    rvs = {addr: {"email": addr} for addr in mailing_list}

    return {
        "from": (
            f'{current_app.config["APP_NAME"]} <noreply@{get_secret("MG_DOMAIN")}>'
        ),
        "to": mailing_list,
        "subject": subject,
        "text": content.text,
        "html": content.html,
        "recipient-variables": dumps(rvs),
    }


def construct(email_addr: str, subject: str, content: EmailTemplate) -> dict:
    """Construct a Mailgun email dictionary."""
    return {
        "from": (
            f'{current_app.config["APP_NAME"]} <noreply@{get_secret("MG_DOMAIN")}>'
        ),
        "to": email_addr,
        "subject": subject,
        "text": content.text,
        "html": content.html,
    }


def render(template_name: str, **render_opts: str) -> EmailTemplate:
    """Render a email message with text and HTML sections."""
    return EmailTemplate(
        render_template(f"emails/{template_name}.txt", **render_opts),
        render_template(f"emails/{template_name}.jinja2", **render_opts),
    )


def send(email: dict[str, str]) -> bool:
    """Send out a completed email."""
    # If email sending is not configured, just pretend the email
    # sent out correctly instead of making the caller handle the special case
    if not current_app.config["ENABLE_EMAIL_SENDING"]:
        return True

    # Attempt to send out the email
    r = requests.post(
        f'https://api.mailgun.net/v3/{get_secret("MG_DOMAIN")}/messages',
        auth=("api", get_secret("MG_API_KEY")),
        data=email,
    )
    r.raise_for_status()
    return True


def make_and_send(
    email_addr: str, subject: str, template_name: str, **render_opts: Any
) -> bool:
    """Helper function to construct and send a single email."""
    email_content = render(template_name, **render_opts)
    email_msg = construct(email_addr, subject, email_content)
    return send(email_msg)
