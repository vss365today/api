"""Rename prompts table

Revision ID: fd1efe346516
Revises: ed1da33697ff
Create Date: 2023-07-02 17:48:50.170211

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "fd1efe346516"
down_revision = "ed1da33697ff"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("prompts_new", "prompts")


def downgrade() -> None:
    op.rename_table("prompts", "prompts_new")
