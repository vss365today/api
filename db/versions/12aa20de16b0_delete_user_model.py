"""Delete User model

Revision ID: 12aa20de16b0
Revises: 03a61012d6f9
Create Date: 2023-02-03 11:24:13.166901

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "12aa20de16b0"
down_revision = "03a61012d6f9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("username", table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column(
            "id", mysql.INTEGER(display_width=11), autoincrement=True, nullable=False
        ),
        sa.Column(
            "username",
            mysql.VARCHAR(charset="utf8mb4", collation="utf8mb4_unicode_ci", length=20),
            nullable=False,
        ),
        sa.Column(
            "password",
            mysql.VARCHAR(
                charset="utf8mb4", collation="utf8mb4_unicode_ci", length=128
            ),
            nullable=False,
        ),
        sa.Column("date_created", mysql.DATETIME(), nullable=False),
        sa.Column("last_signin", mysql.DATETIME(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_collate="latin1_swedish_ci",
        mysql_default_charset="latin1",
        mysql_engine="InnoDB",
    )
    op.create_index("username", "users", ["username"], unique=False)
    # ### end Alembic commands ###
