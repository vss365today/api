"""More ApiKey adjustments

Revision ID: e03e08dd379c
Revises: b9a085a1f8c1
Create Date: 2023-05-05 18:29:03.376134

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = "e03e08dd379c"
down_revision = "b9a085a1f8c1"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("api_keys", "has_settings")
    op.drop_column("audit_api_keys", "has_settings")
    op.drop_constraint("host_dates_ibfk_1", "host_dates", type_="foreignkey")
    op.create_foreign_key(
        None,
        "host_dates",
        "hosts",
        ["host_id"],
        ["_id"],
        onupdate="CASCADE",
        ondelete="CASCADE",
    )


def downgrade():
    op.drop_constraint(None, "host_dates", type_="foreignkey")
    op.create_foreign_key(
        "host_dates_ibfk_1",
        "host_dates",
        "hosts",
        ["host_id"],
        ["_id"],
        onupdate="CASCADE",
    )
    op.add_column(
        "audit_api_keys",
        sa.Column(
            "has_settings",
            mysql.TINYINT(display_width=1),
            server_default=sa.text("0"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "api_keys",
        sa.Column(
            "has_settings",
            mysql.TINYINT(display_width=1, unsigned=True),
            server_default=sa.text("0"),
            autoincrement=False,
            nullable=False,
        ),
    )
