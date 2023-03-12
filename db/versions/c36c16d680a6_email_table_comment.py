"""Add comment to Email table.

Revision ID: c36c16d680a6
Revises: f97b33a8b909
Create Date: 2023-03-12 19:27:19.399391

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "c36c16d680a6"
down_revision = "f97b33a8b909"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table_comment(
        "emails",
        "Store email addresses for those who want Prompt notifications.",
        existing_comment=None,
        schema=None,
    )


def downgrade():
    op.drop_table_comment(
        "emails",
        existing_comment="Store email addresses for those who want Prompt notifications.",
        schema=None,
    )
