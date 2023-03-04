"""Rename `APIKey.has_api_key`

Revision ID: f97b33a8b909
Revises: cf379e9a2dc4
Create Date: 2023-03-04 11:57:38.955462

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "f97b33a8b909"
down_revision = "cf379e9a2dc4"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "api_keys",
        "has_api_key",
        new_column_name="has_keys",
        existing_nullable=False,
        existing_server_default="0",
        existing_type=sa.types.Boolean,
    )


def downgrade():
    op.alter_column(
        "api_keys",
        "has_keys",
        new_column_name="has_api_key",
        existing_nullable=False,
        existing_server_default="0",
        existing_type=sa.types.Boolean,
    )
