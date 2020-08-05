from typing import Literal

from sqlalchemy.exc import DBAPIError, IntegrityError

from src.core.database.base import connect_to_db

__all__ = ["email_create", "email_delete"]


def email_create(addr: str) -> bool:
    """Add a subscription email address."""
    try:
        sql = "INSERT INTO emails (email) VALUES (:addr)"
        with connect_to_db() as db:
            db.query(sql, addr=addr.lower())
        return True

    # That address aleady exists in the database.
    # However, to prevent data leakage, pretend it added
    except IntegrityError as exc:
        print(f"New subscription exception: {exc}")
        print(addr)
        return True

    # An error occurred trying to record the email
    except DBAPIError as exc:
        print(f"New subscription exception: {exc}")
        print(addr)
        return False


def email_delete(addr: str) -> Literal[True]:
    """Remove a subscription email address."""
    sql = "DELETE FROM emails WHERE email = :addr"
    with connect_to_db() as db:
        db.query(sql, addr=addr)
    return True
