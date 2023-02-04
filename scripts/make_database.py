import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect


# We have to add the app path to the path to get the db
APP_ROOT = Path(__file__).parent.parent
sys.path.insert(0, APP_ROOT.as_posix())


from db.dummy_db import create_app
from src.core.database import models


def create_database():
    """Create a brand new copy of the database."""
    app = create_app()
    with app.app_context():
        # Create the database tables if needed
        if not bool(inspect(models.db.engine).get_table_names()):
            print("Creating new database...")
            models.db.create_all()

            # Tell Alembic this is a new database and
            # we don't need to update it to a newer schema
            alembic_cfg = Config("alembic.ini")
            command.stamp(alembic_cfg, "head")


if __name__ == "__main__":
    create_database()
