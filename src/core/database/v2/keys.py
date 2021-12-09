from secrets import token_hex

from flask import current_app
from sqlalchemy.exc import DataError

from src.core.database.models import ApiKey, ApiKeyAudit, db


__all__ = ["can_access", "create", "delete", "get", "get_all", "update"]


# def can_access(route: str, token: str) -> bool:
#     """Determine if the given API key has permission to access a route."""
#     sql = f"SELECT has_{route} FROM api_keys WHERE token = :token"
#     with connect_to_db() as db:
#         return bool(db.query(sql, token=token).one()[0])


def create(data: dict) -> dict | False:
    """Create an API key with specified permissions."""
    try:
        new_token = token_hex()
        key = ApiKey(key=new_token, **data)
        db.session.add(key)
        db.session.commit()
        return {"token": new_token}

    # We hit some DB error
    except DataError as exc:
        db.session.rollback()
        current_app.logger.exception(exc)
        return False


def delete(key: str) -> bool:
    """Delete an API key."""
    if ApiKey.exists(key):
        ApiKey.delete(key)
        return True
    return False


def get(key: str) -> ApiKey | None:
    """Get an API key's permissions."""
    # That key doesn't exist
    if not ApiKey.exists(key):
        return None
    return ApiKey.query.filter_by(key=key).first()


def get_all() -> list[ApiKey]:
    """Get all recorded API key's permissions."""
    return ApiKey.query.order_by(ApiKey.date_created).all()


# def update(permissions: dict) -> bool:
#     """Update an API key's permissions."""
#     # Convert the boolean fields to integers
#     permissions = __bool_to_int(permissions)

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
