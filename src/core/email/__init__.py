from typing import Dict

import requests

from flask import current_app
from flask import render_template


__all__ = ["construct", "render", "send", "make_and_send"]


def construct(email_addr: str, subject: str, content: dict) -> dict:
    """Construct a Mailgun email dictionary."""
    return {
        "from": (
            f'{current_app.config["APP_NAME"]} '
            f'<noreply@{current_app.config["APP_DOMAIN"]}>'
        ),
        "to": email_addr,
        "subject": subject,
        "text": content["text"],
        "html": content["html"],
    }


def render(template_name: str, **render_opts: str) -> Dict[str, str]:
    """Render a email template with all info."""
    rendered = {
        "html": render_template(f"emails/{template_name}.jinja2", **render_opts),
        "text": render_template(f"emails/{template_name}.txt", **render_opts),
    }
    return rendered


def send(email: Dict[str, str]) -> bool:
    """Send out a completed email."""
    # If email sending is not configured, just pretend the email
    # sent out correctly instead of making the caller handle the special case
    if not current_app.config["ENABLE_EMAIL_SENDING"]:
        return True

    # Attempt to send out the email
    try:
        r = requests.post(
            f'https://api.mailgun.net/v3/{current_app.config["MG_DOMAIN"]}/messages',
            auth=("api", current_app.config["MG_API_KEY"]),
            data=email,
        )
        r.raise_for_status()
        return True

    # Some error occurred while attempting to send the email
    except requests.HTTPError as exc:
        print(exc)
    return False


def make_and_send(
    email_addr: str, subject: str, template_name: str, **render_opts: str
) -> bool:
    """Convenience function to construct and send an email in one call."""
    email_content = render(template_name, **render_opts)
    email_msg = construct(email_addr, subject, email_content)
    return send(email_msg)
