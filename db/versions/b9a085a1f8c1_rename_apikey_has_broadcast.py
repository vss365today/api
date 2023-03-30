"""Rename ApiKey.has_broadcast

Revision ID: b9a085a1f8c1
Revises: c36c16d680a6
Create Date: 2023-03-29 23:07:13.049777

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "b9a085a1f8c1"
down_revision = "c36c16d680a6"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "api_keys",
        "has_broadcast",
        new_column_name="has_notifications",
        existing_nullable=False,
        existing_server_default="0",
        existing_type=sa.types.Boolean,
    )


def downgrade():
    op.alter_column(
        "api_keys",
        "has_notifications",
        new_column_name="has_broadcast",
        existing_nullable=False,
        existing_server_default="0",
        existing_type=sa.types.Boolean,
    )
