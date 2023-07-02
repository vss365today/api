"""Remove old v1 tables

Revision ID: ed1da33697ff
Revises: f862f100f6fb
Create Date: 2023-07-02 17:45:57.300445

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "ed1da33697ff"
down_revision = "f862f100f6fb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("writer_dates")
    op.drop_table("prompts")
    op.drop_table("writers")


def downgrade() -> None:
    op.create_table(
        "prompts",
        sa.Column("tweet_id", mysql.VARCHAR(length=25), nullable=False),
        sa.Column("date", sa.DATE(), nullable=False),
        sa.Column("uid", mysql.VARCHAR(length=30), nullable=False),
        sa.Column("content", mysql.VARCHAR(length=2048), nullable=False),
        sa.Column("word", mysql.VARCHAR(length=30), nullable=False),
        sa.Column("media", mysql.VARCHAR(length=512), nullable=True),
        sa.Column("media_alt_text", mysql.VARCHAR(length=1000), nullable=True),
        sa.Column(
            "date_added",
            mysql.DATETIME(),
            server_default=sa.text("current_timestamp() ON UPDATE current_timestamp()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["uid"], ["writers.uid"], name="writer_uid-prompts_uid", onupdate="CASCADE"
        ),
        sa.PrimaryKeyConstraint("tweet_id"),
        comment="Legacy table for storing prompts.",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_comment="Legacy table for storing prompts.",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index("tweet_id", "prompts", ["tweet_id"], unique=False)
    op.create_index("ix_prompts_uid", "prompts", ["uid"], unique=False)
    op.create_table(
        "writers",
        sa.Column("uid", mysql.VARCHAR(length=30), nullable=False),
        sa.Column("handle", mysql.VARCHAR(length=20), nullable=False),
        sa.PrimaryKeyConstraint("uid"),
        mysql_collate="utf8mb4_unicode_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
    op.create_index("uid", "writers", ["uid"], unique=False)
    op.create_table(
        "writer_dates",
        sa.Column("uid", mysql.VARCHAR(length=30), nullable=False),
        sa.Column("date", sa.DATE(), nullable=False),
        sa.ForeignKeyConstraint(
            ["uid"],
            ["writers.uid"],
            name="writer_uid-writer_dates_uid",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("uid", "date"),
        mysql_collate="utf8mb4_unicode_ci",
        mysql_default_charset="utf8mb4",
        mysql_engine="InnoDB",
    )
