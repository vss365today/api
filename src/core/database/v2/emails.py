from flask import current_app
from sqlalchemy.exc import IntegrityError

from src.core.database.models import Email, db


__all__ = ["create", "delete", "get_all", "get_emails_totalling"]


def create(address: str) -> bool:
    """Add an email address."""
    try:
        db.session.add(Email(address=address))
        db.session.commit()
        current_app.logger.debug(f"Email '{address}' added to mailing list.")
        return True

    # We hit some DB error
    except IntegrityError as exc:
        db.session.rollback()
        current_app.logger.exception(exc)
        return False


def delete(address: str) -> None:
    """Remove an email address."""
    qs = db.select(Email).filter_by(address=address)
    if (email := db.session.execute(qs).scalars().first()) is not None:
        db.session.delete(email)
        db.session.commit()
    current_app.logger.debug("Email removed from subscription list.")
    return None


def get_all() -> list[Email]:
    """Get all email addresses."""
    return db.session.execute(db.select(Email).order_by(Email.address)).scalars().all()


def get_emails_totalling(limit: int, /) -> list[Email]:
    """Get emails from the database up to the limit."""
    return (
        db.session.execute(db.select(Email).limit(limit).order_by(Email.address))
        .scalars()
        .all()
    )
