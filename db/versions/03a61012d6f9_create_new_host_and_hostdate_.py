"""Create new Host and HostDate models

Revision ID: 03a61012d6f9
Revises:
Create Date: 2023-02-03 11:22:39.359292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "03a61012d6f9"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "hosts",
        sa.Column("_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "handle",
            sa.String(length=30, collation="utf8mb4_unicode_ci"),
            nullable=False,
        ),
        sa.Column(
            "twitter_uid",
            sa.String(length=40, collation="utf8mb4_unicode_ci"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("_id"),
        sa.UniqueConstraint("handle"),
        sa.UniqueConstraint("twitter_uid"),
        comment="Store the #vss365 Hosts.",
    )
    op.create_table(
        "host_dates",
        sa.Column("_id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("host_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["host_id"], ["hosts._id"], onupdate="CASCADE", ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("_id"),
        comment="Store the hosting dates of #vss365 Hosts.",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("host_dates")
    op.drop_table("hosts")
    # ### end Alembic commands ###
