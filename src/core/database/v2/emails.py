from flask import current_app
from sqlalchemy.exc import IntegrityError

from src.core.database.models import Email, db


__all__ = ["create", "delete", "get_all"]


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
    db.session.delete(Email.query.filter_by(address=address).first())
    db.session.commit()
    current_app.logger.debug("Email removed from subscription list.")
    return None


def get_all() -> list[Email]:
    """Get all email addresses."""
    return Email.query.order_by(Email.address).all()
