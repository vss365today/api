from secrets import token_hex
from typing import Dict, List, Literal, Optional

from sqlalchemy.exc import DataError

from src.core.database.core import connect_to_db
from src.core.models.v1.ApiKey import ApiKey


__all__ = ["can_access", "create", "delete", "exists", "get", "get_all", "update"]


def __bool_to_int(records: dict) -> dict:
    """Convert Boolean values to integer values."""
    for k, v in records.items():
        if isinstance(v, bool):
            records[k] = int(v)
    return records


def can_access(route: str, token: str) -> bool:
    """Determine if the given API key has permission to access a route."""
    sql = f"SELECT has_{route} FROM api_keys WHERE token = :token"
    with connect_to_db() as db:
        return bool(db.query(sql, token=token).one()[0])


def create(permissions: dict) -> Dict[str, str]:
    """Create an API key with specified permissions."""
    # Convert the boolean fields to integers
    permissions = __bool_to_int(permissions)

    # Generate a new token for the API key
    new_token = token_hex()

    # Create the record
    sql = """INSERT INTO api_keys (
        token, `desc`, has_api_key, has_archive,
        has_broadcast, has_host, has_prompt,
        has_settings, has_subscription
    ) VALUES (
        :token, :desc, :has_api_key, :has_archive,
        :has_broadcast, :has_host, :has_prompt,
        :has_settings, :has_subscription
    )
    """
    try:
        with connect_to_db() as db:
            db.query(sql, token=new_token, **permissions)
            return {"token": new_token}
    except DataError as exc:
        print(f"API key creation exception: {exc}")
        return {}


def delete(token: str) -> Literal[True]:
    """Delete an API key."""
    sql = "DELETE FROM api_keys WHERE token = :token"
    with connect_to_db() as db:
        db.query(sql, token=token)
        return True


def exists(token: str) -> bool:
    """Determine if an API key exists."""
    sql = "SELECT 1 FROM api_keys WHERE token = :token"
    with connect_to_db() as db:
        return bool(db.query(sql, token=token).one())


def get(token: str) -> Optional[ApiKey]:
    """Get an API key's permissions."""
    sql = "SELECT * FROM api_keys WHERE token = :token LIMIT 1"
    with connect_to_db() as db:
        record = db.query(sql, token=token).one()
        return ApiKey(record) if record else None


def get_all() -> List[ApiKey]:
    """Get all recorded API key's permissions."""
    sql = "SELECT * FROM api_keys"
    with connect_to_db() as db:
        return [ApiKey(record) for record in db.query(sql)]


def update(permissions: dict) -> bool:
    """Update an API key's permissions."""
    # Convert the boolean fields to integers
    permissions = __bool_to_int(permissions)

    # Update the key
    sql = """UPDATE api_keys
    SET
        `desc` = :desc,
        has_api_key = :has_api_key,
        has_archive = :has_archive,
        has_broadcast = :has_broadcast,
        has_host = :has_host,
        has_prompt = :has_prompt,
        has_settings = :has_settings,
        has_subscription = :has_subscription
    WHERE token = :token
    """
    try:
        with connect_to_db() as db:
            db.query(sql, **permissions)
            return True
    except DataError as exc:
        print(f"API key update exception: {exc}")
        return False
