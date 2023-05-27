"""Rename PromptMedia.media

Revision ID: f862f100f6fb
Revises: e03e08dd379c
Create Date: 2023-05-19 21:43:18.260997

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "f862f100f6fb"
down_revision = "e03e08dd379c"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint("prompt_media_ibfk_1", "prompt_media", type_="foreignkey")
    op.alter_column(
        "prompt_media",
        "media",
        new_column_name="file",
        existing_nullable=True,
        existing_type=sa.types.String(512, collation="utf8mb4_unicode_ci"),
    )
    op.create_foreign_key(
        None,
        "prompt_media",
        "prompts_new",
        ["prompt_id"],
        ["_id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(None, "prompt_media", type_="foreignkey")
    op.alter_column(
        "prompt_media",
        "file",
        new_column_name="media",
        existing_nullable=True,
        existing_type=sa.types.String(512, collation="utf8mb4_unicode_ci"),
    )
    op.create_foreign_key(
        "prompt_media_ibfk_1",
        "prompt_media",
        "prompts_new",
        ["prompt_id"],
        ["_id"],
        onupdate="CASCADE",
    )
