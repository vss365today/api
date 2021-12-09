# coding: utf-8
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DDL, Column, Date, DateTime, ForeignKey, String, event, text
from sqlalchemy.types import Boolean
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.orm import relationship


db = SQLAlchemy()


__all__ = [
    "ALL_TRIGGERS",
    "ApiKey",
    "ApiKeyAudit",
    "Email",
    "Prompt",
    "User",
    "Host",
    "HostingDate",
    "db",
]


class ApiKey(db.Model):
    __tablename__ = "api_keys"
    __table_args__ = {
        "comment": "API keys for accessing protected API endpoints. By default, keys can only access public, unprotected endpoints and actions. Authorization can be granted on a granular level for complete control over key permissions."
    }

    _id = Column(TINYINT(3), primary_key=True)
    key = Column("token", String(64, "utf8mb4_unicode_ci"), nullable=False, unique=True)
    date_created = Column(DateTime, nullable=False, default=datetime.now)
    desc = Column(String(256, "utf8mb4_unicode_ci"))
    has_api_key = Column(Boolean, nullable=False, default=False)
    has_archive = Column(Boolean, nullable=False, default=False)
    has_broadcast = Column(Boolean, nullable=False, default=False)
    has_host = Column(Boolean, nullable=False, default=False)
    has_prompt = Column(Boolean, nullable=False, default=False)
    has_settings = Column(Boolean, nullable=False, default=False)
    has_subscription = Column(Boolean, nullable=False, default=False)

    @classmethod
    def delete(cls, key: str) -> None:
        db.session.delete(cls.query.filter_by(key=key).first())
        db.session.commit()
        return None

    @classmethod
    def exists(cls, key: str) -> bool:
        """Determine if an API key exists."""
        return cls.query.filter_by(key=key).first() is not None


class Email(db.Model):
    __tablename__ = "emails"

    email = Column(String(150, "utf8mb4_unicode_ci"), primary_key=True, unique=True)
    date_added = Column(DateTime, server_default=text("current_timestamp()"))


class User(db.Model):
    __tablename__ = "users"

    id = Column(INTEGER(11), primary_key=True)
    username = Column(String(20, "utf8mb4_unicode_ci"), nullable=False, unique=True)
    password = Column(String(128, "utf8mb4_unicode_ci"), nullable=False)
    date_created = Column(
        DateTime, nullable=False, server_default=text("current_timestamp()")
    )
    last_signin = Column(DateTime)


class Host(db.Model):
    __tablename__ = "writers"

    uid = Column(String(30, "utf8mb4_unicode_ci"), primary_key=True, unique=True)
    handle = Column(String(20, "utf8mb4_unicode_ci"), nullable=False)


class ApiKeyAudit(db.Model):
    __tablename__ = "audit_api_keys"
    __table_args__ = {"comment": "Audit table to track permission changes to API keys."}

    _id = Column(TINYINT(3), primary_key=True)
    key_id = Column(
        ForeignKey("api_keys._id", ondelete="CASCADE"), nullable=False, index=True
    )
    date_updated = Column(
        DateTime, nullable=False, server_default=text("current_timestamp()")
    )
    has_api_key = Column(Boolean, nullable=False, default=False)
    has_archive = Column(Boolean, nullable=False, default=False)
    has_broadcast = Column(Boolean, nullable=False, default=False)
    has_host = Column(Boolean, nullable=False, default=False)
    has_prompt = Column(Boolean, nullable=False, default=False)
    has_settings = Column(Boolean, nullable=False, default=False)
    has_subscription = Column(Boolean, nullable=False, default=False)

    key = relationship("ApiKey")


class Prompt(db.Model):
    __tablename__ = "prompts"

    tweet_id = Column(String(25, "utf8mb4_unicode_ci"), primary_key=True, unique=True)
    date = Column(Date, nullable=False)
    uid = Column(
        ForeignKey("writers.uid", onupdate="CASCADE"), nullable=False, index=True
    )
    content = Column(String(2048, "utf8mb4_unicode_ci"), nullable=False)
    word = Column(String(30, "utf8mb4_unicode_ci"), nullable=False)
    media = Column(String(512, "utf8mb4_unicode_ci"))
    media_alt_text = Column(String(1000, "utf8mb4_unicode_ci"))
    date_added = Column(
        DateTime,
        nullable=False,
        server_default=text("current_timestamp() ON UPDATE current_timestamp()"),
    )

    host = relationship("Host")


class HostingDate(db.Model):
    __tablename__ = "writer_dates"

    uid = Column(
        ForeignKey("writers.uid", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    date = Column(Date, primary_key=True, nullable=False)

    host = relationship("Host")


trigger_api_key_permission_changes = DDL(
    """CREATE TRIGGER IF NOT EXISTS `api_key_permission_changes` AFTER UPDATE ON `api_keys`
    FOR EACH ROW BEGIN
    INSERT INTO audit_api_keys(
        key_id,
        has_api_key,
        has_archive,
        has_broadcast,
        has_host,
        has_prompt,
        has_settings,
        has_subscription
    )
    VALUES (
        old._id,
        old.has_api_key,
        old.has_archive,
        old.has_broadcast,
        old.has_host,
        old.has_prompt,
        old.has_settings,
        old.has_subscription
    );
    END;"""
)
event.listen(ApiKey, "after_update", trigger_api_key_permission_changes)

ALL_TRIGGERS = (trigger_api_key_permission_changes,)
