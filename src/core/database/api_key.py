from typing import Dict, List, Optional
from secrets import token_hex

from sqlalchemy.exc import DataError

from src.core.database import __connect_to_db
from src.core.models.v1.ApiKey import ApiKey


__all__ = ["create", "delete", "exists", "has_permission", "get", "get_all", "update"]


def __int_to_bool(records: dict) -> dict:
    for k, v in records.items():
        if isinstance(v, int):
            records[k] = bool(v)
    return records


def __bool_to_int(records: dict) -> dict:
    for k, v in records.items():
        if isinstance(v, bool):
            records[k] = int(v)
    return records


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
        has_subscription
    ) VALUES (
        :token, :desc, :has_api_key, :has_archive,
        :has_broadcast, :has_host, :has_prompt,
        :has_subscription
    )
    """
    try:
        with __connect_to_db() as db:
            db.query(sql, token=new_token, **permissions)
            return {"token": new_token}
    except DataError as exc:
        print(f"API key creation exception: {exc}")
        return {}


def delete(token: str) -> bool:
    """Delete an API key."""
    sql = "DELETE FROM api_keys WHERE token = :token"
    with __connect_to_db() as db:
        return bool(db.query(sql, token=token).one())


def exists(token: str) -> bool:
    """Determine if an API key exists."""
    sql = "SELECT 1 FROM api_keys WHERE token = :token"
    with __connect_to_db() as db:
        return bool(db.query(sql, token=token).one())


def get(token: str) -> Optional[ApiKey]:
    """Get an API key's permissions."""
    sql = "SELECT * FROM api_keys WHERE token = :token LIMIT 1"
    with __connect_to_db() as db:
        record = db.query(sql, token=token).one()
        return ApiKey(record) if record else None


def get_all(token: str) -> List[ApiKey]:
    """Get an API key's permissions."""
    sql = "SELECT * FROM api_keys"
    with __connect_to_db() as db:
        return [ApiKey(record) for record in db.query(sql, token=token)]


def has_permission(route: str, token: str) -> bool:
    """Determine if the given API key has permission to access a route."""
    sql = f"SELECT has_{route} FROM api_keys WHERE token = :token"
    with __connect_to_db() as db:
        return bool(db.query(sql, token=token).one()[0])


def update(permissions: dict):
    """Update an API key's permissions."""
    raise NotImplementedError

    # Convert the boolean fields to integers
    permissions = __bool_to_int(permissions)
