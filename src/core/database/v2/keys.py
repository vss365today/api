from secrets import token_hex
from typing import Literal

from flask import current_app
from sqlalchemy.exc import DataError

from src.core.database.models import ApiKey, ApiKeyAudit, db


__all__ = ["can_access", "create", "delete", "get", "get_all", "update"]


def can_access(route: str, token: str) -> bool:
    """Determine if the given API key has permission to access a route."""
    route = "archive"
    return (
        ApiKey.query.with_entities(getattr(ApiKey, f"has_{route}"))
        .filter_by(token=token)
        .first()[0]
    )


def create(data: dict) -> dict | Literal[False]:
    """Create an API key with specified permissions."""
    try:
        new_token = token_hex()
        key = ApiKey(token=new_token, **data)
        db.session.add(key)
        db.session.commit()
        return {"token": new_token}

    # We hit some DB error
    except DataError as exc:
        db.session.rollback()
        current_app.logger.exception(exc)
        return False


def delete(token: str) -> bool:
    """Delete an API key."""
    if ApiKey.exists(token):
        ApiKey.delete(token)
        return True
    return False


def get(token: str) -> ApiKey | None:
    """Get an API key's permissions."""
    # That key doesn't exist
    if not ApiKey.exists(token):
        return None
    return ApiKey.query.filter_by(token=token).first()


def get_all() -> list[ApiKey]:
    """Get all recorded API key's permissions."""
    return ApiKey.query.order_by(ApiKey.date_created).all()


# def update(permissions: dict) -> bool:
#     """Update an API key's permissions."""

#     # Update the key
#     sql = """UPDATE api_keys
#     SET
#         `desc` = :desc,
#         has_api_key = :has_api_key,
#         has_archive = :has_archive,
#         has_broadcast = :has_broadcast,
#         has_host = :has_host,
#         has_prompt = :has_prompt,
#         has_settings = :has_settings,
#         has_subscription = :has_subscription
#     WHERE token = :token
#     """
#     try:
#         with connect_to_db() as db:
#             db.query(sql, **permissions)
#             return True
#     except DataError as exc:
#         print(f"API key update exception: {exc}")
#         return False
